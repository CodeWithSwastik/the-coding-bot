import discord
from discord.ext import commands

class PrivateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command(self, ctx):
        if not await self.bot.is_owner(ctx.author):
            return

def setup(bot):
    bot.add_cog(PrivateCog(bot))