# cost_calculator.py — full version (the book shows a condensed version in §3.5)
#
# Cost of the history injected into the prompt, under three memory strategies.
# The book's scenario: a B2B SaaS support chatbot, 500 conversations/day,
# 15 exchanges per conversation, ~500 tokens per exchange (100 user + 400 assistant).
#
#     python cost_calculator.py
import math

MODEL_INPUT_COST_PER_1M = 2.50    # $ per 1M input tokens. Update from the official pricing page.
MODEL_OUTPUT_COST_PER_1M = 10.00  # $ per 1M output tokens (output ≈ 4× input)

CONVERSATIONS_PER_DAY = 500
TURNS = 15
TOKENS_PER_TURN = 500
DAYS_PER_MONTH = 30

SUMMARY_EVERY = 5          # the history is summarized every 5 turns
SUMMARY_TOKENS = 350       # size of the summary that replaces the raw history
EXTERNAL_MEMORY_TOKENS = 350  # targeted facts injected from SQLite on each request


def monthly_memory_cost(
    conversations_per_day: int,
    turns: int,
    avg_history_tokens: int,
) -> float:
    """Monthly cost of the history injected into the prompt."""
    daily = avg_history_tokens * turns * conversations_per_day
    return daily * MODEL_INPUT_COST_PER_1M / 1_000_000 * DAYS_PER_MONTH


def _usd(x: float) -> float:
    """Commercial rounding to the cent (round() rounds 65.625 to 65.62)."""
    return math.floor(x * 100 + 0.5) / 100


def _report(avg_tokens: float, extra_daily_cost: float = 0.0) -> dict:
    requests_per_day = CONVERSATIONS_PER_DAY * TURNS
    daily_tokens = float(avg_tokens * requests_per_day)
    daily_cost = daily_tokens * MODEL_INPUT_COST_PER_1M / 1_000_000 + extra_daily_cost
    return {
        "daily_history_tokens": round(daily_tokens, 1),
        "daily_cost_usd": _usd(daily_cost),
        "monthly_cost_usd": _usd(daily_cost * DAYS_PER_MONTH),
    }


def naive_full_history() -> dict:
    """The whole history is resent on every turn: (t-1) × 500 tokens at turn t."""
    history = [(t - 1) * TOKENS_PER_TURN for t in range(1, TURNS + 1)]
    avg = sum(history) / TURNS
    return {"avg_history_tokens_per_request": round(avg, 1), **_report(avg)}


def summarize_every_n_turns() -> dict:
    """
    Every SUMMARY_EVERY turns, the raw history is replaced by a summary.
    Each summarization is an LLM call: you pay for the summarized history as input
    and for the generated summary as output.
    """
    history, summary_calls_input = [], 0
    for t in range(1, TURNS + 1):
        block = (t - 1) // SUMMARY_EVERY            # number of summaries already done
        raw = ((t - 1) % SUMMARY_EVERY) * TOKENS_PER_TURN
        history.append((SUMMARY_TOKENS if block else 0) + raw)

    n_summaries = (TURNS - 1) // SUMMARY_EVERY
    for k in range(n_summaries):
        # input = previous summary (if any) + the last SUMMARY_EVERY turns
        summary_calls_input += (SUMMARY_TOKENS if k else 0) + SUMMARY_EVERY * TOKENS_PER_TURN

    synthesis_daily = CONVERSATIONS_PER_DAY * (
        summary_calls_input * MODEL_INPUT_COST_PER_1M
        + n_summaries * SUMMARY_TOKENS * MODEL_OUTPUT_COST_PER_1M
    ) / 1_000_000

    avg = sum(history) / TURNS
    return {
        "avg_history_tokens_per_request": round(avg, 1),
        **_report(avg),                                   # history only, like the other strategies
        "synthesis_monthly_usd": _usd(synthesis_daily * DAYS_PER_MONTH),
        "total_monthly_usd": _report(avg, extra_daily_cost=synthesis_daily)["monthly_cost_usd"],
    }


def external_sqlite_memory() -> dict:
    """Only a few targeted facts are injected (SQLite lookup, no LLM call)."""
    return {"tokens_per_request": EXTERNAL_MEMORY_TOKENS, **_report(EXTERNAL_MEMORY_TOKENS)}


if __name__ == "__main__":
    scenarios = {
        "naive_full_history": naive_full_history(),
        f"summarize_every_{SUMMARY_EVERY}_turns": summarize_every_n_turns(),
        "external_sqlite_memory": external_sqlite_memory(),
    }
    for name, stats in scenarios.items():
        print(f"\n--- {name} ---")
        for key, value in stats.items():
            print(f"  {key}: {value}")
