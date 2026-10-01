import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from db import supabase
from profiles import get_users
from matching import get_user_matching_jobs


def filter_already_sent_jobs(user_id, jobs):
    sent_jobs = (
        supabase.table("user_jobs_delivered")
        .select("job_id")
        .eq("user_id", user_id)
        .execute()
    )
    sent_job_ids = {row["job_id"] for row in sent_jobs.data}
    filtered_jobs = [job for job in jobs if job["id"] not in sent_job_ids]
    return filtered_jobs


def get_smtp_connection():
    email_address = os.environ.get("EMAIL_ADDRESS")
    email_password = os.environ.get("EMAIL_APP_PASSWORD")

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email_address, email_password)
    return server


def send_job_email(smtp_server, email: str, jobs: list):
    if not jobs:
        print(f"No matching jobs for {email}, skipping.")
        return

    sender = os.environ.get("EMAIL_ADDRESS")

    body_lines = []
    for job in jobs:
        body_lines.append(
            f"{job['title']}\n"
            f"Company: {job['company']}\n"
            f"Location: {job['location']}\n"
            f"Apply: {job['application_url']}\n"
        )
    body = "\n\n".join(body_lines)

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = email
    msg["Subject"] = f"{len(jobs)} new job matches for you"
    msg.attach(MIMEText(body, "plain"))

    smtp_server.sendmail(sender, email, msg.as_string())
    print(f"Email sent to {email} with {len(jobs)} jobs.")


def record_delivery(user_id, job_ids):
    rows = [{"user_id": user_id, "job_id": job_id} for job_id in job_ids]
    supabase.table("user_jobs_delivered").insert(rows).execute()


def run_send_matches():
    users = get_users()
    smtp_server = get_smtp_connection()

    try:
        for user in users:
            user_id = user["id"]
            email = user["email"]

            try:
                matched_jobs = get_user_matching_jobs(
                    email=email, match_threshold=0.4, match_count=10
                )

            except Exception as e:
                print(f"Failed to get matches for {email}: {e}")
                continue

            new_jobs = filter_already_sent_jobs(user_id, matched_jobs)

            if new_jobs:
                send_job_email(smtp_server, email, new_jobs)
                job_ids = [job["id"] for job in new_jobs]
                record_delivery(user_id, job_ids)
    finally:
        smtp_server.quit()


if __name__ == "__main__":
    run_send_matches()
