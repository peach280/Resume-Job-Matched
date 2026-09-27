from db import supabase


def get_matching_jobs(
    profile_embedding: list,
    match_threshold: float = 0.5,
    match_count: int = 10
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
            "match_count": match_count
        }
    ).execute()

    return response.data


def get_user_matching_jobs(
    email: str,
    match_threshold: float = 0.5,
    match_count: int = 10
):
    """
    Gets a user's stored profile embedding and finds
    matching jobs.
    """

    response = (
        supabase
        .table("users")
        .select("profile_embedding")
        .eq("email", email)
        .single()
        .execute()
    )

    if not response.data:
        raise ValueError(
            f"No profile found for {email}"
        )

    profile_embedding = response.data[
        "profile_embedding"
    ]

    return get_matching_jobs(
        profile_embedding=profile_embedding,
        match_threshold=match_threshold,
        match_count=match_count
    )