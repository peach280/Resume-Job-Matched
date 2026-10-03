# Resume → Job Matches

A $0, end-to-end pipeline that reads your resume, understands it, and emails you relevant software engineering roles — automatically, every day.

**Live app:** https://resume-job-matched.vercel.app

## The problem

Job boards show you everything, relevant or not. A fresher gets flooded with senior/staff postings; a senior engineer gets flooded with internships. This app reads your actual resume, classifies your experience level, and filters accordingly,so what lands in your inbox is worth your time.

## How it works

Four independent pipelines, each deployable and testable on its own:

Resume Upload (user-triggered)
PDF → text extraction → LLM structuring (skills, roles, experience level)
→ embedding → stored profile

Job Ingestion (scheduled, daily)
LinkedIn public search → HTML parsing → date filtering → dedup
→ embedding → stored job listings

Matching (scheduled, daily)
Stored profile embedding → pgvector similarity search
→ experience-level filter → new-jobs-only filter

Delivery (same scheduled run)
Filtered matches → email → delivery record (prevents re-sending)


## Stack

- **Frontend:** Angular, deployed on Vercel
- **Backend:** FastAPI, deployed on Render
- **Database:** Supabase (Postgres + pgvector)
- **Embeddings:** `fastembed` (ONNX runtime — chosen specifically to avoid PyTorch's memory footprint on free-tier hosting)
- **LLM extraction:** Groq, with automatic fallback to raw-text embedding if the API call fails
- **Scheduling:** GitHub Actions (ingestion and matching/delivery run as independent, scheduled jobs)
- **Email:** Gmail SMTP

## Engineering decisions

- **Graceful degradation, not hard failure.** If the LLM extraction call fails (rate limit, timeout, malformed response), the user still gets a usable profile built from raw resume text instead of structured fields rather than a failed upload. The rest of the pipeline never knows which path was taken; both return the same shape.
- **Composite primary key for delivery tracking.** `(user_id, job_id)` as a primary key on the delivery table makes duplicate-send protection a database guarantee, not just an application-level check — safe even under concurrent writes.
- **Filter before capping, not after.** Experience-level filtering happens against a wider candidate pool *before* truncating to the final result count filtering an already-truncated set could silently return zero results on a day when the top matches happen to skew senior.
- **Switched embedding libraries mid-deployment** after hitting a hard memory ceiling on free-tier hosting. PyTorch's default build includes CUDA/GPU libraries that serve no purpose on a GPU-less host. Moved to `fastembed` (ONNX-based, no PyTorch dependency) for the same model output at a fraction of the memory footprint.
- **Deliberately avoided a serverless backend deployment** despite the appeal of "no idle cost." This app loads an embedding model at startup and chains an LLM call plus database writes per request — serverless cold-start-per-invocation would hit model-reload overhead on every request and risked execution timeouts. A persistent server with a lightweight keep-alive ping was the better-fit trade-off.

## Known limitations (deliberately scoped out, not hidden)

- **No work-authorization/eligibility filtering.** Ingestion doesn't currently scrape full job descriptions, only title, company, location, and URL so citizenship or visa requirements buried in a job description aren't detected. This is the clear next milestone: full JD scraping would unlock better embeddings, reliable seniority detection, and eligibility filtering all at once.
- **Location matching is coarse.** Ingestion searches fixed buckets (India, Remote) rather than parsing granular location preferences from resumes.
- **Matches are delivered on a daily schedule, not instantly.** Expect your first email within 24 hours of uploading, not immediately.

## Running it locally

```bash
# backend
pip install -r requirements.txt
uvicorn app:app --reload

# frontend
cd resume-uploader
npm install
ng serve
```

Environment variables needed: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `GROQ_API_KEY`, `EMAIL_ADDRESS`, `EMAIL_APP_PASSWORD`.