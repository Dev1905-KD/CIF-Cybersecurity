# CIF evaluation metrics starter

This provides a reproducible evaluation harness for the existing CIF pipeline.

## Metrics implemented

1. **Retrieval:** Precision@K, Recall@K, MRR@K, nDCG@K. Requires human-labelled relevant evidence keys.
2. **Claim verification:** per-class precision, recall, F1 and support for Supported / Partially Supported / Unsupported, plus accuracy and macro-F1. Requires human labels for generated claims.
3. **Belief revision:** exact belief-status accuracy against an independently assigned expected status. This is intentionally not called directional accuracy.
4. **Performance:** mean, median and p95 end-to-end query latency, measured by the runner.

The evaluator skips unmeasurable metrics rather than inventing zeros. The example dataset is a schema template, not a labelled benchmark: replace the placeholder labels and evidence keys with manually verified annotations before reporting results.

## Install / run

Run from the CIF repository root with the existing virtual environment activated.

```powershell
python scripts/run_cif_evaluation.py --dataset evaluation/ground_truth.jsonl
python scripts/evaluate_cif.py --predictions evaluation/predictions.jsonl --ground-truth evaluation/ground_truth.jsonl --k 5
```

Output: `evaluation/report.json`

The runner invokes `CRAGLlamaPipeline.run(query)` and closes the pipeline after the dataset. It does not edit your core pipeline files.

## Ground-truth format

Each line in `ground_truth.jsonl` is one JSON object:

- `query`: exact query sent to CIF.
- `relevant_evidence`: manually confirmed evidence keys. Key format is `source|claim` if the record has no explicit `evidence_id`, `id`, or `reference`; otherwise use that explicit identifier.
- `claim_labels`: exact claim text and human-assigned label. Labels must be `Supported`, `Partially Supported`, or `Unsupported`.
- `expected_belief_status`: independently adjudicated expected belief status, e.g. `needs_review`, `supported`, or `rejected`.

Do not label claims based only on CIF's own output. Verify against authoritative source material / the benchmark annotation protocol.

## Important limitations

- Your current CVE response's graph evidence record has `source` and `claim` but no explicit evidence ID. Therefore the retrieval evaluator uses `source|claim` as its key for that record.
- The current output may not expose ranked semantic candidate records, even though it reports semantic candidate counts. In that case semantic retrieval ranking cannot be evaluated from that output. The script will evaluate only the evidence records actually returned.
- This code does not compute ablation results. To compare graph-only, vector-only and hybrid retrieval, run each mode as a separate controlled experiment and record its mode and outputs. Do not infer ablation metrics from a single hybrid run.
- Belief status accuracy is only a simple exact-match measure. To evaluate belief revision direction, create a separate human-labelled expected transition (`previous_status`, `expected_new_status`) after defining a revision policy.
