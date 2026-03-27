from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExamCatalogItem:
    exam_code: str
    exam_name: str
    provider: str
    levels: list[str] = field(default_factory=list)
    syllabus_sources: list[dict[str, str]] = field(default_factory=list)
    previous_paper_sources: list[dict[str, str]] = field(default_factory=list)
    pattern_sources: list[dict[str, str]] = field(default_factory=list)
    answer_key_sources: list[dict[str, str]] = field(default_factory=list)


EXAM_CATALOG: list[ExamCatalogItem] = [
    ExamCatalogItem(
        exam_code="TNTET",
        exam_name="Tamil Nadu Teacher Eligibility Test",
        provider="Tamil Nadu Teachers Recruitment Board (TRB)",
        levels=["Paper I (Classes 1-5)", "Paper II (Classes 6-8)"],
        syllabus_sources=[
            {"title": "TRB official portal", "url": "https://www.trb.tn.gov.in/"},
            {"title": "TRB latest notifications", "url": "https://www.trb.tn.gov.in/index.php"},
        ],
        previous_paper_sources=[
            {"title": "TRB question paper resources", "url": "https://www.trb.tn.gov.in/"},
        ],
        pattern_sources=[
            {"title": "TRB TNTET exam notifications", "url": "https://www.trb.tn.gov.in/"},
        ],
        answer_key_sources=[
            {"title": "TRB answer key announcements", "url": "https://www.trb.tn.gov.in/"},
        ],
    ),
    ExamCatalogItem(
        exam_code="TNPSC",
        exam_name="Tamil Nadu Public Service Commission Exams",
        provider="Tamil Nadu Public Service Commission (TNPSC)",
        levels=["Group I", "Group II/IIA", "Group IV", "Departmental Exams"],
        syllabus_sources=[
            {"title": "TNPSC official portal", "url": "https://www.tnpsc.gov.in/"},
            {"title": "TNPSC syllabus page", "url": "https://www.tnpsc.gov.in/English/syllabus.html"},
        ],
        previous_paper_sources=[
            {"title": "TNPSC previous question papers", "url": "https://www.tnpsc.gov.in/English/previous-questions.html"},
        ],
        pattern_sources=[
            {"title": "TNPSC scheme of examination", "url": "https://www.tnpsc.gov.in/english/scheme.html"},
        ],
        answer_key_sources=[
            {"title": "TNPSC answer key / results section", "url": "https://www.tnpsc.gov.in/English/results.aspx"},
        ],
    ),
    ExamCatalogItem(
        exam_code="GATE",
        exam_name="Graduate Aptitude Test in Engineering",
        provider="IIT System (rotating organizing institute)",
        levels=["All engineering branches in active cycle papers"],
        syllabus_sources=[
            {"title": "GATE 2025 official portal", "url": "https://gate2025.iitr.ac.in/"},
            {"title": "GATE 2025 information brochure", "url": "https://gate2025.iitr.ac.in/doc/download/GATE2025_InformationBrochure.pdf"},
            {"title": "GATE archive (IIT Kanpur 2023)", "url": "https://gate.iitk.ac.in/GATE2023/gate_syllabus.html"},
        ],
        previous_paper_sources=[
            {"title": "GATE previous year papers", "url": "https://gate.iitk.ac.in/GATE2023/download_info.html"},
            {"title": "GATE paper/keys hub", "url": "https://gate.iitk.ac.in/GATE2023/papers_keys.html"},
        ],
        pattern_sources=[
            {"title": "GATE mock test gateway", "url": "https://gate.iitk.ac.in/GATE2023/mock.html"},
        ],
        answer_key_sources=[
            {"title": "GATE master keys", "url": "https://gate.iitk.ac.in/GATE2023/papers_keys.html"},
        ],
    ),
    ExamCatalogItem(
        exam_code="NCEES_FE_PE",
        exam_name="NCEES FE and PE Exams",
        provider="NCEES",
        levels=["FE disciplines", "PE disciplines"],
        syllabus_sources=[
            {"title": "FE exam overview", "url": "https://ncees.org/exams/fe-exam/"},
            {"title": "PE exam overview", "url": "https://ncees.org/exams/pe-exam/"},
            {"title": "FE Other Disciplines specs PDF", "url": "https://ncees.org/wp-content/uploads/FE-Other-CBT-specs.pdf"},
        ],
        previous_paper_sources=[
            {"title": "NCEES exam prep and practice", "url": "https://account.ncees.org/exam-prep/"},
        ],
        pattern_sources=[
            {"title": "NCEES examinee guide", "url": "https://ncees.org/exams/examinee-guide/"},
        ],
        answer_key_sources=[
            {"title": "NCEES scoring and diagnostics", "url": "https://ncees.org/exams/"},
        ],
    ),
    ExamCatalogItem(
        exam_code="PMP",
        exam_name="Project Management Professional",
        provider="PMI",
        levels=["PMP Certification Exam"],
        syllabus_sources=[
            {"title": "PMP certification page", "url": "https://www.pmi.org/certifications/project-management-pmp"},
            {"title": "PMP exam content outline PDF", "url": "https://www.pmi.org/-/media/pmi/documents/public/pdf/certifications/pmp-examination-content-outline-english.pdf"},
        ],
        previous_paper_sources=[
            {"title": "PMI authorized prep resources", "url": "https://www.pmi.org/shop/p-/elearning/pmi-authorized-online-pmp-practice-exam/el086"},
        ],
        pattern_sources=[
            {"title": "PMP exam updates", "url": "https://www.pmi.org/certifications/project-management-pmp/new-exam"},
        ],
        answer_key_sources=[
            {"title": "PMI scoring policy", "url": "https://www.pmi.org/certifications/project-management-pmp"},
        ],
    ),
]


def as_dict() -> list[dict[str, Any]]:
    return [
        {
            "exam_code": item.exam_code,
            "exam_name": item.exam_name,
            "provider": item.provider,
            "levels": item.levels,
            "syllabus_sources": item.syllabus_sources,
            "previous_paper_sources": item.previous_paper_sources,
            "pattern_sources": item.pattern_sources,
            "answer_key_sources": item.answer_key_sources,
        }
        for item in EXAM_CATALOG
    ]
