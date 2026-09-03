import os
import base64

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

vision_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


async def analyze_image(
    image_bytes: bytes,
    content_type: str,
    query: str,
):
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    completion = vision_client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
                            Answer the user's question about the image.

                            User question:
                            {query}

                            Give only the final answer.
                            Do not include reasoning, analysis, or <think> tags.
                        """,
                    },
                    
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{content_type};base64,{image_base64}",
                            "detail": "auto",
                        },
                    },
                ],
            }
        ],

        temperature=0.7,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )

    answer = completion.choices[0].message.content or ""

    print("RAW IMAGE RESPONSE:")
    print(answer)

    if "</think>" in answer:
        answer = answer.split("</think>", 1)[1].strip()

    print("FINAL IMAGE ANSWER:")
    print(answer)

    return answer