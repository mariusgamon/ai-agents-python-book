# handoff_triage.py
import config

from agents import Agent, Runner
import asyncio

# Each language agent produces the FINAL answer in its language
french_agent = Agent(
    name="FrenchAgent",
    model=config.DEFAULT_MODEL,
    instructions="You always answer in French, clearly and directly.",
)

spanish_agent = Agent(
    name="SpanishAgent",
    model=config.DEFAULT_MODEL,
    instructions="Respondes siempre en español, de forma clara y directa.",
)

# The triage agent routes, then steps aside: it never answers itself
triage_agent = Agent(
    name="TriageAgent",
    model=config.DEFAULT_MODEL,
    instructions="""Detect the language of the question.
    If it's French, hand off to FrenchAgent.
    If it's Spanish, hand off to SpanishAgent.
    Don't answer yourself.""",
    handoffs=[french_agent, spanish_agent],
)

async def main():
    result = await Runner.run(triage_agent, input="¿Qué es un agente de IA?")
    # The answer comes from SpanishAgent, not from triage
    print(result.final_output)

asyncio.run(main())
