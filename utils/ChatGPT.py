from typing import List

import openai
from dotenv import dotenv_values


async def call_chatgpt(prompt: List[dict], model="gpt-4o-mini") -> dict:

    config = dotenv_values('.env')
    client = openai.OpenAI(api_key=config["OPENAI_SECRET"])
    try:
        competion = client.chat.completions.create(
            model=model,
            messages=prompt,
            temperature=0.4,
        )
    except Exception as e:
        return {
            "response": None,
            "error": str(e)
        }
    result = competion.choices[0].message.content
    return {
        "response": result,
        "error": False
    }