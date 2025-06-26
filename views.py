import discord 
from utils import get_date_options, get_time_options, events
from datetime import datetime

class DateSelectView(discord.ui.View):
    def __init__(self, event_name):
        super().__init__()
        self.event_name = event_name
        self.add_item(DateDropdown(event_name))
        self.add_item(ExitButton())

class DateDropdown(discord.ui.Select):
    def __init__(self, event_name):
        options = get_date_options()
        self.event_name = event_name
        super().__init__(placeholder="Pick a date", options=options)
    
    async def callback(self, interactions: discord.Interaction):
        selected_date = self.values[0]
        await interactions.response.send_message(
            f"Selected `{selected_date}` — pick your available time period (starting time):",
            view=TimeSlotView(interactions.user.id, selected_date, self.event_name),
            ephemeral=True
        )

class TimeSlotView(discord.ui.View):
    def __init__(self, user_id, selected_date, event_name):
        super().__init__()
        self.user_id = user_id
        self.selected_date = selected_date
        self.event_name = event_name
        self.add_item(TimeSlotDropdownStart())
        self.add_item(TimeSlotDropdownEnd())
        self.add_item(SaveButton(user_id, selected_date, event_name))

class TimeSlotDropdownStart(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Pick your earliest starting time",
            options=get_time_options(),
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

class TimeSlotDropdownEnd(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Pick your latest starting time",
            options=get_time_options(),
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

class SaveButton(discord.ui.Button):
    def __init__(self, user_id, selected_date, event_name):
        super().__init__(label="Submit Time", style=discord.ButtonStyle.success)
        self.user_id = user_id
        self.selected_date = selected_date
        self.event_name = event_name

    async def callback(self, interaction: discord.Interaction):
        time_earliest = next(item for item in self.view.children if isinstance(item, TimeSlotDropdownStart))
        time_latest = next(item for item in self.view.children if isinstance(item, TimeSlotDropdownEnd))
        
        if not time_earliest.values or not time_latest.values: # values is a list
            await interaction.response.send_message(
                "⚠️ Please select one time slot before submitting.",
                ephemeral=True
            )
            return

        start_time_str, end_time_str = time_earliest.values[0], time_latest.values[0]
        start_time, end_time = datetime.strptime(start_time_str, "%H:%M").time(), datetime.strptime(end_time_str, "%H:%M").time()

        if end_time < start_time:
            await interaction.response.send_message(
                "⚠️ End time must be *after* start time.",
                ephemeral=True
            )
            return

        # Store result in memory
        events[self.event_name].setdefault(self.user_id, {})
        events[self.event_name][self.user_id][self.selected_date] = (start_time_str, end_time_str) 

        print(events)

        await interaction.response.send_message(
            f"✅ Saved: {self.selected_date} → {f'{start_time_str} - {end_time_str}'}\nPick another date?",
            view=DateSelectView(self.event_name),
            ephemeral=True
        )

class ExitButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Finish", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "👋 Thanks! Your availability has been recorded.",
            ephemeral=True
        )
        self.view.stop()  # stops the view from accepting further input