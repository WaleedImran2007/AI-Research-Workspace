from groq import Groq
import os

from langchain_core.documents import Document

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def transcribe_audio(audio_path: str):

    with open(audio_path, "rb") as audio_file:

        transcription = client.audio.transcriptions.create(
            file = audio_file,
            model = "whisper-large-v3-turbo",
            response_format = "verbose_json",
            timestamp_granularities=["segment"],
            temperature = 0,
        )

    return transcription

def create_audio_chunks(transcription, chunk_size=1000):
    segments = transcription.segments

    documents = []

    current_text = ""
    current_start = None

    for segment in segments:
        text = segment["text"].strip()

        if not text:
            continue

        if current_start is None:
            current_start = segment["start"]

        current_text += " " + text

        if len(current_text) >= chunk_size:
            documents.append(Document(
                page_content=current_text.strip(),
                metadata={
                    "startTime": current_start,
                    "documentType": "audio,"
                }
            ))

            current_text = ""
            current_start = None

    # Remaining Text
    if current_text.strip():
        documents.append(
            Document(
                page_content=current_text.strip(),
                metadata={
                    "startTime": current_start,
                    "documentType": "audio",
                }
            )
        )

    return documents