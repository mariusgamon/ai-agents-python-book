import json
from mistral_raw import llm, SYSTEM_PROMPT, extract_json
from dispatcher import dispatch_tool


def agent_with_tools(user_input: str, max_turns: int = 10) -> str:
    """
    A complete agent with tool calling from scratch.

    Flow on each turn:
    1. The LLM answers
    2. If JSON   → dispatcher → result injected → next turn
    3. If text   → final answer → we return
    4. If max_turns is reached → RuntimeError
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_input},
    ]

    for turn in range(1, max_turns + 1):
        print(f"\n── Turn {turn} ──────────────────────────")

        # LLM call
        response = llm(messages)
        messages.append({"role": "assistant", "content": response})

        print(f"LLM : {response[:120]}{'...' if len(response) > 120 else ''}")

        # ─── Try to parse it as a tool call ─────────────────────────────────
        stripped = extract_json(response)   # tolerates ```json ... ```
        if stripped.startswith("{") and stripped.endswith("}"):
            try:
                data = json.loads(stripped)

                tool_name = data.get("tool", "")
                args      = data.get("args", {})

                if not tool_name:
                    # Valid JSON but not a tool call → final answer
                    return response

                # Run the tool
                print(f"→ Tool : {tool_name}({args})")
                tool_result = dispatch_tool(tool_name, args)
                print(f"← Result: {tool_result[:80]}{'...' if len(tool_result) > 80 else ''}")

                # Inject the result into the context
                messages.append({
                    "role":    "user",
                    "content": (
                        f"Result of '{tool_name}':\n{tool_result}\n\n"
                        "Continue with this data."
                    ),
                })
                continue  # next turn

            except json.JSONDecodeError:
                # Starts with { but isn't valid JSON
                # The LLM may have made a formatting error → final answer
                print("⚠ Invalid JSON — treated as the final answer")
                return response

        # ─── No JSON → final answer ─────────────────────────────────────────
        return response

    raise RuntimeError(
        f"Agent stuck after {max_turns} turns. "
        f"Check the system prompt or increase max_turns."
    )


# ─── Test ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    questions = [
        "What's the weather like in Boston right now?",
        "What is 847.50 * 1.20 (with 20% VAT)?",
        "What's the weather like in Tokyo, and what is 15 * 7?",
    ]

    for q in questions:
        print(f"\n{'='*60}")
        print(f"Question: {q}")
        print(f"{'='*60}")
        result = agent_with_tools(q)
        print(f"\nFinal answer: {result}")
