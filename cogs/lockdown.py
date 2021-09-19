import discord
from discord.ext import commands

class Lockdown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Roles on which the bot will deny perms
        self.bot.lockdown_roles = [836266952401223681]
        
        #Categories where the bot wont change perms (staff categories, important categories, etc)
        self.bot.blacklisted_categories = [836266383183708170, 836506482027266128, 836265345257177199] 


    @commands.command(aliases=['glockdown'])
    @commands.has_permissions(manage_guild=True)
    async def globallockdown(self, ctx): 
        for channel in ctx.guild.channels:
            if str(channel.type) == 'text':
                if channel.category != None:     
                    if channel.category.id not in self.bot.blacklisted_categories:
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
    async def globalunlock(self, ctx):
        for channel in ctx.guild.channels:
            if str(channel.type) == 'text':
                if channel.category != None:     
                    if channel.category.id not in self.bot.blacklisted_categories:
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