import os
from bot import TheCodingBot

os.environ.setdefault("JISHAKU_HIDE", "1")
os.environ.setdefault("JISHAKU_NO_UNDERSCORE", "1")

if __name__ == "__main__":
    bot = TheCodingBot()
    bot.run(bot.config.bot_token)
