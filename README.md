# TraceBench

A CLI that boosts large language model (LLM) adoption confidence by exploring why an LLM answer may have not passes retrieval expectations, using a simple system of pass, fail or overlap.

TraceBench is built for corpora (local docs + embeddings) with strong containment boundaries. It does not browse the web.
If the answer is not supported by retrieved context, prompt responds accordingly.


## What it does

Given:
- a question
- retrieved chunks (with similarity scores + sources)
- an optional model answer

TraceBench outputs:
- PASS/FAIL verdict
- failure classification (retrieval gap, policy violation, unsupported answer, etc.)
- likely cause (2–5 bullets)
- corrective levers (2–5 bullets)
- evidence (source + chunk id + excerpt)

## Why

Most demos show “RAG works”.
Real systems fail.

TraceBench is a diagnoser:
- When retrieval is empty
- When retrieval is weak
- When an answer is unsupported
- When a model should have refused
- When chunking / k / thresholds are the real cause

## Classifiers (v1)

- RETRIEVAL_EMPTY
- RETRIEVAL_LOW_CONFIDENCE
- RETRIEVAL_HAS_ANSWER_BUT_NOT_USED
- ANSWER_UNSUPPORTED
- ANSWER_CONTRADICTS_CONTEXT
- ANSWER_INCOMPLETE
- PROMPT_POLICY_VIOLATION
- OK_NOT_FOUND_COMPLIANT
- OK_SUPPORTED

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

```text
## Usage

1) Analyze retrieval-only (no model call)
```bash
python TraceBench/run.py \
  --question "What happens if the answer is missing?" \
  --retrieval_json sample_runs/retrieval.json \
  --answer_txt sample_runs/answer.txt

```text
## Output example
```bash
VERDICT: FAIL
TYPE: PROMPT_POLICY_VIOLATION

CAUSE
- Retrieval confidence is low (top1=0.61)
- No chunk contains required query terms (overlap<2)
- Model answered anyway

FIXES
- Enforce rules when evidence is missing
- Raise minimum similarity threshold OR increase k
- Add refusal template and answer gate

EVIDENCE
- docs/sample.md#chunk_6 (score=0.61): 

## Design principles
	•	Rules > vibes
	•	Receipts > persuasion
	•	Cheap heuristics that are easy to tune
	•	Boundary-setting-first (no web browsing)

## Roadmap (future extensions)
	•	Add “k/threshold sweep” mode
	•	Add golden test set + CI
	•	Add JSON output for dashboards
