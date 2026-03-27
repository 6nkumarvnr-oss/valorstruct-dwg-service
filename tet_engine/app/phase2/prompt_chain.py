from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI

SYSTEM_PROMPT = """
You are an expert competitive-exam question-setter.
Generate grounded MCQs only from provided source chunks.
Rules:
1) Stay within syllabus topic and exam context.
2) Return strictly valid JSON.
3) Each MCQ must have exactly 4 options A/B/C/D and one correct option.
4) Include concise explanation and source_chunk_ids used.
5) Avoid duplicates and ambiguous options.
""".strip()

USER_TEMPLATE = """
Exam: {exam_code}
Paper: {paper_name}
Subject: {subject_name}
Topic: {topic_name}
Difficulty: {difficulty}
Language: {language}
Requested Count: {count}

Source chunks:
{source_chunks}

Return JSON with shape:
{{
  "questions": [
    {{
      "question_text": "...",
      "options": [{{"label":"A","text":"..."}}, {{"label":"B","text":"..."}}, {{"label":"C","text":"..."}}, {{"label":"D","text":"..."}}],
      "correct_option": "A",
      "explanation": "...",
      "source_chunk_ids": [1, 2]
    }}
  ]
}}
""".strip()


def generate_grounded_mcqs(*, exam_code: str, paper_name: str, subject_name: str, topic_name: str, difficulty: str, language: str, count: int, source_chunks: list[dict[str, Any]]) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY", "")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    if not api_key:
        return {
            "questions": [
                {
                    "question_text": f"Fallback MCQ for {topic_name} (set OPENAI_API_KEY for live generation)",
                    "options": [
                        {"label": "A", "text": "Option A"},
                        {"label": "B", "text": "Option B"},
                        {"label": "C", "text": "Option C"},
                        {"label": "D", "text": "Option D"},
                    ],
                    "correct_option": "A",
                    "explanation": "Fallback explanation.",
                    "source_chunk_ids": [chunk.get("id") for chunk in source_chunks[:2]],
                }
            ]
        }

    client = OpenAI(api_key=api_key)
    user_prompt = USER_TEMPLATE.format(
        exam_code=exam_code,
        paper_name=paper_name,
        subject_name=subject_name,
        topic_name=topic_name,
        difficulty=difficulty,
        language=language,
        count=count,
        source_chunks=json.dumps(source_chunks, ensure_ascii=False),
    )

    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )

    text = response.output_text
    parsed = json.loads(text)
    if "questions" not in parsed:
        raise ValueError("Model response missing 'questions' key")
    return parsed
