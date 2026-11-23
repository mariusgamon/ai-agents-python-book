from tools import get_weather, calculate, search_web_snippets

# ─── Tool registry ────────────────────────────────────────────────────────────
# Key  : the exact name the LLM must mention in its JSON
# Value: the matching Python function
TOOLS: dict[str, callable] = {
    "get_weather":         get_weather,
    "calculate":           calculate,
    "search_web_snippets": search_web_snippets,
}


def dispatch_tool(tool_name: str, args: dict) -> str:
    """
    Runs a tool by its name.

    Always returns a string — even on error.
    That lets the loop continue and the LLM adapt.
    """
    if tool_name not in TOOLS:
        known = ", ".join(TOOLS.keys())
        return f"[ERROR] Unknown tool: '{tool_name}'. Available: {known}"

    try:
        result = TOOLS[tool_name](**args)
        return str(result)

    except TypeError as e:
        return f"[ERROR] Invalid arguments for '{tool_name}': {e}"

    except Exception as e:
        return f"[ERROR] '{tool_name}' failed: {type(e).__name__}: {e}"
