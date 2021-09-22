import discord
from discord.ext import commands
from asyncio import sleep


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(Utility(bot))
