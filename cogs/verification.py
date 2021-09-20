import discord
from discord.ext import commands

from cogs.moderation import is_staff
from captcha.image import ImageCaptcha

import random  
import string

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.member_role_id = 744403871262179430
        self.captcha = ImageCaptcha(width = 280, height = 90)

    @property
    def member_role(self):
        return self.bot.tca.get_role(self.member_role_id)

    @commands.command()
    @is_staff()
    async def verify(self, ctx, member: discord.Member):
        await member.add_roles(
            self.member_role, reason=f"Manually verified by {ctx.author.name}."
        )
        await ctx.embed(f"{member.mention} has been verified.")

    @commands.command()
    @is_staff()
    async def sus(self, ctx, member: discord.Member):
        await ctx.embed(f'{self.calculate_suspicion(member)} %')

    async def create_captcha(self):

        captcha_text = ''.join(random.choices(string.digits, k=6))
        
        data = await self.bot.run_async(self.captcha.generate, captcha_text)
        return discord.File(data, filename="captcha.png")

    def calculate_suspicion(self, member: discord.Member) -> float:
        sus = 0
        if member.avatar is None: 
            # default pfp
            sus += 10
        if not any(dict(member.public_flags).values()):
            # no badges
            sus += 10

        # time joined - created
        delta = member.joined_at - member.created_at
        hours = delta.days * 24 + delta.seconds/3600
        if delta.days == 0:
            sus += (86400-delta.seconds)*80/(86400)
        elif hours < 24*7*4: # 1 month
            sus += (24*7*2-hours)*40/(24*7*2)

        return round(sus)

def setup(bot):
    bot.add_cog(Verification(bot))
