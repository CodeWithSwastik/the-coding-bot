import discord
import asyncio
from discord.ext import commands
from utils.views import Confirm

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
        if interaction.channel_id != self.private_help_channel:
            return

        if interaction.data.get("custom_id", "") == "help_button_test":
            if (
                thread := self.find_existing_thread(
                    interaction.channel, interaction.user.id
                )
            ):
                return await interaction.response.send_message(
                    f"You already have a private help channel: {thread.mention}",
                    ephemeral=True,
                )

            await self.handle_thread_setup(interaction)


    def find_existing_thread(self, channel, id):
        for thread in channel.threads:
            if str(id) in thread.name and not thread.archived:
                return thread
        return None
    
    async def handle_thread_setup(self, interaction):
        language_select = discord.ui.View()
        language_select.add_item(LanguageSelect(self.bot))
        await interaction.response.send_message(
            "Select the language you need help with.", 
            view=language_select, 
            ephemeral=True
        )
        res = await language_select.wait()
        if res:
            return await interaction.edit_original_message(
                content="You didn't select a language on time.", 
            )            


        confirm = Confirm(interaction.user)
        await interaction.edit_original_message(
            content=f"Is this correct? You need help from: <@&{language_select.value}>", 
            view=confirm
        )                    
        await confirm.wait()
        if not confirm.value:
            # User selected cancel
            return await interaction.edit_original_message(
                content="You have cancelled this, press the button again to create a new one.", 
                view=None
            )             

        thread = await interaction.channel.create_thread(
            name=f"help {interaction.user.name} {interaction.user.id}",
        )
        await thread.edit(locked=True)

        await thread.send(
            f"{interaction.user.mention} needs help! <@&760844827804958730> <@&{language_select.value}>",
            allowed_mentions=discord.AllowedMentions(users=True, roles=False),
        )
        await interaction.edit_original_message(
            content=f"Your private help thread has been created: {thread.mention}",
            view=None
        )

    @commands.command()
    async def close(self, ctx):
        if str(ctx.channel.type) == 'private_thread' and ctx.channel.parent.id == self.private_help_channel:
            await ctx.send('This channel will be archived soon. Hope you are happy with the help.')
            await asyncio.sleep(5)
            await ctx.channel.edit(archived=True)
        else:
            await ctx.embed('This command can only be used to close help threads.')


def setup(bot):
    bot.add_cog(Help(bot))

class LanguageSelect(discord.ui.Select):
    def __init__(self, bot):
        options = [
            discord.SelectOption(
                label='Python', 
                #description='You need help with Python', 
                emoji=bot.get_custom_emoji('python'),
                value=807098700589301791
            ),
            discord.SelectOption(
                label='Javacript', 
                #description='You need help with Javacript', 
                emoji=bot.get_custom_emoji('js'),
                value=807098827185717299
            ),
            discord.SelectOption(
                label='Java', 
                #description='You need help with Java', 
                emoji=bot.get_custom_emoji('java'),
                value=807098903127916584
            ),
            discord.SelectOption(
                label='C++', 
                #description='You need help with C++', 
                emoji=bot.get_custom_emoji('cpp'),
                value=807098975986384947
            ),
            discord.SelectOption(
                label='C#', 
                #description='You need help with C#', 
                emoji=bot.get_custom_emoji('csharp'),
                value=807099060883423272
            ),
            discord.SelectOption(
                label='HTML CSS', 
                #description='You need help with HTML or CSS', 
                emoji=bot.get_custom_emoji('html'),
                value=807099145278062602
            ),
        ]
        super().__init__(placeholder='Choose the language', min_values=1, max_values=1, options=options)


    async def callback(self, interaction):
        self.view.value = self.values[0]
        self.disabled = True
        self.view.stop()
        await interaction.response.defer()
