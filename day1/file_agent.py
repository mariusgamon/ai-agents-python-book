# file_agent.py
import config  # loads .env and validates the key

from agents import Agent, Runner, function_tool
import asyncio

# Load file content once at startup — not inside the tool
with open("data/notes.txt", "r", encoding="utf-8") as f:
    FILE_CONTENT = f.read()

@function_tool
def read_notes() -> str:
    """Returns the content of the meeting notes."""
    return FILE_CONTENT

agent = Agent(
    name="NotesAssistant",
    model=config.DEFAULT_MODEL,
    instructions="""You are an assistant that answers questions about meeting notes.
    Use the read_notes() tool to access the content.
    Answer directly and precisely.""",
    tools=[read_notes],
)

async def main():
    questions = [
        "What is the marketing budget?",
        "Who is the priority client contact?",
        "What is the deadline for API v2?",
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        result = await Runner.run(agent, input=question)
        print(f"Answer: {result.final_output}")

asyncio.run(main())
