# email_extractor.py
import config
from pydantic import BaseModel, Field
from agents import Agent, Runner
import asyncio


class ActionItem(BaseModel):
    """An action item extracted from the email."""
    description: str = Field(description="Short description of the action")
    assignee: str | None = Field(
        default=None,
        description="Person the action is assigned to, if mentioned"
    )


class EmailAnalysis(BaseModel):
    """Structured analysis of an incoming email."""
    sender_name: str = Field(description="Sender's full name")
    sender_company: str | None = Field(
        default=None,
        description="Sender's company, if mentioned"
    )
    subject_summary: str = Field(
        description="One-sentence summary of the subject (max 15 words)"
    )
    urgency: str = Field(
        description="Urgency level: low, medium, high, critical"
    )
    action_items: list[ActionItem] = Field(
        default_factory=list,
        description="List of actions requested in the email"
    )
    requires_response: bool = Field(
        description="True if the email expects an explicit reply"
    )


agent = Agent(
    name="EmailAnalyzer",
    model=config.DEFAULT_MODEL,
    instructions="""You analyze incoming emails and extract structured information.
    Be precise and concise. For urgency, use these rules:
    - critical: deadline within 24h or explicit "urgent"
    - high: deadline within a week or strong language
    - medium: standard business request
    - low: informational, no action needed""",
    output_type=EmailAnalysis,  # ← Force structured output
)


TEST_EMAIL = """
Hi,

Following our call this morning, I'm confirming that the v2 deployment
absolutely must be finished before Friday at 6 p.m.

The client (Acme Corp) is threatening to terminate the contract if we
don't deliver on time. Could you:
1. Finalize the integration tests by Wednesday
2. Prepare the migration script for Thomas
3. Reply to confirm that this is feasible

Thanks,
Sophie Martin
CTO — DataFlow Inc.
"""


async def main():
    result = await Runner.run(agent, input=TEST_EMAIL)

    # result.final_output is an EmailAnalysis object directly
    analysis: EmailAnalysis = result.final_output

    print(f"From: {analysis.sender_name} ({analysis.sender_company})")
    print(f"Subject: {analysis.subject_summary}")
    print(f"Urgency: {analysis.urgency}")
    print(f"Reply expected: {'Yes' if analysis.requires_response else 'No'}")
    print(f"\nActions ({len(analysis.action_items)}):")
    for i, action in enumerate(analysis.action_items, 1):
        assignee = f" → {action.assignee}" if action.assignee else ""
        print(f"  {i}. {action.description}{assignee}")

    # In production: serialize to your database / API
    print(f"\nJSON for your API:\n{analysis.model_dump_json(indent=2)}")


asyncio.run(main())
