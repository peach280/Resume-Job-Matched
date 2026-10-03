from fastapi import FastAPI, UploadFile, File, Form
from resume_parser import extract_resume_text,parse_resume
from profiles import create_or_update_profile
from db import supabase
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://resume-job-matched.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/health")
def health():
    return {"status": "ok"}
@app.post("/upload-resume")
def upload_resume(
    email: str = Form(...),
    file: UploadFile = File(...)
):
    raw_text = extract_resume_text(file.file)
    profile_data = parse_resume(raw_text)
    print(profile_data)
    create_or_update_profile(
        email=email,
        resume_text=profile_data["profile_text"],
        skills=profile_data["skills"],
        preferred_roles=profile_data["preferred_roles"],
        experience_level=profile_data["experience_level"]
    )
    print(f"Received file: {file.filename}, email: {email}")
    return {"status": "received", "filename": file.filename}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)