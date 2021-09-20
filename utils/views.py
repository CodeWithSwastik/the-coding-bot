import discord

class Confirm(discord.ui.View):
    """Confirmation buttons"""

    def __init__(self, user):
        super().__init__()
        self.value = None
        self.user = user

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.primary)
    async def confirm(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):

        self.value = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):

        self.value = False
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "You cannot interact with this!", ephemeral=True
            )
            return False
        return True
