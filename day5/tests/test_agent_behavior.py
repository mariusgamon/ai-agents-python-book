# tests/test_agent_behavior.py
import pytest
import config
from agents import Agent, Runner, ModelSettings
from tools.vat import calculate_vat

# Test agent (same config as production, minimal cost)
agent = Agent(
    name="TestAssistant",
    instructions="You are a billing assistant. Use calculate_vat for any tax question.",
    tools=[calculate_vat],
    model="gpt-5.4-mini",  # cheaper for tests
)

@pytest.mark.asyncio
async def test_agent_calls_vat_tool():
    """The agent must call calculate_vat when asked a VAT question."""
    result = await Runner.run(
        agent,
        input="What's the total including VAT for €500 before tax?",
        max_turns=3,
    )
    # Check that the tool was called
    tool_call_items = [
        item for item in result.new_items
        if item.type == "tool_call_item"
    ]
    assert len(tool_call_items) > 0, "The agent did not call calculate_vat"

@pytest.mark.asyncio
async def test_agent_response_contains_amount():
    """The answer must contain the correct amount including VAT."""
    result = await Runner.run(
        agent,
        input="VAT on €1000 before tax at 20%?",
        max_turns=3,
    )
    # Models often write “1,200” or “1 200” (with a no-break space, U+202F or U+00A0)
    output = result.final_output
    for space in ("\u202f", "\u00a0", " ", ","):
        output = output.replace(space, "")
    assert "1200" in output

@pytest.mark.asyncio
async def test_agent_stops_on_max_turns():
    """Deterministic test: the tool call is forced and only one turn is allowed.
    The agent needs a second turn to answer after the tool: the SDK must
    raise MaxTurnsExceeded instead of continuing."""
    from agents.exceptions import MaxTurnsExceeded
    forced = agent.clone(model_settings=ModelSettings(tool_choice="required"))
    with pytest.raises(MaxTurnsExceeded):
        await Runner.run(forced, input="VAT on €100 before tax?", max_turns=1)
