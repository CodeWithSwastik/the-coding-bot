import asyncio
from discord.errors import InvalidArgument
from utils.views import Confirm
import discord
import re
from discord.ext import commands


class AddBot(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @property
    def pending_channel(self):
        return self.bot.get_channel(842059829953560608)

    @property
    def pending_message_id(self):
        return 894205037079851018

    @property
    def add_bot_channel(self):
        return self.bot.get_channel(894208222678892574)


    @property
    def testing_guild(self):
        return self.bot.get_guild(841721684876328961)

    @property
    def testing_bot_role(self):
        return self.testing_guild.get_role(842081841581654066) if self.testing_guild else None
    
    @property
    def user_bot_role(self):
        return self.bot.tca.get_role(842101681806376980) if self.bot.tca else None
    
    def parse_msg_id(self, bot_id, content):
        content = content[content.index(':-'):].split('\n')
        for i in content:
            if str(bot_id) in i:
                return int(i.split(':')[1]), i

    async def get_pending_message(self):
        return await self.pending_channel.fetch_message(self.pending_message_id)

    async def get_bot_owner(self, embed):
        id = [f.value for f in embed.fields if f.name == 'Submitted By'][0][2:20]
        return await self.bot.fetch_user(id)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild == self.testing_guild and member.bot:
            await member.add_roles(self.testing_bot_role)


    @commands.command()
    @commands.has_any_role(729927579645247562, 737517726737629214)
    @commands.cooldown(1, 86400, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.user)
    async def addbot(self, ctx, bot: discord.User, *, reason: str):
        if not bot.bot:
            raise InvalidArgument('That is not a bot!')

        if bot in ctx.guild.members:
            raise InvalidArgument('That bot is already in this server!')

        if str(bot.id) in (await self.get_pending_message()).content:
            raise InvalidArgument('That bot has already been submitted, please keep your dms open and you\'ll be notified if your bot gets approved!')

        if len(reason) not in range(50, 1000):
            raise InvalidArgument('Reason must be 50 to 1000 characters long.')


        embed = discord.Embed(title='Is this correct?', description=f'**Reason:** {reason}')
        embed.set_author(name=str(bot), icon_url=bot.avatar.url)
        
        confirm_view = Confirm(ctx.author)
        msg = await ctx.reply(content = '\u200b', embed=embed, view=confirm_view)

        result = await confirm_view.wait()
        await msg.delete()

        if result or not confirm_view.value:
            # User selected cancel or timeout
            ctx.command.reset_cooldown(ctx)
            return 

        await ctx.embed(
            f'{self.bot.get_custom_emoji("greentick")} Your bot will be verified by our staff and added soon!'
        )

        invite = discord.utils.oauth_url(bot.id, guild=self.testing_guild)
        embed = discord.Embed(title='User-Made Bot', description=f'Click bot name to invite.')
        embed.add_field(name='Status', value='Pending approval')
        embed.add_field(name='Submitted By', value=ctx.author.mention + ' (' + str(ctx.author) + ')')
        embed.add_field(name='Reason', value=reason)
        embed.add_field(name='Bot Account', value=bot.mention)
        embed.set_author(name=str(bot), icon_url=bot.avatar.url, url=invite)
        ch_msg = await self.pending_channel.send(embed=embed)
        msg = await self.get_pending_message()
        await msg.edit(content = msg.content+f'\n{bot.id}:{ch_msg.id}')

    @addbot.error
    async def addbot_error(self, ctx, error):
        ctx.command.reset_cooldown(ctx)
        if isinstance(error, commands.CommandInvokeError):
            error = error.original
        text = str(error)
        if isinstance(error, commands.MissingAnyRole):  
            text = re.sub(r"'(\d+)'", r"<@&\1>", text)
        hellno = self.bot.get_custom_emoji('hellno')
        embed = discord.Embed(description=f'{hellno} {text}', color=0xff0000)
        await ctx.send(embed=embed)

    @commands.user_command(name='Approve Bot', guild_ids=[841721684876328961])
    #commands.slash_command(name='approve', guild_ids=[841721684876328961])
    async def approve_bot(self, ctx, bot: discord.Member):
        if not bot.bot:
            return await ctx.respond("You can't approve a non-bot.")
        msg = await self.get_pending_message()
        if str(bot.id) not in msg.content:
            return await ctx.respond("That bot has either been already denied or approved.")
        await ctx.respond("Approving the bot....")

        bot_msg_id, full_text = self.parse_msg_id(bot.id, msg.content)
        e = await self.pending_channel.fetch_message(bot_msg_id)
        embed = e.embeds[0]
        embed.set_field_at(0, name='Status', value='Approved, Pending admin approval')
        embed.add_field(name='Approved by', value=ctx.author.mention + ' (' + str(ctx.author) + ')')
        embed.description = 'Check <#894208222678892574> to add the bot.'
        embed.color = discord.Color.green()
        embed.set_author(name=embed.author.name, icon_url=embed.author.icon_url)
        embed.set_footer(text=f'Approved by {ctx.author}', icon_url=ctx.author.display_avatar.url)
        await e.edit(embed = embed)

        await msg.edit(content=msg.content.replace(full_text, ''))
        await bot.remove_roles(*bot.roles[1:])
        await bot.add_roles(ctx.guild.get_role(894211972894191616))


        embed.description = 'Press the button to get the invite link.'
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Add this bot", emoji="🔗"))
        await self.add_bot_channel.send(content=bot.id, embed=embed, view=view)


        try:
            owner = await self.get_bot_owner(embed)
            await owner.send(f'Your bot, {embed.author.name} has been approved in The Coding Realm and will be added soon.')
        except discord.Forbidden:
            pass
        await ctx.respond("Bot approved.")

    #@commands.slash_command(name='deny', guild_ids=[841721684876328961])
    commands.user_command(name='Deny Bot', guild_ids=[841721684876328961])
    async def deny_bot(self, ctx, bot: discord.Member):
        if not bot.bot:
            return await ctx.respond("You can't deny a non-bot.")
        msg = await self.get_pending_message()
        if str(bot.id) not in msg.content:
            return await ctx.respond("That bot has either been already denied or approved.")
            
        await ctx.respond("Please type out the reason for denial.")
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author
        message = await self.bot.wait_for('message', check=check, timeout=60)
        reason_of_denial = message.content

        bot_msg_id, full_text = self.parse_msg_id(bot.id, msg.content)
        e = await self.pending_channel.fetch_message(bot_msg_id)
        embed = e.embeds[0]
        embed.set_field_at(0, name='Status', value='Denied')
        embed.add_field(name='Denied by', value=ctx.author.mention + ' (' + str(ctx.author) + ')')
        embed.add_field(name='Reason of Denial', value=reason_of_denial)


        embed.description = 'Denied'
        embed.color = discord.Color.red()
        embed.set_author(name=embed.author.name, icon_url=embed.author.icon_url)
        embed.set_footer(text=f'Denied by {ctx.author}', icon_url=ctx.author.display_avatar.url)

        await e.edit(embed = embed)

        await msg.edit(content=msg.content.replace(full_text, ''))
        try:
            owner = await self.get_bot_owner(embed)
            await owner.send(f'Your bot, {embed.author.name} has been declined. Reason: {reason_of_denial}')
        except discord.Forbidden:
            pass
        await bot.kick(reason=f'Denied by {ctx.author.name}')
        await ctx.respond("Bot denied. It has been kicked from this server.")

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.channel_id != self.add_bot_channel.id:
            return

        if not interaction.message:
            return

        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("You don't have permissions to add the bot!", ephemeral=True)

        bot_id = int(interaction.message.content)
        invite = discord.utils.oauth_url(bot_id, guild=interaction.guild)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Invite the bot", url=invite))
        await interaction.response.send_message("**IMPORTANT**: Please add the bot within 5 minutes otherwise the bot will have elevated permissions!", view = view)

        def check(m):
            return m.bot and m.id == bot_id

        try:
            bot_joined = await self.bot.wait_for('member_join', check=check, timeout=300)
        except asyncio.TimeoutError:
            return        

        await bot_joined.add_roles(self.user_bot_role)

        embed = interaction.message.embeds[0]
        embed.set_footer(text=f'Added by {interaction.user}', icon_url=interaction.user.display_avatar.url)
        embed.set_field_at(0, name='Status', value='Added')
        embed.add_field(name='Added by', value=interaction.user.mention + ' (' + str(interaction.user) + ')')
        embed.description = 'Added'
        embed.color = discord.Color.green()
        embed.set_author(name=embed.author.name, icon_url=embed.author.icon_url)
        embed.timestamp = discord.utils.utcnow()
        await interaction.message.edit(content=None, embed=embed, view=None)
        await interaction.delete_original_message()
        
def setup(bot):
    bot.add_cog(AddBot(bot))
