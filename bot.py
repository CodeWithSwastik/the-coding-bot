import os

import discord
from discord import Intents
from discord.ext import commands

from config import Config

# from utils.database import Database


class TheCodingBot(commands.Bot):
    def __init__(self):
        self.config = Config()
        # self.db = Database()
        super().__init__(
            command_prefix=commands.when_mentioned_or(">"),
            intents=Intents.all(),
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions(
                everyone=False, users=True, roles=False
            ),
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="over TCA"
            ),
        )

        # public cogs
        for file in os.listdir("cogs/public") + os.listdir("cogs/private"):

            if file.endswith(".py") and not file.startswith("_"):

                name = file[:-3]
                self.load_extension(name=f"cogs.{name}")

        self.load_extension("jishaku")
        self.load_extension("autoreload")

    async def on_ready(self):
        print("Bot is ready.")

    @property
    def session(self):
        return self.http._HTTPClient__session

    @property
    def tca(self):
        return self.get_guild(681882711945641997)

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or CustomContext)

    def get_custom_emoji(self, name):
        emoji = discord.utils.get(self.emojis, name=name, guild__id=681882711945641997)
        return emoji or ""

    async def run_async(self, func, *args, **kwargs):
        return await self.loop.run_in_executor(None, func, *args, **kwargs)


class CustomContext(commands.Context):
    pass
