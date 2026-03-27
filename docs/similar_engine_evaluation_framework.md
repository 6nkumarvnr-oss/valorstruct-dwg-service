# Evaluate similar AI question-bank engines for your app

Use this framework to compare your engine against similar AI systems used for exam-question generation.

## 1) What to compare
Score each engine on 0-5 for these dimensions:

1. **Syllabus alignment**
2. **Answer-key correctness**
3. **Explanation quality**
4. **Duplicate control**
5. **Difficulty calibration**
6. **Source grounding/traceability**
7. **Review workflow support**
8. **Publishing controls and audit report**
9. **API readiness/integration ease**
10. **Cost per 1,000 generated questions**
11. **Latency / generation speed**
12. **Security and compliance readiness**

## 2) Recommended weighted scoring
- correctness-heavy because this is exam content:
  - Answer-key correctness: 20%
  - Syllabus alignment: 15%
  - Explanation quality: 10%
  - Duplicate control: 8%
  - Difficulty calibration: 8%
  - Source grounding: 10%
  - Review workflow: 7%
  - Publish/audit controls: 7%
  - API readiness: 5%
  - Cost: 5%
  - Latency: 3%
  - Security/compliance: 2%

## 3) Evaluation method
1. Use the same syllabus and source set for all engines.
2. Generate same number of questions by topic and difficulty.
3. Blind-review quality by human reviewers.
4. Measure objective metrics:
   - key accuracy
   - duplicate ratio
   - out-of-syllabus ratio
   - average response time
   - estimated cost
5. Compute weighted score and rank engines.

## 4) Decision rule
- Pick the engine with highest weighted score **only if**:
  - answer-key correctness >= 95%
  - out-of-syllabus <= 3%
  - duplicate ratio <= 5%

If not, reject for production and iterate.

## 5) Output artifact
Publish a comparison report with:
- engine name/version
- benchmark dataset version
- metric table
- weighted final score
- go/no-go recommendation
