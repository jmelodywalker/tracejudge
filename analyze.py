import json
from typing import Any, Dict, List


def print_summary(report: Dict[str, Any]) -> None:
    run_id = report.get("run_id")
    verdict = report.get("verdict")
    flags = report.get("flags") or []
    scores = report.get("scores") or {}

    print("")
    print(f"run_id:  {run_id}")
    print(f"verdict: {verdict}")
    print(f"flags:   {', '.join(flags) if flags else '(none)'}")
    print("")
    print(f"top1_distance:  {scores.get('top1_distance')}")
    print(f"overlap_ratio:  {scores.get('overlap_ratio')}")
    print(f"answer_len:     {scores.get('answer_len')}")
    print("")


def analyze_run(run: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step B v0:
    - Heuristic 1: Missing Answer Detection (phrase-based, normalized)
    - Heuristic 2: Top-K Signal Strength (distance-based)
    - Heuristic 3: Support Overlap
    """

    query = (run.get("query") or "").strip()
    answer = (run.get("answer_text") or "").strip()
    sources: List[Dict[str, Any]] = run.get("sources") or []

    flags: List[str] = []
    scores: Dict[str, Any] = {}

    # -----------------------------
    # Heuristic 1: Missing answer detection
    # -----------------------------
    normalized = " ".join(answer.lower().strip().split())

    missing_phrases = [
        "not found in corpus",
        "not in corpus",
        "does not exist in corpus",
        "doesn't exist in corpus",
        "does not exist in the corpus",
        "doesn't exist in the corpus",
        "this information does not exist in corpus",
        "this information doesn't exist in corpus",
        "this information does not exist in the corpus",
        "this information doesn't exist in the corpus",
        "answer not found in corpus",
    ]

    phrase_hit = any(p in normalized for p in missing_phrases)

    is_missing = (normalized == "") or phrase_hit

    scores["missing_answer"] = is_missing
    scores["missing_phrase_hit"] = phrase_hit
    scores["answer_len"] = len(normalized)

    if is_missing:
        flags.append("MISSING_ANSWER")

    # -----------------------------
    # Heuristic 2: Top-1 retrieval strength
    # -----------------------------
    top1 = sources[0] if sources else None
    top1_score = (
        float(top1.get("score"))
        if top1 and top1.get("score") is not None
        else None
    )

    scores["top1_distance"] = top1_score

    WEAK_DISTANCE_THRESHOLD = 1.30

    if top1_score is None:
        flags.append("NO_RETRIEVAL")
    elif top1_score > WEAK_DISTANCE_THRESHOLD:
        flags.append("WEAK_RETRIEVAL")

    # -----------------------------
    # Heuristic 3: Support overlap
    # -----------------------------
    if top1 and answer:
        chunk_text = (top1.get("text") or "").lower()
        answer_words = set(normalized.split())
        chunk_words = set(chunk_text.split())

        overlap = answer_words.intersection(chunk_words)
        overlap_ratio = len(overlap) / max(len(answer_words), 1)

        scores["overlap_ratio"] = overlap_ratio

        if overlap_ratio < 0.2 and not is_missing:
            flags.append("UNSUPPORTED_ANSWER")
    else:
        scores["overlap_ratio"] = 0.0

    # -----------------------------
    # Verdict
    # -----------------------------
    if "NO_RETRIEVAL" in flags:
        verdict = "FAIL"

    elif "UNSUPPORTED_ANSWER" in flags:
        verdict = "FAIL"

    elif is_missing:
        verdict = "PASS"

    elif "WEAK_RETRIEVAL" in flags:
        verdict = "WARN"

    else:
        verdict = "PASS"

    return {
        "run_id": run.get("run_id"),
        "query": query,
        "answer_text": answer,
        "verdict": verdict,
        "flags": flags,
        "scores": scores,
    }


def main() -> None:
    import sys

    if len(sys.argv) != 2:
        print("Usage: python analyze.py sample_runs/run_0001.json")
        raise SystemExit(2)

    path = sys.argv[1]

    with open(path, "r", encoding="utf-8") as f:
        run = json.load(f)

    report = analyze_run(run)

    print_summary(report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()