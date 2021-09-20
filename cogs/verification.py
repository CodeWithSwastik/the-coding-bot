import discord
from discord.ext import commands

from cogs.moderation import is_staff
from captcha.image import ImageCaptcha

import random  
import string
import asyncio

# >jsk py
# ```
# embed = discord.Embed(title=f'Welcome to The Coding Academy {bot.get_custom_emoji("Helloooo")}', description = 'Press the button below to be verified.', color = discord.Color(0x2F3136))
# embed.set_footer(text='If you face any problems with the verification DM one of the moderators!')
# button = discord.ui.Button(emoji=bot.get_custom_emoji('greentick'), custom_id='verify_button', style=discord.ButtonStyle.green)
# view = discord.ui.View()
# view.add_item(button)
# await ctx.send(embed=embed, view=view)
# ```

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.member_role_id = 744403871262179430
        self.captcha = ImageCaptcha(width = 280, height = 90)
        self.verify_channel = 889351320371339334

    @property
    def member_role(self):
        return self.bot.tca.get_role(self.member_role_id)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.channel_id != self.verify_channel:
            return

        if interaction.data.get("custom_id", "") == "verify_button":
            greentick = self.bot.get_custom_emoji('greentick')
            sus = self.calculate_suspicion(interaction.user)
            if sus < 50:
                await interaction.response.send_message(
                    f"You have been verified {greentick}",
                    ephemeral=True,
                )
                method='bot'
            else:
                await interaction.response.send_message(
                    "Please solve the captcha that I will DM you in order to be verified.",
                    ephemeral=True,
                )
                captcha, answer = await self.create_captcha()
                try:
                    embed = discord.Embed(title='Welcome to The Coding academy!', description='Please solve the captcha and send it here.\n**Your captcha**:', color=0x2F3136) 
                    embed.set_image(url='attachment://captcha.png')
                    await interaction.user.send(embed=embed, file=captcha)
                except discord.Forbidden:
                    return await interaction.followup.send(
                        "I couldn't send you a DM please open your DMs and re-click the verify button!",
                        ephemeral=True,
                    )

                def check(m):
                    return interaction.user.dm_channel.id == m.channel.id   
                try:
                    response = await self.bot.wait_for('message', check=check, timeout=60)
                except asyncio.TimeoutError:
                    return await interaction.user.send('Timeout. You failed to respond. Please re-click the verification button.')
                if response.content == answer:
                    embed = discord.Embed(title=f'Verification sucessful {greentick}', description='You have been verified in The Coding Academy.', color=discord.Color.green()) 
                    await interaction.user.send(embed=embed)
                else:
                    return await interaction.user.send('Incorrect captcha. Please re-click the verification button.')
                method = 'captcha'
            await interaction.user.add_roles(
                self.member_role, reason=f"Verified by {method}."
            )
                


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
        return discord.File(data, filename="captcha.png"), captcha_text

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
