import discord
from discord.ext import commands

# I think I should add a system that auto sets slowmode depending on the message frequency
class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
def setup(bot):
    bot.add_cog(Utility(bot))
