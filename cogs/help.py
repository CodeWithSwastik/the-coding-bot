import discord
import asyncio
from discord.ext import commands
from utils.views import Confirm
import re

# >jsk py
# ```
# embed = discord.Embed(title='Private Help', description = 'Press the button below for private help.', color = discord.Color.yellow())
# button = discord.ui.Button(label='Help!', emoji='🙋', custom_id='help_button', style=discord.ButtonStyle.green)
# view = discord.ui.View()
# view.add_item(button)
# e=await ctx.send(embed=embed, view=view)
# ```

# TODO: >delete-stale-threads
class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.private_help_channel = 889149110588960838
        
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: 
            return
        if hasattr(message.channel, 'category') and message.channel.category and message.channel.category.id != 754710748353265745:
            return

        if 'Traceback' in message.content or 'File' in message.content:
            if 'ModuleNotFoundError:' in message.content:
                module = re.findall(r"'.*'", message.content)[-1][1:-1] 
                if module == 'pycord':
                    return await message.reply(f'The correct import for pycord is `import discord`')
                if '.' in module:
                    module = module.split('.')[0]
                await message.reply(f'Did you try `pip install {module}`')
            elif 'SyntaxError:' in message.content:
                await message.reply(f'This could be helpful: <https://realpython.com/invalid-syntax-python/>')
            elif 'IndentationError:' in message.content:
                await message.reply(f'This could be helpful: <https://appuals.com/fix-indentation-error-python/>')
            elif 'ZeroDivisionError:' in message.content:
                await message.reply(
"""The error is kind of self-explanatory. You tried to divide something by 0 which is impossible.

This usually happens when you divide something with a user input and the user inputs 0.

To fix this, use an if statement to check if the number is 0 and dont divide if it is, or use a try-except to catch the error.

```py
try:
  res = a / b
except ZeroDivisionError:
  print('You may not divide by zero')
```
""")
        if 'except:' in message.content:
            await message.reply('Tip: You have a bare except in your code, I would recommend you to use `except Exception:`\nWould be even better if you specify the exception type. You should never use bare excepts in your code.')

        
        if '`' in message.content: # check code
            res, val = check_unmatched(message.content)
            if res:
                await message.reply(f'You have an {val} in your code!')
            if '```py' in message.content:
                
                for i in message.content.split('\n'):
                    keywords = ['if', 'elif', 'else', 'for', 'while', 'def', 'async', 'try', 'except']
                    if any(i.lstrip().startswith(s+ ' ') for s in keywords) and ':' not in i:
                        await message.reply(f'> {i}\nYou missed a colon `:` in this line')



    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.channel_id != self.private_help_channel:
            return

        if interaction.data.get("custom_id", "") == "help_button":
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
            type=discord.ChannelType.public_thread
        )
        await interaction.channel.purge(limit=1)

        # await thread.edit(locked=True) idk?
        await interaction.edit_original_message(
            content=f"Your private help thread has been created: {thread.mention}",
            view=None
        )
        
        await thread.send(
            f"<@&760844827804958730> <@&{language_select.value}>\n"
            f"{interaction.user.mention}, please send your problem/question here.\n"
"""
1. Post your code
2. Post your errors 
3. Send a short description of what you are trying to make

Do not ask “will anybody help me?” or “Hello is anybody willing to help me out” as it wastes and makes helping you out slower, simply post your issue and a helper will get to you as soon as possible.

Once your queries have been solved you can close the thread using `>close`
""",
            allowed_mentions=discord.AllowedMentions(users=True, roles=True),
        )
        def check(m):
            return (
                m.author == interaction.user and 
                m.channel == thread and 
                len(m.content) > 35
            )

        message = await self.bot.wait_for('message', check=check)
        await message.pin()

    @commands.command()
    async def close(self, ctx):
        if str(ctx.channel.type) == 'public_thread' and ctx.channel.parent.id == self.private_help_channel:
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

def check_unmatched(string):
    brackets = ['()', '{}', '[]']
    for x in brackets:
        if string.count(x[0]) > string.count(x[1]):
            return True, f'Unclosed {x[0]!r}'
        elif string.count(x[0]) < string.count(x[1]):
            return True, f'Unopened {x[1]!r}'
    return False, 'Nothing unmatched'
