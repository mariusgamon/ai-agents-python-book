import httpx
import os
from dotenv import load_dotenv

load_dotenv()  # reads MISTRAL_API_KEY from .env

MISTRAL_API_KEY = os.environ["MISTRAL_API_KEY"]
MISTRAL_URL     = "https://api.mistral.ai/v1/chat/completions"


def llm(messages: list[dict], model: str = "mistral-small-latest") -> str:
    """
    Direct call to the Mistral API — no SDK, just HTTP.

    messages: list of dicts {"role": "user"|"assistant"|"system", "content": "..."}
    returns:  the text of the response (content of the first choice)
    """
    response = httpx.post(
        MISTRAL_URL,
        headers={
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type":  "application/json",
        },
        json={
            "model":       model,
            "messages":    messages,
            "temperature": 0.2,      # low, for reproducible decisions
        },
        timeout=30.0,
    )
    response.raise_for_status()     # raises an exception on 4xx / 5xx
    return response.json()["choices"][0]["message"]["content"]


def extract_json(text: str) -> str:
    """Removes the ```json ... ``` fences some models add around the JSON."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else ""   # removes the ```json line
        if t.rstrip().endswith("```"):
            t = t.rstrip()[:-3]
    return t.strip()


# Quick test
if __name__ == "__main__":
    reply = llm([{"role": "user", "content": "Say hello in one sentence."}])
    print(reply)


# Add at the end of mistral_raw.py: the §B.5 loop imports it from this module.
SYSTEM_PROMPT = """You are an intelligent assistant that can use tools.

When you need a tool to answer, reply ONLY with this JSON
(nothing else, no text before or after):

{"tool": "tool_name", "args": {"param1": "value1", ...}}

Available tools:
- get_weather(city: str)          → current weather for the city
- calculate(expression: str)      → Python-safe math calculation
- search_web_snippets(query: str, n: int) → n web snippets (DuckDuckGo, not a news API)

When you have the final answer without a tool, write it normally (no JSON).

IMPORTANT: never make up a tool's result. Always call it."""
