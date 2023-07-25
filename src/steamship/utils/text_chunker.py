import logging


def chunk_text(text: str, chunk_size: int = 200, chunk_overlap: int = 50):
    """Chunk text for embedding and insertion into an embedding index."""
    if chunk_size < 1:
        logging.warning(f"chunk_size was f{chunk_size}. Setting to 200")
        chunk_size = 200

    if chunk_overlap < 0:
        logging.warning(f"chunk_overlap was f{chunk_overlap}. Setting to 0")
        chunk_overlap = 0

    if chunk_overlap > chunk_size:
        logging.warning(f"chunk_size was f{chunk_size}. Setting to chunk_size - 1 of {chunk_size}")
        chunk_overlap = chunk_size - 1 if chunk_size > 1 else 1

    step_size = chunk_size - chunk_overlap

    for i in range(0, len(text), step_size):
        yield text[i : i + chunk_size]
