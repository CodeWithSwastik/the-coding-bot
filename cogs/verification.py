import discord
from discord.ext import commands

from cogs.moderation import is_staff

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.member_role_id = 744403871262179430

    @property
    def member_role(self):
        return self.bot.tca.get_role(self.member_role_id)

    @commands.command()
    @is_staff()
    async def verify(self, ctx, member: discord.Member):
        await member.add_roles(self.member_role, reason=f'Manually verified by {ctx.author.name}.')
        await ctx.embed(f'{member.mention} has been verified.')

def setup(bot):
    bot.add_cog(Verification(bot))
