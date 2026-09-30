from rag.graph_retriever import GraphRetriever
from rag.grader import grade_retrieval


class CorrectiveRetriever:

    def __init__(self):
        self.retriever = GraphRetriever()

    def retrieve(self, cve):

        context = self.retriever.retrieve_cve_context(
            cve
        )

        grading = grade_retrieval(
            context
        )

        # -------------------------
        # First retrieval
        # -------------------------

        if grading["status"] == "relevant":

            return {
                "context": context,
                "grading": grading,
                "correction_used": False
            }

        # -------------------------
        # Corrective retrieval
        # -------------------------

        if grading["status"] in {
            "weak",
            "irrelevant"
        }:

            corrected_context = (
                self.correct_retrieval(cve)
            )

            corrected_grading = grade_retrieval(
                corrected_context
            )

            return {
                "context": corrected_context,
                "grading": corrected_grading,
                "correction_used": True
            }

    def correct_retrieval(self, cve):

        # Broader graph search.
        # This is our first corrective strategy.

        query = """
        MATCH (v:Vulnerability)
        WHERE toLower(v.id) = toLower($cve)

        OPTIONAL MATCH (v)-[r]-(connected)

        RETURN
            v.id AS cve,
            v.description AS description,
            collect({
                relationship: type(r),
                entity: labels(connected),
                id: connected.id,
                name: connected.name,
                source: connected.source
            }) AS connections
        """

        with self.retriever.connection.driver.session() as session:

            result = session.run(
                query,
                cve=cve
            )

            record = result.single()

            if not record:
                return None

            return {
                "cve": record["cve"],
                "description": record["description"],
                "connections": record["connections"]
            }

    def close(self):
        self.retriever.close()