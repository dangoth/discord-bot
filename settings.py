from dotenv import load_dotenv
import os

load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
WARCRAFTLOGS_API_KEY = os.getenv("WARCRAFTLOGS_API_KEY")
OPENAI_TOKEN = os.getenv("OPENAI_TOKEN")
