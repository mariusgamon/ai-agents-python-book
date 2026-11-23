# tool_stock_naive.py
from agents import function_tool
import httpx

@function_tool
async def get_stock_price(ticker: str) -> dict:
    """Gets the current price of a stock for a given ticker."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://api.marketdata.example/v1/quote/{ticker}"
        )
        return resp.json()
