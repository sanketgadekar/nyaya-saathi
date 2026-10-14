import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ],
        temperature=temperature,
        max_tokens=2000
    )
    return response.choices[0].message.content