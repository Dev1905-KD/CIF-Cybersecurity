#!/usr/bin/env python3
"""Evaluate CIF predictions against manually labelled JSONL ground truth."""
import argparse
import json
import math
import statistics
import re
from collections import defaultdict
from pathlib import Path

LABELS = ("Supported", "Partially Supported", "Unsupported")


def norm(value):
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def as_list(value):
    return value if isinstance(value, list) else []


def get_path(obj, *path, default=None):
    cur = obj
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur.get(key)
    return cur


def evidence_key(item):
    if not isinstance(item, dict):
        return norm(item)
    explicit = item.get("evidence_id") or item.get("id") or item.get("reference")
    if explicit:
        return norm(explicit)
    source = norm(item.get("source"))
    claim = norm(item.get("claim") or item.get("description") or item.get("text"))
    return f"{source}|{claim}" if source or claim else ""


def collect_retrieved_evidence(result):
    """Collect only evidence records actually present in the saved response."""
    retrieval = result.get("retrieval", {}) if isinstance(result, dict) else {}
    adaptive = result.get("adaptive_retrieval", {}) if isinstance(result, dict) else {}
    candidates = []
    graph_evidence = as_list(get_path(retrieval, "graph_retrieval", "context", "evidence", default=[]))
    candidates.extend(graph_evidence)
    # Include semantic lists only when actual records are serialized in output.
    for path in (("semantic_evidence",), ("retrieved_evidence",), ("evidence",),
                 ("retrieval_result", "semantic_evidence"),
                 ("retrieval_result", "retrieved_evidence")):
        value = get_path(retrieval, *path, default=[])
        candidates.extend(as_list(value))
    candidates.extend(as_list(get_path(adaptive, "retrieval_result", "evidence", default=[])))
    ranked, seen = [], set()
    for item in candidates:
        key = evidence_key(item)
        if key and key not in seen:
            seen.add(key)
            ranked.append(key)
    return ranked, len(graph_evidence)


def retrieval_metrics(ranked, relevant, k):
    relevant = {norm(x) for x in relevant if norm(x)}
    if not relevant:
        return None
    top = ranked[:k]
    hits = [1 if item in relevant else 0 for item in top]
    # Standard Precision@K denominator remains K, even if fewer than K items returned.
    precision = sum(hits) / k
    recall = sum(hits) / len(relevant)
    mrr = next((1.0 / i for i, hit in enumerate(hits, 1) if hit), 0.0)
    dcg = sum(hit / math.log2(i + 1) for i, hit in enumerate(hits, 1))
    ideal = min(len(relevant), k)
    idcg = sum(1.0 / math.log2(i + 1) for i in range(1, ideal + 1))
    return {"precision": precision, "recall": recall, "mrr": mrr,
            "ndcg": dcg / idcg if idcg else 0.0}


def get_claim_predictions(result):
    claims = as_list(result.get("claim_verification")) if isinstance(result, dict) else []
    if not claims:
        claims = as_list(get_path(result, "multi_agent_verification", "evidence_agent", "claims", default=[]))
    return {norm(c.get("claim")): c.get("status") for c in claims
            if isinstance(c, dict) and c.get("claim")}


def classification_metrics(pairs):
    if not pairs:
        return None
    out, f1s = {}, []
    for label in LABELS:
        tp = sum(y == label and p == label for y, p in pairs)
        fp = sum(y != label and p == label for y, p in pairs)
        fn = sum(y == label and p != label for y, p in pairs)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        support = sum(y == label for y, _ in pairs)
        out[label] = {"precision": precision, "recall": recall, "f1": f1, "support": support}
        f1s.append(f1)
    out["overall"] = {
        "accuracy": sum(y == p for y, p in pairs) / len(pairs),
        "macro_f1": sum(f1s) / len(f1s),
        "evaluated_claims": len(pairs),
        "note": "Macro-F1 includes all three configured labels, including labels with zero support."
    }
    return out


