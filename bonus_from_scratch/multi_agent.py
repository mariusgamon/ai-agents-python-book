import json
from mistral_raw import llm, extract_json
from dispatcher import dispatch_tool


# ─── Specialized agents ────────────────────────────────────────────────────────

def research_agent(query: str) -> str:
    """
    Specialized agent: factual research.
    Short context, precise instructions = better accuracy.
    """
    messages = [
        {
            "role":    "system",
            "content": (
                "You are an expert in factual research. "
                "Answer only with verifiable facts. "
                "Be concise (3-5 lines max). "
                "If you are not sure, say so explicitly."
            ),
        },
        {"role": "user", "content": query},
    ]
    return llm(messages)


def writer_agent(brief: str) -> str:
    """
    Specialized agent: writing and rephrasing.
    Turns raw data into readable text.
    """
    messages = [
        {
            "role":    "system",
            "content": (
                "You are an expert in clear, concise writing. "
                "Turn the brief you are given into structured, professional text. "
                "Use short paragraphs. No unnecessary jargon."
            ),
        },
        {"role": "user", "content": brief},
    ]
    return llm(messages)


def analyst_agent(data: str) -> str:
    """
    Specialized agent: analysis and recommendations.
    """
    messages = [
        {
            "role":    "system",
            "content": (
                "You are a senior analyst. From the data provided, "
                "identify 2-3 key insights and state one actionable recommendation. "
                "Format: Insights (list) + Recommendation (1 sentence)."
            ),
        },
        {"role": "user", "content": data},
    ]
    return llm(messages)


# ─── Agent registry ────────────────────────────────────────────────────────────
AGENTS: dict[str, callable] = {
    "research":  research_agent,
    "writer":    writer_agent,
    "analyst":   analyst_agent,
}


# ─── The orchestrator's system prompt ─────────────────────────────────────────
ORCHESTRATOR_SYSTEM = f"""You are an orchestrator. You coordinate specialized agents
and tools to accomplish complex tasks.

To delegate to an agent, reply ONLY with this JSON:
{{"delegate": "agent_name", "input": "what the agent must accomplish"}}

To call a tool, reply ONLY with this JSON:
{{"tool": "tool_name", "args": {{...}}}}

Available agents: {', '.join(AGENTS.keys())}
Available tools : get_weather(city: str), calculate(expression: str),
                  search_web_snippets(query: str, n: int)

When the task is completely done, write your final answer normally (no JSON).

Recommended strategy for a complex task:
1. research  → gather the facts
2. analyst   → extract the insights
3. writer    → write the final summary
"""


# ─── Main orchestrator ─────────────────────────────────────────────────────────

def orchestrator(user_request: str, max_turns: int = 12) -> str:
    """
    Multi-agent orchestrator from scratch.

    Handles two kinds of delegation:
    - {"delegate": "agent_name", "input": "..."} → sub-agent
    - {"tool": "tool_name", "args": {...}}        → tool Python
    """
    messages = [
        {"role": "system", "content": ORCHESTRATOR_SYSTEM},
        {"role": "user",   "content": user_request},
    ]
    delegation_log = []  # trace of delegations, for debugging

    for turn in range(1, max_turns + 1):
        print(f"\n── Turn {turn}/{max_turns} ──────────────────────────────")

        response = llm(messages)
        messages.append({"role": "assistant", "content": response})

        stripped = extract_json(response)   # tolerates ```json ... ```

        # ── Attempt JSON parsing ─────────────────────────────────────────────
        if stripped.startswith("{") and stripped.endswith("}"):
            try:
                data = json.loads(stripped)

                # Case 1: delegation to an agent
                if "delegate" in data:
                    agent_name  = data["delegate"]
                    agent_input = data.get("input", user_request)

                    if agent_name not in AGENTS:
                        result = f"[ERROR] Unknown agent: '{agent_name}'"
                    else:
                        print(f"→ Delegating to: {agent_name}")
                        result = AGENTS[agent_name](agent_input)
                        delegation_log.append({"agent": agent_name, "turns": turn})

                    print(f"← Result ({agent_name}): {result[:80]}...")
                    messages.append({
                        "role":    "user",
                        "content": f"Result from agent '{agent_name}':\n{result}\n\nContinue.",
                    })
                    continue

                # Case 2: tool call
                if "tool" in data:
                    tool_name = data["tool"]
                    args      = data.get("args", {})
                    print(f"→ Tool: {tool_name}({args})")
                    result = dispatch_tool(tool_name, args)
                    print(f"← Result: {result[:80]}")
                    messages.append({
                        "role":    "user",
                        "content": f"Result of tool '{tool_name}':\n{result}\n\nContinue.",
                    })
                    continue

            except json.JSONDecodeError:
                pass  # malformed JSON → treat as the final answer

        # ── Final answer ──────────────────────────────────────────────────────
        print(f"\nDelegations made: {delegation_log}")
        return response

    raise RuntimeError(f"Orchestrator stuck after {max_turns} turns.")


# ─── Test ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    result = orchestrator(
        "Write a professional summary of this week's "
        "news about AI in Europe."
    )
    print(f"\n{'='*60}\nFinal summary:\n{result}")
