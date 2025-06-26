import os 
import discord 
from discord.ext import commands 
from dotenv import load_dotenv
from views import DateSelectView
from utils import events, get_best_time

load_dotenv()
token = os.getenv("token")

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix="/", intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    try:
        synced = await client.tree.sync(guild=discord.Object(id=1051835171239903232))
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@client.tree.command(guild= discord.Object(id=1051835171239903232), name = "start", description="Start scheduling an event")
async def start(interaction: discord.Interaction):
    await interaction.response.send_modal(ScheduleModal())

class ScheduleModal(discord.ui.Modal, title="Submit Availability"):
    event_name = discord.ui.TextInput(label="Event Name", placeholder="e.g. Movie")
    location = discord.ui.TextInput(label="Event Location", placeholder="e.g. Village Cinema")

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title = self.event_name.value, 
            description=f"📍 {self.location.value}\n\nClick below to submit your availability!"
        )

        if self.event_name.value in events:
            await interaction.response.send_message("This event already exists! Please finish scheduling the existing one first.")
            return 
        else:
            events[self.event_name.value] = {}

        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar)
        await interaction.response.send_message(embed=embed, view=DateSelectView(self.event_name.value))

@client.tree.command(guild= discord.Object(id=1051835171239903232), name = "summary", description="View event summary")
async def summary(interaction: discord.Interaction):
    embed = discord.Embed(title="📋 Event Summary", color=discord.Color.blue())

    if not events:
        embed.description = "No events scheduled."
    else:
        for event_name, responses in events.items():
            response_count = len(responses)
            embed.add_field(
                name=f"🗓️ {event_name}",
                value=f"**{response_count}** response{'s' if response_count != 1 else ''}",
                inline=False
            )

    await interaction.response.send_message(embed=embed, ephemeral=False)

@client.tree.command(guild= discord.Object(id=1051835171239903232), name = "schedule", description="Schedule the best time for everyone")
@discord.app_commands.describe(event_name = "Name of the event to schedule")
async def schedule(interaction: discord.Interaction, event_name: str):
    embed = discord.Embed(title="📋 Schedule Summary", color=discord.Color.blue())

    if event_name not in events:
        embed.description = "Event not found."
    else:
        best_date, best_time, max_users, users = get_best_time(events, event_name)
        user_mentions = "\n".join(f"<@{uid}>" for uid in users)

        embed.description = (
            f"**🗓️ Best Date:** {best_date}\n"
            f"**🕒 Best Time:** {best_time}\n"
            f"**👥 Number of Users Available:** {max_users}\n\n"
            f"**✅ Users Available:**\n{user_mentions}"
        )

    await interaction.response.send_message(embed=embed)

client.run(token)