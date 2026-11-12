"""
Run CIF against evaluation queries and save complete outputs + latency.

Run from CIF repository root:
  python scripts/run_cif_evaluation.py --dataset evaluation/ground_truth.jsonl

This uses the existing CRAGLlamaPipeline and does not modify its reasoning logic.
"""

import argparse
import json
import time
from pathlib import Path
import sys

# Add CIF repository root to Python import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag.crag_llama_pipeline import CRAGLlamaPipeline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="evaluation/ground_truth.jsonl")
    parser.add_argument("--output", default="evaluation/predictions.jsonl")
    args = parser.parse_args()

    dataset = Path(args.dataset)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    cases = []
    with dataset.open("r", encoding="utf-8-sig") as f:
        for line_no, line in enumerate(f, 1):
            if line.strip():
                item = json.loads(line)
                if not item.get("query"):
                    raise ValueError(f"Missing query at line {line_no}")
                cases.append(item)

    pipeline = CRAGLlamaPipeline()
    try:
        with output.open("w", encoding="utf-8") as out:
            for index, case in enumerate(cases, 1):
                query = case["query"]
                print(f"[{index}/{len(cases)}] {query}")
                start = time.perf_counter()
                try:
                    result = pipeline.run(query)
                    latency_ms = (time.perf_counter() - start) * 1000
                    record = {"query": query, "result": result,
                              "latency_ms": round(latency_ms, 2)}
                    out.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
                    out.flush()
                    print(f"  completed in {latency_ms:.0f} ms")
                except Exception as exc:
                    latency_ms = (time.perf_counter() - start) * 1000
                    record = {"query": query, "error": f"{type(exc).__name__}: {exc}",
                              "latency_ms": round(latency_ms, 2)}
                    out.write(json.dumps(record, ensure_ascii=False) + "\n")
                    out.flush()
                    print(f"  FAILED: {record['error']}")
    finally:
        pipeline.close()

    print(f"\nSaved raw predictions to {output}")


if __name__ == "__main__":
    main()
