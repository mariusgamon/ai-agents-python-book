# orchestrator_naive.py
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
    instructions="You are an assistant. Use your tools if needed to answer.",
    tools=[
        content_finder.as_tool(
            tool_name="find_content",
            tool_description="Searches the document base and returns the relevant excerpts.",
        ),
    ],
)

result = await Runner.run(orchestrator, input="Find me the docs on the auth API")
print(result.final_output)
# → "I couldn't find any matching document."
