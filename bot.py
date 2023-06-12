"""
Limitations:
    Shutdown of the bot while helltide timers are activated will remove all timers
"""

# Package Imports
import json
import asyncio
from discord.ext import commands, tasks
import discord
from discord import app_commands
import os
import platform
from datetime import datetime, timedelta

# Local Imports
from resources import embeds

# Bot instance
bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())

# Load bot configuration file
if __name__ == "__main__":
    with open("config.json", "r") as f:
        config = json.load(f)

# Modify on base time change for helltides
# Global Var
HELLTIDE_BASE_TIME = datetime(2023, 6, 12, 14, 45, 0)


# On Ready data
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")
    synced = await bot.tree.sync()
    print(f"Slash CMDs Synced {len(synced)} Commands")


# ----------------------------------------------------------------------------------------------------------------------
# TASKS


# ----------------------------------------------------------------------------------------------------------------------
# BASE FUNCTIONS

def generate_times(base_time: datetime) -> list:
    """
    Takes a base time and evaluates each increment of time 135 minutes passed the base time.
    Observes the first datetime increment past the current time and returns it and 9 future
    increment datetime objects.

    :param base_time: datetime object holding a base time to evaluate off of
    :return: list of evaluated datetime objects in the future
    """
    occurrences = []
    group_duration = timedelta(hours=2, minutes=15)
    current_time = datetime.now()

    time_difference = current_time - base_time
    remainder_seconds = time_difference.total_seconds() % group_duration.total_seconds()
    remaining_seconds = group_duration.total_seconds() - remainder_seconds
    next_occurrence = current_time + timedelta(seconds=remaining_seconds)

    occurrences.append(next_occurrence)

    for _ in range(1, 10):
        next_occurrence += group_duration
        occurrences.append(next_occurrence)

    return occurrences



# ----------------------------------------------------------------------------------------------------------------------
# BOT COMMANDS

@bot.tree.command(name="helltide", description="Sets a notification for the user on a selected Helltide event")
@app_commands.describe(time_prior_notification="Early notice in minutes you'd like to be notified")
async def helltide(inter: discord.Interaction, time_prior_notification: float):
    reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

    await inter.response.defer(ephemeral=True)

    author = inter.user.id

    times = generate_times(HELLTIDE_BASE_TIME)
    time_library = {k: v for k, v in zip(reactions, times)}

    await inter.followup.send(embed=embeds.standard_embed(text="Stay a while..."))

    msg = await inter.user.send(embed=embeds.timer_embed(times))

    for reaction in reactions:
        await msg.add_reaction(reaction)

    try:
        reac, user = await bot.wait_for("reaction_add", timeout=180)

        if user.id == author and str(reac) in reactions:
            time_to_helltide = time_library[str(reac)]
            time_delta = (time_to_helltide - datetime.now()) - timedelta(minutes=time_prior_notification)
            notification_time = datetime.now() + time_delta
            delta_seconds = int(time_delta.total_seconds())

            await inter.user.send(embed=embeds.standard_embed(
                text=f"I will notify you at {notification_time.strftime('%H:%M')} of the helltide",
                color=discord.Color.dark_red(),
                title="**__The Armys of Hell Approach__**",
                footer=datetime.now().strftime("%m/%d/%Y %H:%M")
            )
            )
            await asyncio.sleep(delta_seconds)
            await inter.user.send(embed=embeds.standard_embed(
                text="Helltide is beginning soon",
                color=discord.Color.dark_red(),
                title="**__The Blood Rain Falls__**",
                url="https://diablo4.life/trackers/helltide",
                footer=datetime.now().strftime("%m/%d/%Y %H:%M"),
                image="https://cdn.discordapp.com/attachments/788999177442426910/1116944779046027295"
                      "/RDT_20230609_2319368608710735668798406.jpg "
            )
            )

    except asyncio.TimeoutError:
        await msg.delete()


@bot.tree.command(name="helltimer", description="Sets the base loop time of the helltide timer")
@app_commands.describe(time_of_next_helltide="Time of next helltide event in a 24 hour format; '13:15'")
async def helltimer(inter: discord.Interaction, time_of_next_helltide: str):
    global HELLTIDE_BASE_TIME
    given_helltide_time = datetime.strptime(time_of_next_helltide, "%H:%M").time()
    helltide_start_time = datetime.combine(datetime.today().date(), given_helltide_time)
    HELLTIDE_BASE_TIME = helltide_start_time

    await inter.response.send_message(embed=embeds.standard_embed(
        text=f"The Helltide loop has been reset to start at {helltide_start_time.time()}",
        title="**__Helltimer__**",
        deckard=True,
        footer=datetime.now().strftime("%m/%d/%Y %H:%M")
    ))

    author = inter.user.name
    admin = await bot.fetch_user(208970082594848771)
    await admin.send(embed=embeds.standard_embed(
        text=f"{author} has changed the helltide base timer to loop around {helltide_start_time}",
        title="**__Helltimer Change__**",
        deckard=True,
        footer=datetime.now().strftime("%m/%d/%Y %H:%M")
    ))

# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    bot.run(config["token"])
