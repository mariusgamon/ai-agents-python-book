# tests/test_tools.py
# We test the logic (compute_vat, fetch_weather), not the FunctionTool objects.
import pytest
from tools.vat import compute_vat
from tools.weather import fetch_weather

# --- Deterministic tests (no LLM, no external API) ---

def test_vat_standard_rate():
    result = compute_vat(1000, rate=0.20)
    assert result["vat_amount"] == 200.0
    assert result["amount_incl_tax"] == 1200.0

def test_vat_zero_amount():
    result = compute_vat(0)
    assert result["vat_amount"] == 0.0

def test_vat_custom_rate():
    result = compute_vat(1000, rate=0.055)
    assert result["vat_amount"] == 55.0

# --- Tests with mocks (simulated external API) ---

@pytest.mark.asyncio
async def test_weather_api_down(monkeypatch):
    """When the weather API is unavailable, the tool returns a clean error."""
    import httpx

    async def mock_get(*args, **kwargs):
        raise httpx.ConnectTimeout("API unreachable")

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)
    result = await fetch_weather("London")
    assert "error" in result
    assert "timeout" in result["error"].lower()
