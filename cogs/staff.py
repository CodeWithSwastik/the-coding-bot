import discord
from discord.ext import commands

from cogs.moderation import is_staff
from utils.views import Confirm

from datetime import datetime

class Staff(commands.Cog):
    # Add staff checks :yeah:
    def __init__(self, bot):
        self.bot = bot
        self.on_patrol_id = 726441123966484600
        self.afks = {}
        self.last_cas = datetime.now()

    @property
    def on_patrol(self):
        return self.bot.tca.get_role(self.on_patrol_id)

    @property
    def on_patrol_helper(self):
        return self.bot.tca.get_role(760844827804958730)

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
            await message.reply(embed=embed, delete_after=3)

        mentions = message.mentions
        for i in mentions:
            if self.is_staff(i) and self.is_afk(i):
                embed = discord.Embed(color=discord.Color.yellow())
                embed.description = f'{i.mention} is currently AFK. **{self.afks.get(i.id,"")}**'
                await message.reply(embed=embed, delete_after=3)



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
        msg = await ctx.reply(content = '\u200b', embed=embed, view=confirm_view)

        result = await confirm_view.wait()
        if result or not confirm_view.value:
            # User selected cancel or timeout
            return await msg.delete()

        self.last_cas = datetime.now()
        await ctx.reply('I have called all staff. Please be patient.')
        await self.staff_chat.send(f'{self.on_patrol.mention}, {ctx.author.mention} has called all staff in {ctx.channel.mention}. Reason: {reason}')
        

    @commands.command()
    async def staff(self, ctx, who='patrol'):
        who = who.lower()
        if who == 'patrol':
            title = f"On Patrol Staff {self.bot.get_custom_emoji('policesiren')}"
            members = self.on_patrol.members
        elif who == 'all':
            title = f"All Staff"
            members = self.bot.tca.get_role(795145820210462771).members            

        embed = discord.Embed(
            title=title,
            color=discord.Color.yellow(),
        )
        online, dnd, idle, offline = self.bot.get_custom_emojis("online", "dnd", "idle", "offline")
        mapping = {
            discord.Status.online : (online, 4), 
            discord.Status.dnd    : (dnd, 3),
            discord.Status.idle   : (idle, 2),
            discord.Status.offline: (offline, 1),
        }

        members = sorted(members, key=lambda m: mapping[m.status][1], reverse=True)
        embed.description = '\n'.join([f'{mapping[m.status][0]} {m.mention}' for m in members])
        await ctx.send(embed=embed)

    @commands.command(name='update-staff-list')
    @commands.has_permissions(administrator=True)
    async def update_staff_list(self, ctx):
        staff_list_channel = self.bot.tca.get_channel(765066298299383809)
        mod_roles = [
            681895373454835749,
            838634262693412875,
            725899526350831616,
            795136568805294097,
            729530191109554237,
            681895900070543411,
            729537643951554583,
        ]
        embed = discord.Embed(title='**Staff List**', color=0x2F3136)
        embed.description = ''
        for r in mod_roles:
            r = self.bot.tca.get_role(r)
            valid_members = []
            for m in r.members:
                admin = m.top_role.name == 'Admin Perms' and r.name == 'Admin'
                if m.top_role == r or admin:
                    valid_members.append(m)

            embed.description += f"{r.mention} | **{len(valid_members)}** \n"

            for m in valid_members:
                embed.description += f"> `{m.id}` {m.mention}\n"
            embed.description += '\n'
        await staff_list_channel.purge(limit=1)
        await staff_list_channel.send(embed=embed)
        await ctx.embed(f"Done {self.bot.get_custom_emoji('greentick')}")

    @commands.command(name='update-helper-list')
    @commands.has_permissions(administrator=True)
    async def update_helper_list(self, ctx):
        staff_list_channel = self.bot.tca.get_channel(849559721127575562)
        mod_roles = [
            783909939311280129,
            726650418444107869,
        ]
        embed = discord.Embed(title='**Helper List**', color=0x2F3136)
        embed.description = ''
        for r in mod_roles:
            r = self.bot.tca.get_role(r)
            valid_members = []
            for m in r.members:
                if m.top_role == r:
                    valid_members.append(m)

            embed.description += f"{r.mention} | **{len(valid_members)}** \n"

            for m in valid_members:
                embed.description += f"> `{m.id}` {m.mention}\n"
            embed.description += '\n'
        await staff_list_channel.purge(limit=1)
        await staff_list_channel.send(embed=embed)
        await ctx.embed(f"Done {self.bot.get_custom_emoji('greentick')}")

    @commands.command()
    @commands.has_role("Official Helper")
    async def onpatrol(self, ctx):
        await ctx.author.add_roles(self.on_patrol_helper)
        await ctx.send("You are now on patrol.")

    @commands.command()
    @commands.has_role("Official Helper")
    async def offpatrol(self, ctx):
        await ctx.author.remove_roles(self.on_patrol_helper)
        await ctx.send("You are now off patrol.")

def setup(bot):
    bot.add_cog(Staff(bot))
