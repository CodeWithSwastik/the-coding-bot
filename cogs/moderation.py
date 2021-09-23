from typing import List
import discord
from discord.ext import commands, tasks
from discord.utils import format_dt

import string
import random
import datetime
from durations import Duration
import re
from io import BytesIO

from sqlalchemy.orm.exc import NoResultFound

from utils.models import ModAction, LogModel
from utils.database import Database

def is_staff():
    return commands.has_any_role("Staff", "Trainee Mod")  # Staff + Trainee

def is_higher(author: discord.Member, target: discord.Member):
    if author.top_role.position <= target.top_role.position:
        raise commands.CheckFailure('You do not have permissions to interact with that user')

# Sending logs
async def send_logs(self, case: ModAction, action=None, reason=None, send_duration=True):
    if not action:
        action = case.action
    if not reason:
        reason = case.reason
    
    expiry = datetime.datetime.now()+datetime.timedelta(seconds=case.duration) if send_duration else None # For kicks and bans

    log = LogModel(
            case_id = case.case_id, # Manually setting case_id after inserting to db since it doesnt return the generated one.
            user_id = case.user_id,
            mod_id = case.mod_id,
            action = action,
            reason = reason,
            expiry = expiry
        )

    user = self.bot.tca.get_member(log.user_id)
    mod = self.bot.tca.get_member(log.mod_id)
    expiry_ts = format_dt(log.expiry) if expiry else None
    embed = discord.Embed(
        title = f"{log.action} | case {log.case_id}",
        description=f"**Offender:** {user.name} ({user.id}) \n**Reason:** {log.reason} \n**Moderator:** {mod.mention} \n**Expires on:** {expiry_ts}",
        color=discord.Color.orange(),
        timestamp=datetime.datetime.now()
    )
    await self.bot.logs.send(embed=embed)

