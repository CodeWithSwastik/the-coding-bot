import discord
from discord.ext import commands
from .moderation import is_staff

# I think I should add a system that auto sets slowmode depending on the message frequency
class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.previous_messages: list[discord.Message] = []
        self.last_change = discord.utils.utcnow()
        self.busy = False

    @property
    def average_time(self):
        time_diff = []
        for i, msg in enumerate(self.previous_messages[:-1]):
            delta = self.previous_messages[i+1].created_at - msg.created_at
            time_diff.append(delta.total_seconds())

        return sum(time_diff)/len(time_diff)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.channel.id == 743817386792058971: # general
            return
        if message.channel.permissions_for(message.author).manage_messages:
            return

        self.previous_messages.append(message)
        if len(self.previous_messages) < 10:
            return
        current_slowmode = message.channel.slowmode_delay
        if self.average_time > 2 and current_slowmode > 0 and not self.busy:
            self.busy = True
            await message.channel.edit(slowmode_delay=0)
            pika = self.bot.get_custom_emoji('pikacoolwink')
            await message.channel.send(
                f'I set slowmode to 0 for you chill people {pika}'
            )
            self.busy = False

        print(self.average_time)
        if self.average_time < .8 and not self.busy:
                if (message.created_at - self.last_change).total_seconds() < 15: # dont spam
                    return
                self.busy = True
                idk = round(1/self.average_time)
                await message.channel.edit(slowmode_delay=idk)
                await message.channel.send(
                    f'I set slowmode to {idk} as the chat is a bit fast.'
                )
                self.last_change = message.created_at
                self.busy = False


        del self.previous_messages[0]   

    @commands.command()
    @is_staff()
    async def autoslowmode(self, ctx, toggle: bool = None):
        if toggle is None:
            return await ctx.send(f'Auto-slowmode adjustment: {not self.busy}')
        self.busy = not toggle
        await ctx.send(f'I set auto-slowmode adjustment to {toggle}')
        
def setup(bot):
    bot.add_cog(Utility(bot))
