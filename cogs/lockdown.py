import discord
from discord.ext import commands

class Lockdown(commands.Cog):
    def __init__(self, bot):
        # TODO: Lock threads, voice channels
        self.bot = bot

        # Roles on which the bot will deny perms
        self.lockdown_roles = [836266952401223681]
        
        #Categories where the bot will change perms
        self.categories_to_lock = [
            681882712453545989, # Lobby
            754710748353265745, # Help
            842168374393831464, # User made bots
            836265345257177199, # Other
            725738091771592795, # Voice
            758698912822591510, # Music
        ] 

        # Channels which wont be touched
        self.blacklisted_channels = [
            731341772755697695, # Exclusive
            754712400757784709, # how-to-get-help
        ]
    
    @property
    def channels_to_lock(self):
        return [ 
            c for c in self.bot.tca.channels
            if c.category and c.category.id in self.categories_to_lock
            and c.id not in self.blacklisted_channels
        ]

    @commands.command(aliases=['glockdown'])
    @commands.has_permissions(manage_guild=True)
    async def lockdown(self, ctx): 
        for channel in self.channels_to_lock:
            if str(channel.type) == 'text':
                for role_id in self.bot.lockdown_roles:
                    role = ctx.guild.get_role(role_id)
                    # Locking the channels
                    overwrite = channel.overwrites_for(role)
                    overwrite.send_messages = False
                    await channel.set_permissions(role, overwrite=overwrite)
    
        embed = discord.Embed(title="✅ Global lockdown successful", description=f"The server has been locked down by {ctx.author.mention}", color = discord.Color.green())
        await ctx.send(embed=embed)

    @commands.command(aliases=['gunlock'])
    @commands.has_permissions(manage_guild=True)
    async def unlock(self, ctx):
        for channel in self.channels_to_lock:
            if str(channel.type) == 'text':
                for role_id in self.bot.lockdown_roles:
                    role = ctx.guild.get_role(role_id)
                    # Unlocking the channels
                    overwrite = channel.overwrites_for(role)
                    overwrite.send_messages = True
                    await channel.set_permissions(role, overwrite=overwrite)

        embed = discord.Embed(title="✅ Global unlock successful", description=f"The server has been unlocked by {ctx.author.mention}", color = discord.Color.green())
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Lockdown(bot))