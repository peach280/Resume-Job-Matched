from sentence_transformers import SentenceTransformer

print("Loading embedding model (all-MiniLM-L6-v2)...")

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


def generate_embedding(text: str) -> list:
    """
    Converts text into a 384-dimensional embedding.
    """
    return model.encode(text).tolist()