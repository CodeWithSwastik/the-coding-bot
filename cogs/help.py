import discord
import asyncio
from discord.ext import commands

# >jsk py
# ```
# embed = discord.Embed(title='Private Help', description = 'Press the button below for private help.\nNote: This might not work as it is being tested at the moment.', color = discord.Color.yellow())
# button = discord.ui.Button(label='Help!', emoji='🙋', custom_id='help_button', style=discord.ButtonStyle.blurple)
# view = discord.ui.View()
# view.add_item(button)
# await ctx.send(embed=embed, view=view)
# ```


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.private_help_channel = 889149110588960838
    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.channel_id == self.private_help_channel:
            if interaction.data.get("custom_id", "") == "help_button":
                if (
                    thread := self.find_existing_thread(
                        interaction.channel, interaction.user.id
                    )
                ) :
                    await interaction.response.send_message(
                        f"You already have a private help channel: {thread.mention}",
                        ephemeral=True,
                    )

                await interaction.response.send_message("Hello", ephemeral=True)
                thread = await interaction.channel.create_thread(
                    name=f"help {interaction.user.name} {interaction.user.id}"
                )
                await thread.send(
                    f"{interaction.user.mention} needs help! <@&760844827804958730>",
                    allowed_mentions=discord.AllowedMentions.all(),
                )

    def find_existing_thread(self, channel, id):
        for thread in channel.threads:
            if str(id) in thread.name:
                return thread
        return None

    @commands.command()
    async def close(self, ctx):
        if str(ctx.channel.type) == 'private_thread' and ctx.channel.parent.id == self.private_help_channel:
            await ctx.send('This channel will be deleted soon. Hope you are happy with the help.')
            await asyncio.sleep(5)
            await ctx.channel.delete()
        else:
            await ctx.embed('This command can only be used to close help threads.')


def setup(bot):
    bot.add_cog(Help(bot))
