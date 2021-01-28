import os
import disco_bot

from dotenv import load_dotenv

if __name__ == '__main__':
    load_dotenv()
    TOKEN = os.getenv('DISCO_BOT_TOKEN')
    disco = disco_bot.client(auth_token=TOKEN);
    disco.start();