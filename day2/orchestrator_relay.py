# orchestrator_relay.py
from agents import Agent, Runner

content_finder = Agent(
    name="content_finder",
    model="gpt-5.4-mini",
    instructions="You search the document base and return the relevant excerpts.",
    tools=[search_docs],
)

orchestrator = Agent(
    name="orchestrator",
    model="gpt-5.4-mini",
    instructions=(
        "You are an assistant. For any document search request, "
        "hand off to content_finder. For other requests, answer directly."
    ),
    handoffs=[content_finder],  # full handoff, no reinterpretation
)

result = await Runner.run(orchestrator, input="Find me the docs on the auth API")
print(result.final_output)
# → content_finder's output, intact.
