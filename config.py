import os

try:
    import dotenv
except ImportError:
    pass
else:
    dotenv.load_dotenv(".env")


class Config:
    def __init__(self):
        self.bot_token = os.environ["BOT_TOKEN"]
        self.logger_url = os.environ["LOGGER_URL"]
        self.default_prefix = os.environ.get('DEFAULT_PREFIX', '>')