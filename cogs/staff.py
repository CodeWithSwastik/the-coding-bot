import discord
from discord.ext import commands

from cogs.moderation import is_staff
from utils.views import Confirm

from datetime import datetime

class Staff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.on_patrol_id = 726441123966484600
        self.afks = {}
        self.last_cas = datetime.now()

    @property
    def on_patrol(self):
        return self.bot.tca.get_role(self.on_patrol_id)

    @property
    def staff_chat(self):
        return self.bot.tca.get_channel(735864475994816576)

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
        await ctx.author.remove_roles(self.on_patrol)
        try:
            await ctx.author.edit(nick=f'[AFK] {ctx.author.display_name}')
        except discord.Forbidden:
            pass
        self.afks[ctx.author.id] = reason
        embed = discord.Embed(
            description=f'{ctx.author.mention}, you are now AFK. **{self.afk_response(reason)}**', 
            color=discord.Color.yellow()
        )
        await ctx.reply(embed=embed)

    def is_staff(self, member):
        staff_roles = [795145820210462771, 729537643951554583]
        return (
            hasattr(member, 'roles') and 
            any([c in (r.id for r in member.roles) for c in staff_roles])
        )

    def is_afk(self, member):
        return not self.on_patrol in member.roles

    def afk_response(self, reason):
        mapping = {
            'sleep': 'Good night! 😴',
            'study': 'Good luck with your studies!',
            'school': 'Good luck at school!',
            'work': 'Good luck with work!'
        }
        return mapping.get(reason.lower(), reason)

    async def unafk(self, member):
        await member.add_roles(self.on_patrol)
        try:
            await member.edit(nick=member.display_name.replace('[AFK] ', ''))
        except discord.Forbidden:
            pass        
        return self.afks.pop(member.id, '')

    @commands.command(name='cas')
    async def call_all_staff(self, ctx, *, reason):
        if (time :=(datetime.now() - self.last_cas).total_seconds()//60) < 15:
            return await ctx.embed(
                f'Someone has called all staff recently. \nPlease wait {round(15-time)} minutes before calling all staff again.'
            )
        
        embed = discord.Embed(color=discord.Color.red())
        embed.title = '**Are you sure that you want to call all staff?**'
        embed.description = 'If you abuse this you will be punished severely.'

        confirm_view = Confirm(ctx.author)
        msg = await ctx.reply(content = 'e', embed=embed, view=confirm_view)

        await confirm_view.wait()
        if not confirm_view.value:
            # User selected cancel
            return await msg.delete()

        self.last_cas = datetime.now()
        await ctx.reply('I have called all staff. Please be patient.')
        await self.staff_chat.send(f'{self.on_patrol.mention}, {ctx.author.mention} has called all staff in {ctx.channel.mention}. Reason: {reason}')
        
        
def setup(bot):
    bot.add_cog(Staff(bot))
