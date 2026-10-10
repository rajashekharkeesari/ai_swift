"""Load visa policy records from JSON and format them into LangChain Documents."""

import json
import os
import warnings

from langchain_community.document_loaders import JSONLoader
from langchain_core.documents import Document

from src.Embeddings import create_vector_store

warnings.filterwarnings("ignore", category=DeprecationWarning)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "Data", "visaType.json")


def format_documents(raw_docs):
    """Convert raw JSON documents into structured LangChain Documents."""
    processed_docs = []
    for doc in raw_docs:
        visa = json.loads(doc.page_content)
        official_resource = visa.get("official_resource")

        text_content = f"""Country: {visa.get('country')}
Visa Type: {visa.get('visa_type')}

Eligibility Requirements:
- Age: {visa.get('age_min')} to {visa.get('age_max')} years
- Education: {visa.get('education_requirement')}
- Admission Letter: {visa.get('admission_letter')}
- Job Offer: {visa.get('job_offer')}
- Employer Sponsorship: {visa.get('employer_sponsorship')}

Language Requirements:
- English Proficiency: {visa.get('english_proficiency')}
- Accepted Exams: {', '.join(visa.get('accepted_exams', []))}
- Language: {visa.get('language_requirement')}

Financial Requirements:
- Financial Proof: {visa.get('financial_proof')}
- Salary Threshold: {visa.get('salary_threshold')}

Work & Study:
- Work Allowed: {visa.get('work_allowed')}
- Post Study Work: {visa.get('post_study_work')}

Additional Info:
- Medical Exam: {visa.get('medical_exam')}
- Insurance: {visa.get('insurance_required')}
- Visa Duration: {visa.get('visa_duration')}
- PR Path: {visa.get('pr_path')}
- Points System: {visa.get('points_system')}

Remarks: {visa.get('remarks')}
Official Resource: {official_resource}"""

        processed_docs.append(
            Document(
                page_content=text_content,
                metadata={
                    "country": visa.get("country"),
                    "visa_type": visa.get("visa_type"),
                    "source": "visaType.json",
                    "official_resource": official_resource,
                },
            )
        )

    return processed_docs


def build_vector_store():
    """Load the visa dataset, format it, and build (or load) the FAISS vector store."""
    loader = JSONLoader(file_path=DATA_PATH, jq_schema=".[]", text_content=False)
    raw_docs = loader.load()
    docs = format_documents(raw_docs)
    return create_vector_store(docs)
