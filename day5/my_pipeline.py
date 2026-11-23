# my_pipeline.py — the “code that calls Runner.run()” tested by tests/test_pipeline.py
# (companion-repo file: the book only shows the test)
import config
from agents import Agent, Runner

FALLBACK_MESSAGE = "Sorry, I couldn't generate an answer. Please try again in a moment."

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant. Answer concisely.",
    model=config.DEFAULT_MODEL,
)


async def process_request(user_input: str) -> dict:
    result = await Runner.run(agent, input=user_input, max_turns=5)
    output = (result.final_output or "").strip()

    # Silent agent: return a fallback message rather than an empty answer
    if not output:
        return {"status": "empty_response", "fallback_used": True, "output": FALLBACK_MESSAGE}
    return {"status": "ok", "fallback_used": False, "output": output}
