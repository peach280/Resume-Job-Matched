import os
from groq import Groq,APIError
from dotenv import load_dotenv
import json

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
def extract_structured_profile(resume_text):
    """Extract structured info from resume_text organized into different sections based on user's experience"""
    prompt = f"""Extract structured information from the resume below.

Resume text:
{resume_text}

First, internally assess whether this candidate is a "fresher" (little to no
professional work experience, likely a recent graduate) or "experienced"
(has meaningful professional work experience). Do not include this
assessment in your output — use it only to decide how to write the summary:
- If fresher: emphasize projects, education, and relevant coursework in the summary.
- If experienced: emphasize professional work experience and achievements in the summary.

Return a JSON object with exactly these keys:
- "profile_text": a concise summary of the candidate's background, weighted
  as described above (string)
- "skills": list of technical skills mentioned (list of strings)
- "preferred_roles": likely job titles this person fits, based on their background (list of strings)

Return only the JSON object, no other text. Do not include an experience_level key.
"""
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        raw_output = response.choices[0].message.content
        parsed = json.loads(raw_output)
        return parsed
    except (APIError, json.JSONDecodeError) as e:
        print(f"LLM extraction failed: {e}")
        return None
        
    