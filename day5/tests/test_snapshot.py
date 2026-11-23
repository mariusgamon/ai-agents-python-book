# tests/test_snapshot.py
# pip install syrupy
# 1st run: pytest tests/test_snapshot.py --snapshot-update  (creates the snapshot)
# Later runs: pytest compares. A diff = a behavior change to review.
import pytest
from agents import Runner
from my_agents import billing_agent  # your production agent

@pytest.mark.asyncio
async def test_agent_tool_sequence_snapshot(snapshot):
    result = await Runner.run(billing_agent, input="VAT on €1000 at 20%", max_turns=3)
    # We don't snapshot the LLM's raw text: it changes on every call.
    # We snapshot the sequence of tools called, which should stay stable.
    tools_called = [
        item.raw_item.name
        for item in result.new_items
        if item.type == "tool_call_item"
    ]
    assert tools_called == snapshot
