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

def generate_times(start_time):
    datetime_list = [start_time]

    for _ in range(1, 10):
        next_datetime = datetime_list[-1] + timedelta(minutes=135)
        datetime_list.append(next_datetime)

    return datetime_list


# ----------------------------------------------------------------------------------------------------------------------
# BOT COMMANDS

@bot.tree.command(name="helltide", description="Sets a notification for the user on a selected Helltide event")
@app_commands.describe(time_of_next_helltide="Time next helltide is slated to begin in 24 hour format; '13:15'",
                       time_prior_notification="Early notice in minutes you'd like to be notified")
async def helltide(inter: discord.Interaction, time_of_next_helltide: str, time_prior_notification: float):
    reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

    await inter.response.defer(ephemeral=True)

    author = inter.user.id

    given_helltide_time = datetime.strptime(time_of_next_helltide, "%H:%M").time()
    helltide_start_time = datetime.combine(datetime.today().date(), given_helltide_time)
    times = generate_times(helltide_start_time)
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


# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    bot.run(config["token"])
