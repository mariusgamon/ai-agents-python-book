from mistral_raw import llm
from tools import search_web_snippets, calculate


# ─── Tool (atomic action) ──────────────────────────────────────────────────────
# Nothing to redefine — get_weather, calculate, etc. are already tools.


# ─── Skill (composed logic) ───────────────────────────────────────────────────

def skill_research_and_summarize(query: str) -> str:
    """
    Skill: searches for news AND summarizes it in 3 points.
    Combines search_web_snippets (tool) + an LLM call to synthesize.
    """
    # Step 1: get the raw data via a tool
    raw = search_web_snippets(query=query, n=5)

    # Step 2: ask the LLM to synthesize
    summary_messages = [
        {
            "role":    "system",
            "content": "You are a tech-watch expert. Synthesize into 3 concise key points.",
        },
        {
            "role":    "user",
            "content": f"Topic: {query}\n\nRaw results:\n{raw}",
        },
    ]
    return llm(summary_messages)


def skill_budget_check(amount: float, vat_rate: float = 0.20) -> str:
    """
    Skill: computes the pre-tax amount, VAT, and total, and generates a comment.
    Combines calculate (tool) + business logic + an LLM for the comment.
    """
    # Step 1: calculations via the tool
    ttc_result   = calculate(f"{amount} * {1 + vat_rate}")
    vat_amount   = calculate(f"{amount} * {vat_rate}")

    # Step 2: contextual comment via the LLM
    comment_msgs = [
        {"role": "system", "content": "Give a brief budget tip (1 sentence)."},
        {
            "role":    "user",
            "content": f"Pre-tax: €{amount}  VAT({vat_rate*100:.0f}%): {vat_amount}  {ttc_result}",
        },
    ]
    comment = llm(comment_msgs)

    return f"Pre-tax: €{amount} | {ttc_result} | Tip: {comment}"


# ─── Updated registry ──────────────────────────────────────────────────────────
from dispatcher import TOOLS  # we extend the existing registry

TOOLS.update({
    "research_and_summarize": skill_research_and_summarize,
    "budget_check":           skill_budget_check,
})
