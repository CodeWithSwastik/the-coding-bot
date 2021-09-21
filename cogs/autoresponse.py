import discord
from discord.ext import commands, tasks
import random

class Autoresponse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.general_channel = 743817386792058971

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot or msg.channel.id != self.general_channel:
            return
        
        if random.randint(1,1000) == 1:
            embed = discord.Embed(description=self.get_info_message(), color=discord.Color.random())
            await msg.channel.send(embed=embed)

    def get_info_message(self):
        info = [
            #"You can suggest new cards like these to be added! Just DM me to send a modmail to us.",
            f"We currently have {len(self.bot.tca.members)} people in {self.bot.tca.name}!",
            "If you want to be pinged during certain events, go visit <#806909970482069556> for more information!",
            "If you win an event, you might get a custom role with a custom role icon!",
            "If a message gets 5 stars it'll show up in the <#763039747190030407>",
            "You can support the server for free by voting for us on [disboard](https://disboard.org/server/681882711945641997) or typing `!d bump` in <#682157382062964781>"
        ]
        return f'{self.bot.get_custom_emoji("info")}  {random.choice(info)}'

def setup(bot):
    bot.add_cog(Autoresponse(bot))
