from ingestion import run_job_ingestion
from profiles import create_or_update_profile
from matching import get_user_matching_jobs
from emailer import send_job_email


def main():

    # ==========================================
    # STEP 1
    # Ingest jobs
    # ==========================================

    print("\n==============================")
    print("STEP 1: JOB INGESTION")
    print("==============================")

    run_job_ingestion()


    # ==========================================
    # STEP 2
    # Create/update user profile
    # ==========================================

    print("\n==============================")
    print("STEP 2: USER PROFILE")
    print("==============================")

    email = "test@example.com"

    resume_text = """
    Computer Science graduate with experience
    building web applications using React,
    Python, Flask and SQL.
    """

    skills = [
        "Python",
        "C++",
        "JavaScript",
        "React",
        "Flask",
        "SQL",
        "Git",
        "Docker"
    ]

    preferred_roles = [
        "Software Engineer",
        "Backend Engineer",
        "Full Stack Developer"
    ]

    preferred_locations = [
        "India",
        "Remote"
    ]

    create_or_update_profile(
        email=email,
        resume_text=resume_text,
        skills=skills,
        preferred_roles=preferred_roles,
        preferred_locations=preferred_locations
    )


    # ==========================================
    # STEP 3
    # Find matching jobs
    # ==========================================

    print("\n==============================")
    print("STEP 3: JOB MATCHING")
    print("==============================")

    jobs = get_user_matching_jobs(
        email=email,
        match_threshold=0.5,
        match_count=10
    )


    # ==========================================
    # STEP 4
    # Email results
    # ==========================================

    print("\n==============================")
    print("STEP 4: EMAIL")
    print("==============================")

    send_job_email(
        email=email,
        jobs=jobs
    )


if __name__ == "__main__":
    main()