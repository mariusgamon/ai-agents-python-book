# agent_with_memory.py
import config

from agents import Agent, Runner, function_tool
from memory_store import init_db, save_memory, get_memory
from memory_store import get_all_memories as fetch_all_memories
from memory_store import add_to_history, get_recent_history
import asyncio

USER_ID = "primary_user"  # ⚠ Demo only — NEVER hardcode in production.
# In a real service, get user_id from your auth layer (cookie, JWT, header) or the Runner context.
# Note: init_db() is async — we call it from main() below, not at import time.

@function_tool
async def memorize(key: str, value: str) -> str:
    """
    Stores a piece of information about the user for future sessions.

    Args:
        key: Identifier of the information (e.g., "preferred_language", "framework", "level")
        value: The information to remember
    """
    await save_memory(USER_ID, key, value)
    return f"Memorized: {key} = {value}"

@function_tool
async def recall(key: str) -> str:
    """
    Recalls a piece of information stored about the user.

    Args:
        key: The information to recall
    """
    value = await get_memory(USER_ID, key)
    if value:
        return f"{key}: {value}"
    return f"No stored information for '{key}'"

@function_tool
async def get_all_memories() -> str:
    """Returns all the information stored about the user."""
    memories = await fetch_all_memories(USER_ID)
    if not memories:
        return "No information stored yet."
    return "\n".join([f"- {k}: {v}" for k, v in memories.items()])

agent = Agent(
    name="PersonalAssistant",
    model=config.DEFAULT_MODEL,
    instructions="""You are a personal development assistant.
    
    You MUST memorize important information about the user when they mention it:
    - Their preferred language/framework
    - Their level (junior, senior, etc.)
    - Their current projects
    - Their preferences (code style, tools, etc.)
    
    At the start of each conversation, check what you already know via get_all_memories().
    Adapt your responses based on the stored profile.""",
    tools=[memorize, recall, get_all_memories],
)

async def main():
    # Initialize the DB at startup
    await init_db()

    # Fetch recent history (await is required: the function is async)
    history = await get_recent_history(USER_ID, limit=6)

    print("=== Session started ===\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in ["quit", "exit", "q"]:
            break

        messages = history + [{"role": "user", "content": question}]

        result = await Runner.run(
            agent,
            input=messages,
        )

        print(f"\nAgent: {result.final_output}\n")

        # Save to the persistent history (audit, role/content transcript).
        # The conversation_history table keeps a simplified transcript for auditing;
        # the `history` variable below keeps the full SDK context for the LLM.
        await add_to_history(USER_ID, "user", question)
        await add_to_history(USER_ID, "assistant", result.final_output)

        # to_input_list() keeps the run's full history:
        # messages, tool calls (memorize, recall...), tool outputs, handoffs.
        #
        # ⚠ Do NOT slice naively (history[-N:]): you risk splitting a
        # tool_call / tool_call_output pair and breaking the API on the next turn with
        # "No tool call found for function call output".
        #
        # For a long conversation in production, prefer SQLiteSession
        # (seen in 3.2), which truncates intelligently, or implement your own
        # truncation that respects call_id pairs.
        history = result.to_input_list()

asyncio.run(main())
