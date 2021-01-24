import os
import disco_bot

from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCO_BOT_TOKEN')

disco = disco_bot.client(auth_token=TOKEN);
disco.start();