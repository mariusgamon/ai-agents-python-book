# observe_with_langfuse.py — tracing an agent with Langfuse (Langfuse SDK v3 and later)
import config
from langfuse import observe, get_client
from agents import Agent, Runner
import asyncio

# The client reads LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, and LANGFUSE_BASE_URL
# (or LANGFUSE_HOST) from the environment: nothing to hardcode.
langfuse = get_client()

agent = Agent(
    name="TracedAssistant",
    instructions="You are a helpful assistant.",
    model=config.DEFAULT_MODEL,
)


@observe(as_type="generation")  # ← each call creates an observation in Langfuse
async def ask_agent(question: str) -> str:
    # Metadata for filtering in the dashboard
    langfuse.update_current_generation(
        model=config.DEFAULT_MODEL,
        metadata={"agent": "TracedAssistant", "version": "1.0"},
    )
    result = await Runner.run(agent, input=question)

    # Tokens for the full run (context_wrapper.usage aggregates all calls)
    usage = result.context_wrapper.usage
    langfuse.update_current_generation(
        usage_details={"input": usage.input_tokens, "output": usage.output_tokens},
    )
    return result.final_output


async def main():
    answer = await ask_agent("What's the difference between a list and a tuple?")
    print(answer)
    langfuse.flush()  # forces sending before exiting


asyncio.run(main())
