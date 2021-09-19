import re
import traceback

import discord
from discord.ext import commands


class ErrorHandling(commands.Cog):
    def __init__(self, bot: commands.Bot):

        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):

        if hasattr(ctx.command, "on_error"):
            pass

        elif isinstance(error, commands.CommandNotFound):
            pass

        elif not isinstance(error, commands.CommandInvokeError):
            title = " ".join(
                re.compile(r"[A-Z][a-z]*").findall(error.__class__.__name__)
            )
            return await ctx.send(
                embed=discord.Embed(
                    title=title, description=str(error), color=discord.Color.blurple()
                )
            )

        else:

            await ctx.message.clear_reactions()
            await ctx.send(
                embed=discord.Embed(
                    title="Unknown Error",
                    description="Don't worry my developer has been notified about it.",
                    color=0xF5A3FB,
                )
            )

            try:

                webhook = discord.Webhook.from_url(
                    self.bot.config.logger_url, session=self.bot.session
                )

                errno = "".join(
                    traceback.format_exception(type(error), error, error.__traceback__)
                )

                embed = discord.Embed(
                    title=f"Command: {ctx.command.name}",
                    description=f"```py\n{errno}\n```",
                    color=0xED46B3,
                )
                embed.add_field(
                    name="Message ID",
                    value=f"[Click Here]({ctx.message.jump_url})",
                    inline=False,
                )
                embed.add_field(name="Author", value=ctx.author.mention)

                await webhook.send(embed=embed)

            except Exception:
                raise Exception


def setup(bot: commands.Bot):
    bot.add_cog(ErrorHandling(bot))