def evaluate(predictions, ground_truth, k):
    gt_by_query = {norm(x.get("query")): x for x in ground_truth}
    retrieval_rows, claim_pairs, belief_rows, latencies = [], [], [], []
    skipped, claim_match_details, per_query = defaultdict(int), [], []
    for record in predictions:
        query = norm(record.get("query"))
        result = record.get("result", {})
        gold = gt_by_query.get(query)
        if not gold:
            skipped["no_ground_truth_for_query"] += 1
            continue
        ranked, graph_count = collect_retrieved_evidence(result)
        relevant = gold.get("relevant_evidence", [])
        row = {"query": record.get("query"), "ranked_evidence_records_saved": len(ranked),
               "graph_evidence_records_saved": graph_count}
        if relevant and ranked:
            m = retrieval_metrics(ranked, relevant, k)
            if m:
                retrieval_rows.append(m)
                row[f"retrieval_at_{k}"] = m
        elif relevant:
            skipped["retrieval_not_measurable_missing_ranked_evidence"] += 1
        else:
            skipped["retrieval_not_measurable_missing_relevant_evidence_labels"] += 1

        predicted_claims = get_claim_predictions(result)
        matched_here = 0
        for item in as_list(gold.get("claim_labels")):
            if not isinstance(item, dict):
                continue
            claim, expected = norm(item.get("claim")), item.get("status")
            predicted = predicted_claims.get(claim)
            if expected in LABELS and predicted in LABELS:
                claim_pairs.append((expected, predicted))
                matched_here += 1
                claim_match_details.append({"query": record.get("query"), "expected_claim": item.get("claim"),
                                            "expected_status": expected, "predicted_status": predicted,
                                            "match": "exact"})
            else:
                skipped["claim_label_pair_missing_or_unmatched"] += 1
                claim_match_details.append({"query": record.get("query"), "expected_claim": item.get("claim"),
                                            "expected_status": expected, "predicted_status": predicted,
                                            "match": "unmatched"})
        row["claim_labels_matched"] = matched_here

        expected_belief = gold.get("expected_belief_status")
        beliefs = as_list(result.get("beliefs"))
        predicted_belief = beliefs[0].get("status") if beliefs and isinstance(beliefs[0], dict) else None
        if expected_belief:
            if predicted_belief is not None:
                belief_rows.append(predicted_belief == expected_belief)
                row["belief_status_match"] = predicted_belief == expected_belief
            else:
                skipped["belief_status_missing"] += 1
        per_query.append(row)
        latency = record.get("latency_ms")
        if isinstance(latency, (int, float)) and latency >= 0:
            latencies.append(float(latency))

    mean = lambda rows, key: statistics.mean(x[key] for x in rows) if rows else None
    semantic_candidates = []
    for rec in predictions:
        result = rec.get("result", {})
        retrieval = result.get("retrieval", {}) if isinstance(result, dict) else {}
        adaptive = result.get("adaptive_retrieval", {}) if isinstance(result, dict) else {}
        count = get_path(retrieval, "grading", "semantic_candidate_count")
        if count is None:
            count = get_path(adaptive, "grading", "semantic_candidate_count")
        if count is None:
            count = get_path(adaptive, "retrieval_result", "grading", "semantic_candidate_count")
        if isinstance(count, (int, float)):
            semantic_candidates.append(count)
    report = {
        "queries_with_ground_truth": len(gt_by_query),
        "queries_evaluated": len(retrieval_rows),
        f"retrieval_at_{k}": {"precision": mean(retrieval_rows, "precision"),
                              "recall": mean(retrieval_rows, "recall"),
                              "mrr": mean(retrieval_rows, "mrr"),
                              "ndcg": mean(retrieval_rows, "ndcg"),
                              "evaluated_queries": len(retrieval_rows)},
        "retrieval_coverage": {
            "semantic_candidates_reported": sum(semantic_candidates) if semantic_candidates else None,
            "ranked_semantic_records_saved": False,
            "scope": "Only serialized evidence records are scored. Current sample exposes graph evidence but reports semantic candidate counts without the individual ranked semantic records.",
            "warning": "Do not describe these retrieval scores as full hybrid-vector ranking scores until ranked semantic evidence records are included in predictions.jsonl."
        },
        "claim_verification": classification_metrics(claim_pairs),
        "claim_match_details": claim_match_details,
        "belief_revision": {"status_accuracy": sum(belief_rows) / len(belief_rows) if belief_rows else None,
                            "evaluated_beliefs": len(belief_rows),
                            "note": "Exact status match against independently assigned expected_belief_status; not a directional belief-revision metric."},
        "latency_ms": {"mean": statistics.mean(latencies) if latencies else None,
                       "median": statistics.median(latencies) if latencies else None,
                       "p95": sorted(latencies)[max(0, math.ceil(.95 * len(latencies)) - 1)] if latencies else None,
                       "measured_queries": len(latencies)},
        "per_query": per_query,
        "skipped_or_unmeasurable": dict(skipped),
        "interpretation": ["Claim labels are matched to exact generated claim text.",
                           "Retrieval metrics score only evidence records actually serialized in predictions.",
                           "Missing metrics are reported as null, never as zero.",
                           "A single query is a smoke test, not a research-grade benchmark."]
    }
    return report


def load_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8-sig") as f:
        for line_no, line in enumerate(f, 1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}, line {line_no}: {exc}") from exc
    return rows


def main():
    parser = argparse.ArgumentParser(description="Evaluate CIF predictions against labelled ground truth.")
    parser.add_argument("--predictions", default="evaluation/predictions.jsonl")
    parser.add_argument("--dataset", default="evaluation/ground_truth.jsonl")
    parser.add_argument("--output", default="evaluation/report.json")
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()
    predictions, ground_truth = load_jsonl(args.predictions), load_jsonl(args.dataset)
    report = evaluate(predictions, ground_truth, args.k)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nSaved evaluation report to: {output}")


if __name__ == "__main__":
    main()
