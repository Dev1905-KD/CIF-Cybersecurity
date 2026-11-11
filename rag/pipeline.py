from rag.query_processor import process_query
from rag.corrective_retriever import CorrectiveRetriever
from rag.vector_retriever import VectorRetriever
from rag.context_builder import build_context
from rag.grader import grade_retrieval


class CRAGPipeline:

    def __init__(self):
        self.retriever = CorrectiveRetriever()
        self.vector_retriever = VectorRetriever()

    def run(self, query):
        processed = process_query(query)
        cve = processed.get("cve")

        graph_result = None
        if cve:
            graph_result = self.retriever.retrieve(cve)

        semantic_evidence = self.vector_retriever.retrieve(
            query,
            top_k=8
        )

        merged = {
            "cve": cve,
            "description": "",
            "products": [],
            "evidence": [],
            "connections": [],
            "semantic_evidence": semantic_evidence
        }

        if graph_result and graph_result.get("context"):
            graph_context = graph_result["context"]
            merged["description"] = graph_context.get("description") or ""
            merged["products"] = graph_context.get("products") or []
            merged["evidence"] = graph_context.get("evidence") or []
            merged["connections"] = graph_context.get("connections") or []

        # Make semantic results visible to the existing evidence grader.
        for item in semantic_evidence:
            merged["evidence"].append({
                "source": item.get("source") or "Unknown",
                "type": item.get("evidence_type") or "",
                "claim": item.get("claim") or "",
                "date_added": item.get("date_added") or "",
                "similarity": item.get("similarity")
            })

        grading = grade_retrieval(merged)
        context = build_context(merged)

        return {
            "status": "success",
            "query": query,
            "cve": cve,
            "context": context,
            "grading": grading,
            "correction_used": bool(
                graph_result and graph_result.get("correction_used")
            ),
            "retrieval_mode": "hybrid_vector_and_graph",
            "semantic_evidence_count": len(semantic_evidence),
            "graph_retrieval": graph_result
        }

    def close(self):
        self.retriever.close()
        self.vector_retriever.close()
