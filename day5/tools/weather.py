# tools/weather.py
import config
import httpx
from agents import function_tool


async def fetch_weather(city: str) -> dict:
    """
    Gets the current weather for a city.

    Args:
        city: City name (e.g., "Paris", "London", "Chicago")

    Returns:
        Current weather with temperature, description, humidity,
        or an {"error": ...} dict if the service doesn't respond.
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": config.OPENWEATHER_API_KEY, "units": "metric", "lang": "en"}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except httpx.TimeoutException:
        return {"error": f"Timeout: the weather service isn't responding for {city}"}
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error {e.response.status_code} for {city}"}

    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "description": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"],
        "wind_kmh": round(data["wind"]["speed"] * 3.6, 1),
    }


# The same function, exposed to the agent as a tool (same name as in Day 2)
get_weather = function_tool(fetch_weather, name_override="get_weather")
