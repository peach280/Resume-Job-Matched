import requests
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime, timezone, timedelta

from db import supabase
from embeddings import generate_embedding


def fetch_public_job_listings(keyword: str, location: str):
    """
    Fetches publicly available job listings for a keyword/location
    and keeps only jobs posted today.
    """

    print(f"Scraping public job listings " f"for '{keyword}' in '{location}'...")

    base_url = (
        "https://www.linkedin.com/jobs-guest/" "jobs/api/seeMoreJobPostings/search"
    )

    params = {
        "keywords": keyword,
        "location": location,
        "start": 0,
        "f_TPR": "r432000"
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    formatted_jobs = []

    try:
        # Convert params dictionary into URL query string
        query_string = urllib.parse.urlencode(params)

        target_url = f"{base_url}?{query_string}"

        response = requests.get(target_url, headers=headers, timeout=10)

        if response.status_code in (999, 429):
            print("Rate-limited or blocked by target host.")
            return []

        response.raise_for_status()

        # Parse returned HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Find job cards
        job_cards = soup.find_all("li")

        print(f"Found {len(job_cards)} <li> elements.")
        

        for card in job_cards:
            # Find title
            title_tag = card.find("h3", class_="base-search-card__title")

            # Find company
            company_tag = card.find("h4", class_="base-search-card__subtitle")

            # Find location
            location_tag = card.find("span", class_="job-search-card__location")

            # Find application link
            anchor_tag = card.find("a", class_="base-card__full-link")

            # Find posting date
            date_tag = card.find("time", class_="job-search-card__listdate")

            # We need title, URL and date
            if not title_tag or not anchor_tag or not date_tag:
                continue

            # --------------------------------
            # CHECK POSTING DATE
            # --------------------------------

            posted_date_string = date_tag.get("datetime")

            if not posted_date_string:
                continue

            print(
                f"Job: {title_tag.get_text(strip=True)} | "
                f"Raw date: {date_tag.get_text(strip=True)} | "
                f"Datetime: {posted_date_string}"
            )

            cutoff_date = datetime.now(timezone.utc).date() - timedelta(days=5)
            try:
                posted_date = datetime.strptime(posted_date_string, "%Y-%m-%d").date()

            except ValueError:
                continue

            # Ignore jobs that weren't posted today
            if posted_date < cutoff_date:
                continue

            # --------------------------------
            # EXTRACT JOB INFORMATION
            # --------------------------------

            title = title_tag.get_text(strip=True)

            company = (
                company_tag.get_text(strip=True) if company_tag else "Confidential"
            )

            loc = location_tag.get_text(strip=True) if location_tag else "Unknown"

            app_url = anchor_tag.get("href", "").split("?")[0]

            if title and app_url:

                formatted_jobs.append(
                    {
                        "title": title,
                        "company": company,
                        "location": loc,
                        "description": (
                            f"{title} role at " f"{company} located in {loc}."
                        ),
                        "application_url": app_url,
                    }
                )

        print(
            f"Successfully scraped "
            f"{len(formatted_jobs)} listings "
            f"posted today for {location}."
        )

        return formatted_jobs

    except Exception as e:

        print(f"Scraping exception encountered: {e}")

        return []


def run_job_ingestion():

    search_queries = [
        # India
        {"keyword": "Software Engineer", "location": "India"},
        {"keyword": "Software Developer", "location": "India"},
        {"keyword": "Developer", "location": "India"},
        # Remote
        {"keyword": "Software Engineer", "location": "Remote"},
        {"keyword": "Software Developer", "location": "Remote"},
        {"keyword": "Developer", "location": "Remote"},
    ]

    all_raw_jobs = []

    for query in search_queries:

        jobs = fetch_public_job_listings(query["keyword"], query["location"])

        all_raw_jobs.extend(jobs)

    print("==========================================")
    print(f"Total raw jobs collected: " f"{len(all_raw_jobs)}")
    print("*****************************************")

    if not all_raw_jobs:

        print("No jobs found.")

        return

    job_payloads = []

    seen_urls = set()

    for job in all_raw_jobs:

        url = job["application_url"]

        # Prevent duplicate jobs
        if url in seen_urls:
            continue

        seen_urls.add(url)

        # --------------------------------
        # CREATE TEXT FOR EMBEDDING
        # --------------------------------

        combined_text = (
            f"{job['title']} at "
            f"{job['company']} "
            f"({job['location']}): "
            f"{job['description']}"
        )

        # Generate 384-dimensional embedding
        embedding_vector = generate_embedding(combined_text)

        job_payloads.append(
            {
                "title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "description": job["description"],
                "application_url": url,
                "embedding": embedding_vector,
            }
        )

    # --------------------------------
    # SAVE TO SUPABASE
    # --------------------------------

    try:

        response = (
            supabase.table("jobs")
            .upsert(job_payloads, on_conflict="application_url")
            .execute()
        )

        print(f"Successfully upserted " f"{len(job_payloads)} jobs.")

        return response.data

    except Exception as e:

        print(f"Database bulk insert error: {e}")

        return []


if __name__ == "__main__":
    run_job_ingestion()
