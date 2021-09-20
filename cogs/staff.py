import discord
from discord.ext import commands

from cogs.moderation import is_staff

class Staff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cas_id = 726441123966484600
        self.afks = {}

    @property
    def cas(self):
        return self.bot.tca.get_role(self.cas_id)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or str(message.channel.type)=='dm':
            return

        if message.content.startswith('>afk'):
            return
        

        if self.is_staff(message.author) and self.is_afk(message.author):
            await self.unafk(message.author)
            salute = self.bot.get_custom_emoji('salute')
            embed = discord.Embed(color=discord.Color.yellow())
            embed.description = f'Welcome back {salute} I removed your AFK.'
            await message.reply(embed=embed)

        mentions = message.mentions
        for i in mentions:
            if self.is_staff(i) and self.is_afk(i):
                embed = discord.Embed(color=discord.Color.yellow())
                embed.description = f'{i.mention} is currently AFK. **{self.afks.get(i.id,"")}**'
                await message.reply(embed=embed)



    @commands.command()
    @is_staff()
    async def afk(self, ctx, *, reason = 'AFK'):
        embed = discord.Embed(description=f'{ctx.author.mention}, you are now AFK. **{reason}**', color=discord.Color.yellow())
        await ctx.author.remove_roles(self.cas)
        try:
            await ctx.author.edit(nick=f'[AFK] {ctx.author.display_name}')
        except discord.Forbidden:
            pass
        self.afks[ctx.author.id] = reason
        await ctx.reply(embed=embed)

    def is_staff(self, member):
        staff_roles = [795145820210462771, 729537643951554583]
        return (
            hasattr(member, 'roles') and 
            any([c in (r.id for r in member.roles) for c in staff_roles])
        )

    def is_afk(self, member):
        return not self.cas in member.roles

    async def unafk(self, member):
        await member.add_roles(self.cas)
        try:
            await member.edit(nick=member.display_name.replace('[AFK] ', ''))
        except discord.Forbidden:
            pass        
        return self.afks.pop(member.id, '')


def setup(bot):
    bot.add_cog(Staff(bot))
