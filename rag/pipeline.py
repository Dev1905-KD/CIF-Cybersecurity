from rag.query_processor import process_query
from rag.corrective_retriever import (
    CorrectiveRetriever
)
from rag.context_builder import build_context


class CRAGPipeline:

    def __init__(self):

        self.retriever = (
            CorrectiveRetriever()
        )

    def run(self, query):

        # Step 1: Understand query
        processed = process_query(
            query
        )

        cve = processed.get("cve")

        if not cve:

            return {
                "status": "error",
                "message":
                    "No CVE identifier detected."
            }

        # Step 2: Retrieve + correct
        result = self.retriever.retrieve(
            cve
        )

        # Step 3: Build context
        context = build_context(
            result["context"]
        )

        return {
            "query": query,
            "cve": cve,
            "context": context,
            "grading": result["grading"],
            "correction_used":
                result["correction_used"]
        }

    def close(self):
        self.retriever.close()