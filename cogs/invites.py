import asyncio
import discord
from discord.ext import commands


class Invites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invite_manager_id = 720351927581278219
        self._inviter_roles_invite_map = {}

    @property
    def inviter_roles(self):
        return [r for r in self.bot.tca.roles if "inviter" in r.name.lower()]

    @commands.Cog.listener()
    async def on_message(self, msg):
        if not self._inviter_roles_invite_map:
            self.setup_inviter_roles()

        if msg.author.bot:
            return
         
        if msg.content != "i.invites" and msg.content != "i.invite":
            return

        try:
            message = await self.bot.wait_for("message", check = lambda m: m.author.id == self.invite_manager_id and msg.channel == m.channel, timeout=20)
        except asyncio.TimeoutError:
            return
            
        data = message.embeds[0].to_dict()
        des = data["description"]        
        s = des.index("**")
        e = des.index("**", s+1)
        invites = int(des[s+2:e])
        roles = self.get_inviter_roles_for(invites)
        if roles and roles[-1] not in msg.author.roles:
            await msg.author.add_roles(*roles)
            await msg.reply(f"You have been granted the {roles[-1].mention} role!", allowed_mentions=discord.AllowedMentions.none())

    def get_inviter_roles_for(self, invites):
        roles = []
        for i in self._inviter_roles_invite_map:
            if invites >= i:
                roles.append(self._inviter_roles_invite_map[i])
                
        return roles

    def setup_inviter_roles(self):
        for r in self.inviter_roles:
            s = r.name.index("(")
            e = r.name.index(")")
            invites = int(r.name[s+1:e-1])
            self._inviter_roles_invite_map[invites] = r
                
def setup(bot):
    bot.add_cog(Invites(bot))