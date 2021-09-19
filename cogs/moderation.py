import discord
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(aliases=['sm'])
    @commands.has_any_role(729537643951554583, 795145820210462771) # Staff + Trainee
    async def slowmode(self, ctx, time = None):
        if time is None:
            await ctx.send(f'Current slowmode is `{ctx.channel.slowmode_delay}` seconds')
            return
        elif time.startswith('+') or time.startswith('-'):
            new_delay = ctx.channel.slowmode_delay + int(time)
        else:
            new_delay = int(time)
        await ctx.channel.edit(slowmode_delay = new_delay)

        await ctx.send(f'Set slowmode to `{new_delay}` seconds')


def setup(bot):
    bot.add_cog(Moderation(bot))
