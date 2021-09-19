import discord
from discord.ext import commands, tasks

def is_staff():
    return commands.has_any_role('Staff', 'Trainee Moderator') # Staff + Trainee

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.rules = []
        self.faqs = []

        self.setup.start()
    
    @tasks.loop(count=1)
    async def setup(self):
        rules_channel = await self.bot.fetch_channel(681887262136598589)
        faq_channel = await self.bot.fetch_channel(725960895481774084)

        raw_rules = (await rules_channel.fetch_message(790896473231196170)).content
        raw_rules += '\n\n' + (await rules_channel.fetch_message(790896673991557120)).content
        self.rules = self.parse_rules(raw_rules)[:-1]

        raw_faqs = (await faq_channel.fetch_message(794786168461066241)).content
        self.faqs = self.parse_rules(raw_faqs)

    @setup.before_loop
    async def before_setup(self):
        await self.bot.wait_until_ready()

    def parse_rules(self, text: str) -> list:
        return text.split('\n\n')

    @commands.command(aliases=['sm'])
    @is_staff()
    async def slowmode(self, ctx, time = None):
        if time is None:
            await ctx.send(f'Current slowmode is `{ctx.channel.slowmode_delay}` seconds')
            return
        elif time.startswith('+') or time.startswith('-'):
            new_delay = ctx.channel.slowmode_delay + int(time)
        else:
            new_delay = int(time)
        if new_delay > 21600:
            return await ctx.send("Slowmode can't be more than 21600 seconds.")
        await ctx.channel.edit(slowmode_delay = new_delay)
        await ctx.send(f'Set slowmode to `{new_delay}` seconds')

    @slowmode.error
    async def sm_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(str(error.original))

    @commands.command()
    @is_staff()
    async def rule(self, ctx, number:int):
        if number < len(self.rules) and number > 0:
            rule = self.rules[number]
            q = rule.split('\n')[0]
            a = '\n'.join(rule.split('\n')[1:])
            converter = commands.clean_content(fix_channel_mentions=True)
            embed = discord.Embed(
                title=await converter.convert(ctx, q), 
                description=a, 
                color=discord.Color.yellow()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send('Invalid rule number.')

    @commands.command()
    @is_staff()
    async def faq(self, ctx, number:int):
        if number <= len(self.faqs) and number > 0:
            q = self.faqs[number-1].split('\n')[0]
            a = '\n'.join(self.faqs[number-1].split('\n')[1:])
            converter = commands.clean_content(fix_channel_mentions=True)
            embed = discord.Embed(
                title=await converter.convert(ctx, q), 
                description=a, 
                color=discord.Color.yellow()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send('Invalid faq number.')

def setup(bot):
    bot.add_cog(Moderation(bot))
