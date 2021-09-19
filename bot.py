import os
import random

import discord
from discord import Intents
from discord.ext import commands, tasks

from config import Config
from utils.database import Database


class TheCodingBot(commands.Bot):
    def __init__(self):
        self.config = Config()
        self.db = Database()
        super().__init__(
            command_prefix=commands.when_mentioned_or(">"),
            intents=Intents.all(),
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions(
                everyone=False, users=True, roles=False
            ),
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="myself start up"
            ),
        )

        for file in os.listdir("cogs"):

            if file.endswith(".py") and not file.startswith("_"):

                name = file[:-3]
                self.load_extension(name=f"cogs.{name}")

        self.load_extension("jishaku")
        self.load_extension("autoreload")

        self.status_change.start()

    async def on_ready(self):
        print("Bot is ready.")

    @property
    def session(self):
        return self.http._HTTPClient__session

    @property
    def tca(self):
        return self.get_guild(681882711945641997)

    @property
    def staff_role(self):
        return self.tca.get_role(795145820210462771)

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or CustomContext)

    def get_custom_emoji(self, name):
        emoji = discord.utils.get(self.emojis, name=name, guild__id=681882711945641997)
        return emoji or ""

    async def run_async(self, func, *args, **kwargs):
        return await self.loop.run_in_executor(None, func, *args, **kwargs)

    @tasks.loop(minutes=2)
    async def status_change(self):
        await self.wait_until_ready()
        statuses = [
            "over TCA",
            "you 👀",
            "swas",
            "@everyone",
            "general chat",
            "new members",
            "the staff team",
            "the mods",
            random.choice(self.staff_role.members).name,
            "helpers",
            "humans destroy the world",
            "AI take over the world",
            "https://youtu.be/dQw4w9WgXcQ",
            "verified bot tags with envy",
            random.choice(self.tca.get_role(737517726737629214).members).name
            + " (Server Booster)",
            "Server Boosters (boost to get your name on here)",
            "OG members",
            "people get banned",
        ]

        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=random.choice(statuses)
                + " | >help"
            )
        )

    @status_change.before_loop
    async def before_status_change(self):
        await self.wait_until_ready()


class CustomContext(commands.Context):
    
    async def embed(self, content, **kwargs):
        color = kwargs.pop('color', discord.Color.yellow())
        embed = discord.Embed(description=content, color=color, **kwargs)
        await self.send(embed=embed)