class ActionType:
    """Stuff associated with mod actions"""

    default_warn_duration = 2592000 # seconds
    default_mute_duration = 3600 # seconds
    default_ban_duration = 999999999 # Infinite
    default_kick_duration = 999999999 # Need this cuz duration field cant be empty


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

        self.rules = []
        self.faqs = []

        self.setup.start()
        self.loop_database.start()

    @property
    def mute_role(self):
        return self.bot.tca.get_role(766469426429820949)

    @tasks.loop(count=1)
    async def setup(self):
        rules_channel = await self.bot.fetch_channel(681887262136598589)
        faq_channel = await self.bot.fetch_channel(725960895481774084)

        raw_rules = (await rules_channel.fetch_message(790896473231196170)).content
        raw_rules += (
            "\n\n" + (await rules_channel.fetch_message(790896673991557120)).content
        )
        self.rules = self.parse_rules(raw_rules)[:-1]

        raw_faqs = (await faq_channel.fetch_message(794786168461066241)).content
        self.faqs = self.parse_rules(raw_faqs)

    @setup.before_loop
    async def before_setup(self):
        await self.bot.wait_until_ready()

    def parse_rules(self, text: str) -> list:
        return text.split("\n\n")

    @tasks.loop(minutes=1)
    async def loop_database(self):
        data: List[ModAction] = self.db.modutils.modaction_list_all()
        for case in data:
            delta = case.date-datetime.datetime.now()
            if delta <= datetime.timedelta(seconds=1):        
                try:
                    if case.action == "mute":
                        user: discord.Member = self.bot.tca.get_member(case.user_id)
                        if self.mute_role in user.roles:
                            await user.remove_roles(self.mute_role)
                            try:
                                await user.send(f"You have been unmuted. Reason: Mute expired!")
                            except:
                                pass

                    if case.action == "ban":
                        user: discord.Member = self.bot.tca.get_member(case.user_id)
                        try:
                            await self.bot.tca.fetch_ban(user)
                            await self.bot.tca.unban(user, reason="Ban expired")
                        except:
                            pass
                    self.db.modutils.modaction_delete(case.case_id)
                    await send_logs(self, case=case, action="case delete", reason=f"{case.action} expired", send_duration=False)
                    
                except:
                    pass


    @commands.command(aliases=["sm"])
    @is_staff()
    async def slowmode(self, ctx, time=None):
        if time is None:
            await ctx.embed(
                f"Current slowmode is `{ctx.channel.slowmode_delay}` seconds"
            )
            return
        elif time.startswith("+") or time.startswith("-"):
            new_delay = ctx.channel.slowmode_delay + int(time)
        else:
            new_delay = int(time)
        if new_delay > 21600:
            return await ctx.send("Slowmode can't be more than 21600 seconds.")
        await ctx.channel.edit(slowmode_delay=new_delay)
        await ctx.embed(f"Set slowmode to `{new_delay}` seconds")

    @slowmode.error
    async def sm_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.embed(str(error.original))

    @commands.command()
    @is_staff()
    async def rule(self, ctx, number: int):
        if number < len(self.rules) and number > 0:
            rule = self.rules[number]
            q = rule.split("\n")[0]
            a = "\n".join(rule.split("\n")[1:])
            converter = commands.clean_content(fix_channel_mentions=True)
            embed = discord.Embed(
                title=await converter.convert(ctx, q),
                description=a,
                color=discord.Color.yellow(),
            )
            await ctx.send(embed=embed)
        else:
            await ctx.embed("Invalid rule number.")

    @commands.command()
    @is_staff()
    async def faq(self, ctx, number: int):
        if number <= len(self.faqs) and number > 0:
            q = self.faqs[number - 1].split("\n")[0]
            a = "\n".join(self.faqs[number - 1].split("\n")[1:])
            converter = commands.clean_content(fix_channel_mentions=True)
            embed = discord.Embed(
                title=await converter.convert(ctx, q),
                description=a,
                color=discord.Color.yellow(),
            )
            await ctx.send(embed=embed)
        else:
            await ctx.embed("Invalid faq number.")

    @commands.command()
    @is_staff()
    async def nick(self, ctx, member: discord.Member, *, nickname: str = None):
        await self.moderate_nick(member, nickname)
        await ctx.embed(f"Changed {member.mention}'s nickname")

    async def moderate_nick(self, member, nickname=None):
        if nickname is None:
            nickname = 'Moderated Nickname ' + ''.join(random.choices(string.ascii_lowercase, k=8))
        await member.edit(nick=nickname)

    @commands.command()
    @is_staff()
    async def revive(self, ctx):
        # TODO
        await ctx.send("https://tenor.com/8coi.gif")


    @commands.command()
    @is_staff()
    async def warn(self, ctx: commands.Context, member: discord.Member, *, raw: str):

        is_higher(ctx.author, member) # Checking is user is not lower in position

        if re.findall("\d[hmsd]",raw.split()[0]):
            duration = Duration(raw.split()[0]).to_seconds()
            reason = raw.replace(raw.split()[0], "")

        else:
            reason=raw
            duration = ActionType.default_warn_duration

        new_warn = ModAction(
            user_id = member.id,
            mod_id = ctx.author.id,
            action = "warn",
            reason = reason,
            duration = duration
        )

        self.db.modutils.modaction_insert(new_warn)

        case = self.db.modutils.modaction_list_user(member.id)[-1]  #Pulling the case from db to get additional info like id and logs
        case_id = case.case_id

        await send_logs(self, case=case)

        delta_ts = format_dt(datetime.datetime.now()+datetime.timedelta(seconds=duration))

        try:
            await member.send(embed=discord.Embed(
                title=f":warning: You have been warned!",
                description=f"**Case ID:** {case_id} \n**Reason:** {reason} \n**Expires on:** {delta_ts}",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now()
            ).set_footer(text="Open a ticket to appeal."))
        except:
            pass

        await ctx.embed(f":warning: Warned `{member.name}#{member.discriminator}`")

    # Mute command
    @commands.command()
    async def mute(self, ctx: commands.Context, member: discord.Member, *, raw: str="No reason given."):

        # TODO: Role cache
        is_higher(ctx.author, member) # Checking is user is not lower in position

        if re.findall("\d[hmsd]",raw.split()[0]):
            duration = Duration(raw.split()[0]).to_seconds()
            reason = raw.replace(raw.split()[0], "")

        else:
            reason=raw
            duration = ActionType.default_mute_duration

        new_mute = ModAction(
            user_id = member.id,
            mod_id = ctx.author.id,
            action = "mute",
            reason = reason,
            duration = duration
        )

        self.db.modutils.modaction_insert(new_mute)
        
        await member.add_roles(self.mute_role)

        case = self.db.modutils.modaction_list_user(member.id)[-1]    
        await send_logs(self, case=case)

        delta_ts = format_dt(datetime.datetime.now()+datetime.timedelta(seconds=duration))
        try:
            await member.send(embed=discord.Embed(
                title=f":mute: You have been muted!",
                description=f"**Case ID:** {case.case_id} \n**Reason:** {reason} \n**Expires on:** {delta_ts}",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now()
            ).set_footer(text="Open a ticket to appeal."))
        except:
            pass

        await ctx.embed(f":mute: Muted `{member.name}#{member.discriminator}`")

    # Kick command
    @commands.command()
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason="No reason provided"):
        is_higher(ctx.author, member) # Checking is user is not lower in position

        duration = ActionType.default_kick_duration # Need this cuz required int field

        new_kick = ModAction(
            user_id = member.id,
            mod_id = ctx.author.id,
            action = "kick",
            reason = reason,
            duration = duration
        )

        self.db.modutils.modaction_insert(new_kick)
        case = self.db.modutils.modaction_list_user(member.id)[-1]    
        await send_logs(self, case=case, send_duration=False)

        try:
            await member.send(embed=discord.Embed(
                title=f":boot: You have been kicked!",
                description=f"**Case ID:** {case.case_id} \n**Reason:** {reason}",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now()
            ).set_footer(text="Open a ticket to appeal."))
        except:
            pass

        await ctx.embed(f":boot: Kicked `{member.name}#{member.discriminator}`")
        await ctx.guild.kick(member, reason=reason)

    # Ban command
    @commands.command()
    async def ban(self, ctx:commands.Context, member: discord.Member, *, raw: str = "No reason provided"):
        is_higher(ctx.author, member) # Checking is user is not lower in position

        if re.findall("\d[hmsd]",raw.split()[0]):
            duration = Duration(raw.split()[0]).to_seconds()
            reason = raw.replace(raw.split()[0], "")

        else:
            reason=raw
            duration = ActionType.default_ban_duration

        new_ban = ModAction(
            user_id = member.id,
            mod_id = ctx.author.id,
            action = "ban",
            reason = reason,
            duration = duration
        )

        self.db.modutils.modaction_insert(new_ban)
        case = self.db.modutils.modaction_list_user(member.id)[-1]  

        send_duration = case.duration != 999999999

        await send_logs(self, case=case, send_duration=send_duration)
        
        try:
            await member.send(embed=discord.Embed(
                title=f":boot: You have been banned!",
                description=f"**Case ID:** {case.case_id} \n**Reason:** {reason}",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now()
            ).set_footer())
        except:
            pass

        await ctx.embed(f":boot: Banned `{member.name}#{member.discriminator}`")
        await ctx.guild.ban(member, reason=reason)

    @commands.command()
    @commands.has_any_role("Head Moderator", "Admin", "Admin Perms","Head Admin", "Owner")
    async def unban(self, ctx:commands.Context, member: discord.User, *, reason="No reason provided"):
        try:
            await ctx.guild.fetch_ban(member)
        except discord.NotFound:
            return await ctx.send('That user is not banned')
        
        # case = self.db.modutils.modaction_list_user(member.id)[-1] 
        # self.db.modutils.modaction_delete(case.case_id)
        # await send_logs(self, case, action="unban", send_duration=False)
        await ctx.guild.unban(member, reason=reason)
        await ctx.embed(f":white_check_mark: Unbanned `{member.name}#{member.discriminator}`")

    @commands.command()
    @commands.has_any_role("Head Moderator", "Admin", "Admin Perms","Head Admin", "Owner")
    async def delcase(self, ctx:commands.Context, case_id: int, *, reason = "No reason given"):
        case = self.db.modutils.modaction_fetch(case_id=case_id)
        try:
            self.db.modutils.modaction_delete(case_id=case_id)
        except:
            pass

        if not case:
            return await ctx.send("Invalid Case ID...")

        await ctx.send(":white_check_mark:")
        
        await send_logs(self, case=case, action="case delete", reason=reason)
    
    @commands.command(aliases=["clw", "clearall"])
    @commands.has_guild_permissions(administrator=True)
    async def clearmodlogs(self, ctx: commands.Context, member: discord.Member):
        cases = self.db.modutils.modaction_list_user(member.id)
        for case in cases:
            self.db.modutils.modaction_delete(case.case_id)
            
        await ctx.send(":white_check_mark:")

    @commands.command()
    @is_staff()
    async def modlogs(self, ctx: commands.Context, user: discord.User = None):
        infractions = self.db.modutils.modaction_list_user(user.id)
        if len(infractions) == 0:
            return await ctx.send("Member has no modlogs...")
        embed = discord.Embed(
            title=f":pencil: Modlogs | {user.name} ({user.id})",
            color = discord.Color.random()
        )
        
        for case in infractions:

            case_id = case.case_id
            mod = ctx.guild.get_member(case.mod_id)
            date = case.date
            date_ts = format_dt(date)
            expiry = date+datetime.timedelta(seconds=case.duration)
            expiry_ts = format_dt(expiry)
            delta = format_dt(expiry, style="R")
            

            embed.add_field(
                name=f"Case {case_id} | {case.action}",
                value=f"Reason: {case.reason} \nModerator: {mod.mention} ({mod.name}) \nDate: {date_ts} \nDuration: {delta} \nExpires on: {expiry_ts}",
                inline=False
            )
        
        await ctx.send(embed=embed)

    # Evidence command
    @commands.command()
    @is_staff()
    async def evidence(self, ctx: commands.Context, case_id: int, *, proof=None):
        if not ctx.message.attachments:
            return await ctx.send("Please attach evidence.")
        
        files = [discord.File(BytesIO(await attachment.read()), filename=attachment.filename) for attachment in ctx.message.attachments]

        
        case = self.db.modutils.modaction_fetch(case_id)
        if not case:
            return await ctx.send("Invalid Case ID...")

        user = ctx.guild.get_member(case.user_id)
        mod = ctx.guild.get_member(case.mod_id)

        if ctx.author.id != mod.id:
            return await ctx.send("Stop posting evidence for others, let them do it lol...")

        embed = discord.Embed(
            title=f"{user.name} ({user.id})",
            description=f"**Case ID:** {case.case_id} \n**Mod:** {mod.mention} \n**Reason:** {case.reason} \n**Proof:** {proof}",
            color=discord.Color.yellow(),
            timestamp=datetime.datetime.now()
        )
        evidence_ch: discord.TextChannel = self.bot.tca.get_channel(760186182343852032)

        await evidence_ch.send(embed=embed)
        await evidence_ch.send(files=files)
        await ctx.send(":white_check_mark: Evidence sent successfully.")



def setup(bot):
    bot.add_cog(Moderation(bot))
