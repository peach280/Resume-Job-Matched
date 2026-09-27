from db import supabase
from profiles import get_users
from matching import get_user_matching_jobs


def filter_already_sent_jobs(user_id, jobs):
    sent_jobs = (
        supabase
        .table("user_jobs_delivered")
        .select("job_id")
        .eq("user_id", user_id)
        .execute()
    )
    sent_job_ids = {row["job_id"] for row in sent_jobs.data}
    filtered_jobs = [job for job in jobs if job["id"] not in sent_job_ids]
    return filtered_jobs


def send_job_email(email: str, jobs: list):
    """
    Placeholder for the email service.
    We will connect this to an actual email provider
    after the matching pipeline is verified.
    """
    print(f"\nPreparing email for {email}...")

    if not jobs:
        print("No matching jobs found.")
        return

    print(f"Found {len(jobs)} matching jobs:")

    for job in jobs:
        print(
            f"\n{job['title']}"
            f"\nCompany: {job['company']}"
            f"\nLocation: {job['location']}"
            f"\nSimilarity: {job['similarity']:.3f}"
            f"\nApply: {job['application_url']}"
        )


def record_delivery(user_id, job_ids):
    rows = [{"user_id": user_id, "job_id": job_id} for job_id in job_ids]
    supabase.table("user_jobs_delivered").insert(rows).execute()


def run_send_matches():
    users = get_users()
    for user in users:
        user_id = user["id"]
        email = user["email"]

        matched_jobs = get_user_matching_jobs(
            email=email,
            match_threshold=0.5,
            match_count=10
        )

        new_jobs = filter_already_sent_jobs(user_id, matched_jobs)

        if new_jobs:
            send_job_email(email=email, jobs=new_jobs)
            job_ids = [job["id"] for job in new_jobs]
            record_delivery(user_id, job_ids)


if __name__ == "__main__":
    run_send_matches()
