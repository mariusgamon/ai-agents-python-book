# observe_with_logfire.py — instrumentation automatique
import logfire
import openai
from dotenv import load_dotenv

load_dotenv()                          # loads LOGFIRE_TOKEN and OPENAI_API_KEY from .env
logfire.configure()
logfire.instrument_openai()            # ← captures all OpenAI calls

# From here on, every SDK call generates a trace in Logfire
# No change to your agent code needed
