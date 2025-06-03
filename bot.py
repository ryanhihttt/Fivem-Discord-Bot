import discord
from discord.ext import commands
from discord import app_commands
import config

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

class VerifyModal(discord.ui.Modal, title="FiveM Verification"):
    ic_name = discord.ui.TextInput(
        label="Enter your IC Name (min 2 letters)",
        min_length=2,
        max_length=32,
        placeholder="Your IC Name here",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        ic_name = self.ic_name.value
        channel = bot.get_channel(config.LOG_CHANNEL_ID)
        if channel is None:
            await interaction.response.send_message("Verification channel not found. Contact admin.", ephemeral=True)
            return

        embed = discord.Embed(
            title="New Verification Request",
            description=f"User: {interaction.user.mention}\nIC Name: **{ic_name}**",
            color=discord.Color.magenta()
        )
        await channel.send(embed=embed)
        await interaction.response.send_message("Your verification request has been sent!", ephemeral=True)

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(VerifyModal())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    bot.add_view(VerifyView())  # persistent view for button interactions

    # Send the verification panel automatically ONCE when bot starts
    channel = bot.get_channel(config.VERIFICATION_CHANNEL_ID)
    if channel is None:
        print(f"Verification channel ID {config.VERIFICATION_CHANNEL_ID} not found.")
        return

    # Optional: Check if a message with our custom_id already exists to avoid duplicates
    async for message in channel.history(limit=50):
        if message.author == bot.user:
            # Check if message has our view/button
            if message.components:
                # Found existing panel, do not send again
                print("Verification panel already exists in the channel.")
                break
    else:
        # If no existing panel found, send it now
        embed = discord.Embed(
            title="Verification Panel",
            description="Click the **Verify** button below to submit your IC Name for FiveM verification.",
            color=discord.Color.magenta()
        )
        await channel.send(embed=embed, view=VerifyView())
        print("Sent verification panel.")

bot.run(config.TOKEN)