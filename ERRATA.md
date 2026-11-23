# Errata — differences between the book and this repo

The code in this repo is extracted from the book and then tested. Here's what differs.

## Fixes

None: the book's code runs as is.

## Files added by the repo

- `day3/cost_calculator.py` — full version of the script (the book shows a condensed version in §3.5)
- `templates/template_research_agent.py` — complete code (the book shows its outline and an excerpt)
- `templates/template_agent_generation.py` — complete code (the book shows its outline and an excerpt)
- `templates/template_orchestrator_agent.py` — complete code (the book shows its outline and an excerpt)
- `bonus_from_scratch/multi_agent.py` — complete code for §B.7 (the book shows its outline and an excerpt)
- `bonus_from_scratch/complete_agent.py` — complete code for §B.8 (the book shows its outline and an excerpt)
- `day5/my_pipeline.py` — `process_request()` imported by `tests/test_pipeline.py`
- `day5/my_agents.py` — `billing_agent` imported by `tests/test_golden.py` and `tests/test_snapshot.py`
- `day5/tests/__snapshots__/test_snapshot.ambr` — reference snapshot (tool sequence), so that `pytest tests/` passes without `--snapshot-update`
- `day5/pytest.ini` — `pythonpath` for `from tools.vat import ...` + an asyncio loop shared across the tests

## Differences from the French edition

Identifiers, imports, and logic are the same. A few strings change behavior and were adapted:

- `day5/tests/test_agent_behavior.py`, `test_golden.py`: commas are stripped too before checking amounts (English answers write “1,200”).
- `bonus_from_scratch/agent_loop.py`: the end sentinel `"FIN:"` becomes `"END:"` (same length).
- `appendix/security_guardrails.py`, `document_sanitizer.py`: the injection patterns detect English attacks.
- `templates/template_agent_generation.py`: `ContentBrief` values in English (`"short"`, `"medium"`, `"long"`, `"report"`, `"neutral"`…).
- `day2/weather_agent.py`, `day5/tools/weather.py`: `"lang": "en"`.
- `day6/`: app `my-agent-api`, Fly region `iad`.
