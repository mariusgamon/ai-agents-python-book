import httpx
import ast
import operator


def get_weather(city: str) -> str:
    """Gets the weather via Open-Meteo (free, no key)."""
    # Geocoding
    geo = httpx.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "en"},
        timeout=10.0,
    ).json()

    if not geo.get("results"):
        return f"City not found: {city}"

    loc  = geo["results"][0]
    lat, lon = loc["latitude"], loc["longitude"]

    # Weather
    meteo = httpx.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude":          lat,
            "longitude":         lon,
            "current_weather":   True,
            "wind_speed_unit":   "kmh",
        },
        timeout=10.0,
    ).json()

    cw = meteo["current_weather"]
    return (
        f"Weather in {city}: {cw['temperature']}°C, "
        f"wind {cw['windspeed']} km/h."
    )


def calculate(expression: str) -> str:
    """Safely evaluates a math expression.

    Restrictions:
    - only int/float constants are accepted (no strings, lists, etc.)
    - only the 6 operations listed in SAFE_OPS are allowed
    - everything else raises ValueError with an explicit message
    """
    SAFE_OPS = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.USub: operator.neg,
    }

    def _eval(node):
        if isinstance(node, ast.Constant):
            # Explicit filtering: only numbers are accepted.
            # Without this check, "calculate(\"hello\")" would pass silently.
            if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                return node.value
            raise ValueError(f"Constant not allowed: {type(node.value).__name__}")
        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in SAFE_OPS:
                raise ValueError(f"Operation not allowed: {op_type.__name__}")
            return SAFE_OPS[op_type](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in SAFE_OPS:
                raise ValueError(f"Unary operation not allowed: {op_type.__name__}")
            return SAFE_OPS[op_type](_eval(node.operand))
        raise ValueError(f"Expression not allowed: {type(node).__name__}")

    try:
        result = _eval(ast.parse(expression, mode="eval").body)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Calculation error: {e}"


def search_web_snippets(query: str, n: int = 3) -> str:
    """Searches for web snippets via the public DuckDuckGo Instant Answer API (no key).

    Warning: this isn't a real news API. DuckDuckGo Instant Answer
    returns RelatedTopics (encyclopedic, Wikipedia-style snippets), not
    necessarily recent news — sometimes nothing at all.

    For professional tech watch, use a reliable search/news API
    (Tavily, Brave Search, NewsAPI...) or a controlled RSS feed.
    """
    try:
        r = httpx.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1},
            timeout=10.0,
        ).json()
        topics = r.get("RelatedTopics", [])[:n]
        if not topics:
            return f"No results for: {query}"
        return "\n".join(
            f"- {t['Text']}" for t in topics if "Text" in t
        )
    except Exception as e:
        return f"Search error: {e}"
