import discord
from discord import user
from discord.ext import commands, tasks

import string
import random
import datetime
from durations import Duration

from utils.models import ModAction
from utils.database import Database

def is_staff():
    return commands.has_any_role("Staff", "Trainee Mod")  # Staff + Trainee

class ActionType:
    """Stuff associated with mod actions"""

    default_warn_duration = 2592000 # seconds
    default_mute_duration = 3600 # seconds
    default_ban_duration = None # Infinite


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

        self.rules = []
        self.faqs = []

        self.setup.start()

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
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str):
        if reason.split()[0].endswith(("h", "hr", "m", "min", "s", "sec", "d", "days", "month")):
            duration = Duration(reason.split()[0]).to_seconds()
            reason = reason.replace(reason.split()[0], "")

        else:
            duration = ActionType.default_warn_duration

        new_warn = ModAction(
            user_id = member.id,
            mod_id = ctx.author.id,
            action = "warn",
            reason = reason,
            duration = duration
        )

        self.db.modutils.modaction_insert(new_warn)

        delta = datetime.datetime.now()+datetime.timedelta(seconds=duration)
        await ctx.send(embed=discord.Embed(
            title=f":warning: {member.name} has been warned!",
            description=f"**Reason:** `{reason}` \n**Warned By:** {ctx.author.mention} \n**Expires on:** `{delta.date()}`",
            color=discord.Color.orange(),
            timestamp=datetime.datetime.now()
        ).set_footer(text="Open a ticket to appeal."))

    @commands.command()
    @is_staff()
    async def modlogs(self, ctx: commands.Context, user: discord.Member = None):
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
            expiry = date+datetime.timedelta(seconds=case.duration)
            delta = expiry-date

            embed.add_field(
                name=f"Case {case_id} | {case.action}",
                value=f"Reason: `{case.reason}` \nModerator: {mod.mention} ({mod.name}) \nDate: `{date.date()}` \nDuration: `{delta.days} days` \nExpires on: `{expiry.date()}`",
                inline=False
            )
        
        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Moderation(bot))
