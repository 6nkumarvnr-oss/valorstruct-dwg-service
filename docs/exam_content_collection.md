# Multi-Exam Content Collection Plan (as of March 24, 2026)

This document defines what to collect for:
- Tamil Nadu TET (Paper I/II for Classes 1-8)
- TNPSC exams
- GATE (all engineering branches in current cycle)
- NCEES FE/PE
- PMP

## 1) Required artifacts per exam
For each exam, collect and version these objects:
1. Official syllabus / exam content outline (PDF/HTML)
2. Previous question papers (official archives)
3. Exam pattern (marks, duration, section split, question type)
4. Official answer keys or scoring policy

## 2) Catalog source
Use `GET /v2/catalog/exams` to retrieve the curated source list for each exam provider.

## 3) Storage design
- Save source files in object storage (`gs://...` or local upload path).
- Store metadata in `source_documents`.
- Store extracted chunks in `source_chunks`.
- Store generated questions and answer keys in `generated_questions`.

## 4) Answer key policy
- If official answer key exists: attach source key reference.
- If no public key exists (e.g., PMP/NCEES): store explanation + confidence and flag `needs_human_review=true`.
- Never publish unreviewed generated answer keys for high-stakes exams.

## 5) Copyright/legal caution
Many exam bodies restrict redistribution of full papers.
Use only legally permitted sources and preserve source URL + access date.

## 6) Update cadence
- Weekly: check active exam portals (TNTET/TNPSC/GATE cycle pages).
- Monthly: check FE/PE/PMP content updates.
- On notification release: immediately ingest new syllabus/notice PDFs.
