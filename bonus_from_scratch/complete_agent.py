"""
complete_agent.py
─────────────────────────────────────────────────────────────────────────────
Mini-framework agent from scratch.
Dependencies: httpx, python-dotenv
No agent SDK.
"""

import json
import os
import ast
import inspect
import operator
from datetime import datetime

import httpx
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════════════════════════════
# 1. LLM
# ═══════════════════════════════════════════════════════

def llm(messages: list[dict], model: str = "mistral-small-latest") -> str:
    r = httpx.post(
        "https://api.mistral.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['MISTRAL_API_KEY']}"},
        json={"model": model, "messages": messages, "temperature": 0.2},
        timeout=30.0,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def extract_json(text: str) -> str:
    """Removes the ```json ... ``` fences some models add around the JSON."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else ""   # removes the ```json line
        if t.rstrip().endswith("```"):
            t = t.rstrip()[:-3]
    return t.strip()


# ═══════════════════════════════════════════════════════
# 2. TOOLS
# ═══════════════════════════════════════════════════════

def get_weather(city: str) -> str:
    geo = httpx.get("https://geocoding-api.open-meteo.com/v1/search",
                    params={"name": city, "count": 1}, timeout=10).json()
    if not geo.get("results"):
        return f"Unknown city: {city}"
    loc = geo["results"][0]
    m   = httpx.get("https://api.open-meteo.com/v1/forecast",
                    params={"latitude": loc["latitude"], "longitude": loc["longitude"],
                            "current_weather": True}, timeout=10).json()
    cw  = m["current_weather"]
    return f"{city}: {cw['temperature']}°C, wind {cw['windspeed']} km/h"


def calculate(expression: str) -> str:
    SAFE = {ast.Add: operator.add, ast.Sub: operator.sub,
            ast.Mult: operator.mul, ast.Div: operator.truediv,
            ast.Pow: operator.pow, ast.USub: operator.neg}
    def ev(n):
        if isinstance(n, ast.Constant): return n.value
        if isinstance(n, ast.BinOp):   return SAFE[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp): return SAFE[type(n.op)](ev(n.operand))
        raise ValueError(f"Not allowed: {ast.dump(n)}")
    try:
        return f"{expression} = {ev(ast.parse(expression, mode='eval').body)}"
    except Exception as e:
        return f"Error: {e}"


def get_datetime(tz: str = "Europe/Paris") -> str:
    """Returns current date/time in the requested timezone (default: Paris).
    Uses zoneinfo (stdlib since Python 3.9) — no external dep needed."""
    from zoneinfo import ZoneInfo
    return datetime.now(ZoneInfo(tz)).strftime("%A %d %B %Y, %H:%M %Z")


TOOLS: dict[str, callable] = {
    "get_weather":  get_weather,
    "calculate":    calculate,
    "get_datetime": get_datetime,
}


# ═══════════════════════════════════════════════════════
# 3. SKILLS (composed logic)
# ═══════════════════════════════════════════════════════

def skill_weather_report(city: str) -> str:
    """Weather + seasonal context written by the LLM."""
    raw = get_weather(city)
    return llm([
        {"role": "system",  "content": "You are a meteorologist. Comment on the weather in 2 sentences."},
        {"role": "user",    "content": f"Data: {raw}"},
    ])


TOOLS["weather_report"] = skill_weather_report   # registered exactly like a tool


# ═══════════════════════════════════════════════════════
# 4. DISPATCHER
# ═══════════════════════════════════════════════════════

def dispatch_tool(name: str, args: dict) -> str:
    if name not in TOOLS:
        return f"[ERROR] Unknown tool: '{name}'. Available: {', '.join(TOOLS)}"
    try:
        return str(TOOLS[name](**args))
    except Exception as e:
        return f"[ERROR] {name}: {type(e).__name__}: {e}"


# ═══════════════════════════════════════════════════════
# 5. AGENT LOOP
# ═══════════════════════════════════════════════════════

# The model must know the PARAMETERS, not just the names:
# without them, it makes up get_weather(location=...) -> TypeError.
TOOLS_DESC = "\n".join(f"- {name}{inspect.signature(fn)}" for name, fn in TOOLS.items())

SYSTEM = f"""You are an assistant that can use tools.

To call a tool, reply ONLY with this JSON:
{{"tool": "name", "args": {{...}}}}

Tools (use exactly these parameter names):
{TOOLS_DESC}

For the final answer: write normally (no JSON)."""


def run(user_input: str, max_turns: int = 10, verbose: bool = True) -> str:
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user",   "content": user_input},
    ]

    for turn in range(1, max_turns + 1):
        if verbose:
            print(f"[Turn {turn}/{max_turns}]", end=" ")

        response = llm(messages)
        messages.append({"role": "assistant", "content": response})

        stripped = extract_json(response)   # tolerates ```json ... ```
        if stripped.startswith("{") and stripped.endswith("}"):
            try:
                data   = json.loads(stripped)
                name   = data.get("tool", "")
                args   = data.get("args", {})
                if name:
                    if verbose: print(f"→ {name}({args})")
                    result = dispatch_tool(name, args)
                    if verbose: print(f"  ← {result[:60]}{'...' if len(result)>60 else ''}")
                    messages.append({
                        "role":    "user",
                        "content": f"Result of '{name}': {result}\n\nContinue.",
                    })
                    continue
            except json.JSONDecodeError:
                pass

        if verbose: print(f"→ Final answer")
        return response

    raise RuntimeError(f"Agent stuck after {max_turns} turns.")


# ═══════════════════════════════════════════════════════
# 6. ENTRY POINT
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    tests = [
        "What time and what day is it?",
        "What's the weather like in Chicago? Give me a real weather commentary.",
        "What is 1250 * 1.055 (a 5.5% fee)?",
    ]

    for question in tests:
        print(f"\n{'═'*55}")
        print(f"❓ {question}")
        print(f"{'─'*55}")
        answer = run(question, verbose=True)
        print(f"\n✅ {answer}")
