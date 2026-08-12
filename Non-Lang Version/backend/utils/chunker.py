CHUNK_SIZE = 1000
OVERLAP_SIZE = 200

def create_chunks(text):
    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        chunks.append(chunk)
        start += CHUNK_SIZE - OVERLAP_SIZE

    return chunks