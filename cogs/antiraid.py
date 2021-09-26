import discord, asyncio
from discord.ext import commands


class AntiRaid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @property
    def muted_role(self):
        return discord.utils.get(self.bot.tca.roles, name='Muted')

    @commands.Cog.listener()
    async def on_message(self, message):
        if len(message.raw_mentions) > 7:
            roles = message.author.roles[1:]
            await message.author.remove_roles(*roles)
            await message.author.add_roles(self.muted_role)
            await message.reply('I muted this possible raider for 3 minutes, @Staff can see what to do with them.', allowed_mentions=discord.AllowedMentions.all())
            await asyncio.sleep(60*3)
            await message.author.remove_roles(self.muted_role)
            await message.author.add_roles(*roles)            

def setup(bot):
    bot.add_cog(AntiRaid(bot))

