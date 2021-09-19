import discord
from discord.ext import commands


class Archive(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @property
    def archive_category(self):
        return discord.utils.get(self.bot.tca.categories, id=812881115705901088)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def archive(self, ctx, channel: discord.TextChannel=None):
        channel = channel or ctx.channel
        await channel.purge(limit=1)
        await channel.edit(category=self.archive_category, sync_permissions=True)
        embed = discord.Embed(title="✅ Successfully Archived", description=f"`{channel.name}` has been successfully archived", color=discord.Color.green())
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Archive(bot))