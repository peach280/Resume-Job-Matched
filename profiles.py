from db import supabase
from embeddings import generate_embedding

def get_users():
    response=supabase.table("users").select("id","email").execute()
    return response.data
def create_profile_text(
    resume_text: str,
    skills: list[str],
    preferred_roles: list[str]
) -> str:
    """
    Combines user information into one text representation
    that can be converted into an embedding.
    """

    profile_text = f"""
Resume:
{resume_text}

Skills:
{", ".join(skills)}

Preffered Roles
{", ".join(preferred_roles)}
"""

    return profile_text.strip()


def create_or_update_profile(
    email: str,
    resume_text: str,
    skills: list[str],
    preferred_roles: list[str]
):
    """
    Creates or updates a user's profile and generates
    their profile embedding.
    """

    profile_text = create_profile_text(
        resume_text=resume_text,
        skills=skills,
        preferred_roles=preferred_roles
    )

    print(
        f"Generating profile embedding for {email}..."
    )

    profile_embedding = generate_embedding(
        profile_text
    )

    response = (
        supabase
        .table("users")
        .upsert(
            {
                "email": email,
                "profile_embedding": profile_embedding
            },
            on_conflict="email"
        )
        .execute()
    )

    print(
        f"Profile saved for {email}."
    )

    return response.data