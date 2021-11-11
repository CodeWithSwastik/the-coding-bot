import asyncio
import discord
from discord.ext import commands, tasks
import datetime


class Bump(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.disboard_id = 302050872383242240
        self.reminder = None

        self.check_bump_reminder.start()

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot:
            return
         
        if msg.content != "!d bump":
            return

        try:
            message = await self.bot.wait_for("message", check = lambda m: m.author.id == self.disboard_id and msg.channel == m.channel, timeout=20)
        except asyncio.TimeoutError:
            return
        data = message.embeds[0].to_dict()
        #print(data["color"]) # 15420513 -> Red -> Fail

        if data["color"] == 15420513:
            minutes = int(data["description"][42:].split()[0])
            self.reminder = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
            await msg.reply(f"I will remind you guys in <#743817386792058971> after {minutes} minutes")
        else:
            self.reminder = discord.utils.utcnow() + datetime.timedelta(minutes=120)
            await msg.reply(f"I will remind you guys in <#743817386792058971> after 2 hours")

    @tasks.loop(minutes=2)
    async def check_bump_reminder(self):
        if self.reminder:
            if (discord.utils.utcnow() - self.reminder).total_seconds() > 0:
                await self.bot.get_channel(743817386792058971).send("You can bump the server! Type !d bump in <#682157382062964781>")


def setup(bot):
    bot.add_cog(Bump(bot))
