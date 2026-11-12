import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


from rag.crag_llama_pipeline import CRAGLlamaPipeline

query = "Investigate CVE-2026-41473 and identify its vulnerability details, affected component, and security implications."
pipeline = CRAGLlamaPipeline()

try:
    result = pipeline.run(query)

    print("\n========== CIF PIPELINE RESULT ==========")
    print("Pipeline status:", result.get("status"))
    print("Evidence status:", result.get("evidence_status"))

    print("\n========== RETRIEVAL ==========")
    retrieval = result.get("retrieval", {})
    print("Retrieval mode:", retrieval.get("retrieval_mode"))
    print("Semantic evidence count:", retrieval.get("semantic_evidence_count"))
    print("Grading:", retrieval.get("grading"))

    print("\n========== ADAPTIVE RETRIEVAL ==========")
    adaptive = result.get("adaptive_retrieval", {})
    print("Attempts:", len(adaptive.get("attempts", [])))
    print("Final decision:", adaptive.get("final_decision"))

    if result.get("answer"):
        print("\n========== GENERATED ANSWER ==========")
        print(result["answer"])
    
    print("\n========== CLAIM VERIFICATION ==========")
    print(result.get("claim_verification", []))

    print("\n========== MULTI-AGENT CONSENSUS ==========")

    agents = result.get("multi_agent_verification", {})

    for name, agent in agents.items():
        print("\nAgent:", name)
        print("Status:", agent.get("status"))
        print("Full result:", agent)

    print("\n========== CONSISTENCY AGENT DETAILS ==========")
    print(agents.get("consistency_agent", {}))

    print("\n========== REASONING STAGES ==========")
    print("Beliefs:", len(result.get("beliefs", [])))
    print("Hypotheses:", len(result.get("hypotheses", [])))
    print("Simulation:", result.get("simulation", {}).get("final_state", {}))
    print("Hypothesis evaluations:", result.get("hypothesis_evaluations", []))

    print("\n========== FINAL DECISION ==========")
    print(result.get("decision", {}))
    

except Exception:
    import traceback
    traceback.print_exc()

finally:
    pipeline.close()
