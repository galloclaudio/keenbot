from bot import TwitchChatBot
from dotenv import load_dotenv
import os

load_dotenv()

bot = TwitchChatBot(
    username=os.getenv("USERNAME"),
    password=os.getenv("PASSWORD"),
    channels=os.getenv("CHANNELS").split(",")
)

bot.connect()
