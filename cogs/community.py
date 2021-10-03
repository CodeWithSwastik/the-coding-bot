import discord
from discord.ext import commands


class Community(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.creations_channel = 887708887308988487
        
        self.code_bin_channel = 892737692746539008
        

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return 
        if message.channel.id == self.creations_channel:
            if 'http' not in message.content and len(message.attachments) == 0:
                await message.reply(
                    "Your post is not in the correct format so it has been deleted.\n"
                    "Note: This channel isn't meant for conversing, please use the <#892735998285471754> channel instead.", 
                    delete_after=10
                )
                await message.delete()
        if message.channel.id == self.code_bin_channel:
            if '```' not in message.content:
                await message.reply(
                    "Your post is not in the correct format so it has been deleted.\n"
                    "Note: This channel isn't meant for conversing, please use the <#892735998285471754> channel instead.", 
                    delete_after=10
                )
                await message.delete()


def setup(bot):
    bot.add_cog(Community(bot))