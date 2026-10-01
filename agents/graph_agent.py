import re

from knowledge_graph.neo4j_connection import (
    Neo4jConnection
)


class GraphAgent:

    def __init__(self):

        self.connection = Neo4jConnection()

    def verify(
        self,
        answer
    ):

        cves = self._extract_cves(
            answer
        )

        results = []

        for cve in cves:

            exists = self._check_cve(
                cve
            )

            results.append({
                "cve": cve,
                "exists": exists
            })

        if not results:

            status = "No Graph Entities"

        elif all(
            item["exists"]
            for item in results
        ):

            status = "Supported"

        else:

            status = "Needs Review"

        return {
            "agent": "Graph Agent",
            "status": status,
            "entities_checked": len(results),
            "entities_found": sum(
                item["exists"]
                for item in results
            ),
            "entities": results
        }

    def _extract_cves(
        self,
        answer
    ):

        return list(
            set(
                re.findall(
                    r"CVE-\d{4}-\d{4,7}",
                    answer.upper()
                )
            )
        )

    def _check_cve(
        self,
        cve
    ):

        query = """
        MATCH (v:Vulnerability {id: $cve})
        RETURN v.id AS cve
        LIMIT 1
        """

        with self.connection.driver.session() as session:

            result = session.run(
                query,
                cve=cve
            )

            record = result.single()

            return record is not None

    def close(self):

        self.connection.close()