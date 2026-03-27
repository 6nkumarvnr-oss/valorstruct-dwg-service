from __future__ import annotations

import json
from pathlib import Path

WEIGHTS = {
    "syllabus_alignment": 0.15,
    "answer_key_correctness": 0.20,
    "explanation_quality": 0.10,
    "duplicate_control": 0.08,
    "difficulty_calibration": 0.08,
    "source_grounding": 0.10,
    "review_workflow": 0.07,
    "publish_audit_controls": 0.07,
    "api_readiness": 0.05,
    "cost_efficiency": 0.05,
    "latency": 0.03,
    "security_compliance": 0.02,
}


def compute_score(metrics: dict[str, float]) -> float:
    total = 0.0
    for key, weight in WEIGHTS.items():
        total += metrics.get(key, 0.0) * weight
    return round(total, 4)


def main() -> None:
    sample_path = Path("tools/sample_engines.json")
    engines = json.loads(sample_path.read_text())

    ranked = []
    for item in engines:
        score = compute_score(item.get("metrics", {}))
        ranked.append({"engine": item["engine"], "score": score})

    ranked.sort(key=lambda row: row["score"], reverse=True)

    print("Engine Ranking")
    for index, row in enumerate(ranked, start=1):
        print(f"{index}. {row['engine']} -> {row['score']}")


if __name__ == "__main__":
    main()
