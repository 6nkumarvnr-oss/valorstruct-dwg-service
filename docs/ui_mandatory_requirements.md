# Question Bank Engine UI - Mandatory Modules

This checklist is the **minimum UI** required to run the Question Bank Engine in production.

## 1) Authentication & Roles (mandatory)
- Admin login
- Admin-Admin (Super Admin) login
- Content reviewer login
- Super-admin permissions
- Audit trail for every create/update/publish action

## 2) Exam Setup Console (mandatory)
- Create exam (TNTET, TNPSC, GATE, NCEES FE/PE, PMP)
- Create course, paper, subject, topic hierarchy
- Version control for syllabus per exam cycle/year

## 3) Source Ingestion UI (mandatory)
- Upload PDF books/syllabus/question papers
- Track upload status (queued, parsed, chunked, failed)
- Source metadata fields: exam, subject, year, source type, copyright flag
- Link source to syllabus topic

## 4) Question Generation UI (mandatory)
- Select exam/paper/subject/topic
- Select difficulty and number of questions
- Select language
- Trigger `generate-grounded`
- Show retrieved source chunks used for grounding

## 5) Review & Approval Workflow (mandatory)
- Draft list table
- Inline edit for question/options/explanation
- Mark correct option
- Approve/reject buttons
- Bulk actions (approve/reject)
- Reviewer comments and flags

## 6) Answer Key & Quality Controls (mandatory)
- Auto-generated key preview
- Confidence score display
- Duplicate detector warning
- Ambiguity warning
- Mandatory human review for high-stakes exams before publish

## 7) Publishing UI (mandatory)
- Publish to target app course/test bank
- Schedule publish/unpublish
- Rollback published batch
- Track published version number
- Notepad/text publish report download

## 8) Student-Facing UI (mandatory)
- Topic-wise practice
- Sectional tests
- Mock tests
- Instant answer + explanation
- Review incorrect attempts

## 9) Analytics Dashboard (mandatory)
- Accuracy by topic
- Difficulty-wise performance
- Weak-topic recommendation panel
- Question quality feedback from users

## 10) Ops & Monitoring (mandatory)
- Generation job logs
- API error logs
- Failed ingestion queue
- Key/secret status checks
- Data backup status

## Recommended first UI release order
1. Auth + Exam Setup
2. Source Ingestion
3. Generate + Review
4. Publish
5. Student practice screens
6. Analytics
