# email_pipeline_simple.py — Plain Python version (what they should have done)
import config

from openai import AsyncOpenAI

client = AsyncOpenAI()

async def classify_intent(email_body: str) -> str:
    """Classifies the email: billing, technical, feature_request, or other."""
    response = await client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[
            {"role": "system", "content": "Classify this support email intent. "
             "Return exactly one of: billing, technical, feature_request, other."},
            {"role": "user", "content": email_body}
        ],
        max_tokens=20
    )
    return response.choices[0].message.content.strip()

async def draft_response(email_body: str, intent: str) -> str:
    """Generates a draft reply based on the email content and the classified intent."""
    response = await client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[
            {"role": "system", "content": f"Draft a professional response to this "
             f"{intent} support email. Be concise and helpful."},
            {"role": "user", "content": email_body}
        ],
        max_tokens=300
    )
    return response.choices[0].message.content

async def process_support_email(email_body: str) -> dict:
    """Full pipeline: classify, then draft. Two calls, zero framework."""
    intent = await classify_intent(email_body)
    draft = await draft_response(email_body, intent)
    return {"intent": intent, "draft": draft}
