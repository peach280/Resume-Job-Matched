from db import supabase

SENIOR_KEYWORDS = [
    "senior",
    "sr.",
    "staff",
    "principal",
    "lead",
    "iii",
    "architect",
    "manager",
]


def is_senior_role(title: str) -> bool:
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in SENIOR_KEYWORDS)


def get_matching_jobs(
    profile_embedding: list, match_threshold: float = 0.4, match_count: int = 10
):
    """
    Finds jobs whose embeddings are similar to the
    user's profile embedding.
    """

    response = supabase.rpc(
        "match_jobs",
        {
            "query_embedding": profile_embedding,
            "match_threshold": match_threshold,
            "match_count": match_count,
        },
    ).execute()

    return response.data


def get_user_matching_jobs(email, match_threshold=0.4, match_count=10):
    response = (
        supabase.table("users")
        .select("profile_embedding,experience_level")
        .eq("email", email)
        .single()
        .execute()
    )

    if not response.data:
        raise ValueError(f"No profile found for {email}")

    profile_embedding = response.data["profile_embedding"]
    experience_level = response.data.get("experience_level")

    raw_pool_size = match_count * 3

    jobs = get_matching_jobs(
        profile_embedding=profile_embedding,
        match_threshold=match_threshold,
        match_count=raw_pool_size,
    )
    print(f"Raw pool size before filter: {len(jobs)}")
    if experience_level == "fresher":
        jobs = [job for job in jobs if not is_senior_role(job["title"])]
        print(f"Pool size after senior-role filter: {len(jobs)}")

    return jobs[:match_count]
