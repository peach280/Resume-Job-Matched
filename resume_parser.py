from pypdf import PdfReader
from llm_client import extract_structured_profile
def extract_resume_text(uploaded_file):
    """Receives an uploaded file and extracts its text"""
    pdf = PdfReader(uploaded_file)
    text=[]
    for page in pdf.pages:
        text.append(page.extract_text() or "")
    return "\n".join(text)

def parse_resume(raw_text):
    llm_content= extract_structured_profile(raw_text)
    if(llm_content is not None):
        return llm_content
    else:
        return {
            "profile_text": raw_text,
            "skills":[],
            "preferred_roles":[],
            "experience_level":"fresher"
        }