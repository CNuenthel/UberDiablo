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
import interactions
from interactions import slash_command, SlashContext, ButtonStyle, listen, slash_option, OptionType, Button
import threading
import concurrent.futures

# Local Imports
from resources import embeds

# Load bot configuration file
if __name__ == "__main__":
    with open("config.json", "r") as f:
        config = json.load(f)

# Bot instance
bot = interactions.Client(token=config["token"], auto_defer=True)

# Modify on base time change for helltides
# Global Var
HELLTIDE_BASE_TIME = datetime(2023, 6, 12, 14, 45, 0)


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


def find_helltide_time(time_dict: dict, ref_time, notification_time) -> [datetime, int]:
    time_of_helltide = time_dict[ref_time]
    time_delta = (time_of_helltide - datetime.now()) - timedelta(minutes=notification_time)
    notification_time = datetime.now() + time_delta
    delta_seconds = int(time_delta.total_seconds())
    return [notification_time, delta_seconds]


def find_time_splits(datetime_list: list):
    now = datetime.now()
    seconds_between = [(datetime_list[0] - now).total_seconds()]

    for i, dt in enumerate(datetime_list):
        if dt == datetime_list[0]:
            continue
        diff = dt - datetime_list[i - 1]
        seconds_between.append(diff.seconds)

    return seconds_between


async def notifier(wait_times: list, user_id: int):
    for seconds in wait_times:
        await asyncio.sleep(seconds)
        user = await bot.fetch_user(user_id)
        await user.send(embed=embeds.standard_embed(
            "Helltide is beginning soon",
            title="https://diablo4.life/trackers/helltide",
            deckard=True,
            color=interactions.Color.from_hex("#5E0016"),
            footer=datetime.now().strftime("%m/%d/%Y %H:%M"),
            image="https://i.ibb.co/Zf7xS1W/0000.jpg"
        )
        )
        helltide_library[user_id].pop(0)


# ----------------------------------------------------------------------------------------------------------------------
# BOT COMMANDS

helltide_library = {"user_id": ["dt"]}


@slash_command(name="helltide", description="Sets a notification for the user on a selected Helltide event")
@slash_option(
    name="time_prior_notification",
    description="Minutes prior to event to be notified",
    required=True,
    opt_type=OptionType.INTEGER
)
async def helltide(ctx: SlashContext, time_prior_notification: float):
    times = generate_times(HELLTIDE_BASE_TIME)
    user_id = ctx.user.id

    if user_id not in helltide_library:
        helltide_library[user_id] = []

    time_library = {time.time().strftime("%H:%M"): time for time in times}

    btns = []

    for time in times:
        time = time.time().strftime("%H:%M")

        style = ButtonStyle.RED
        disabled = False
        if time in helltide_library[user_id]:
            style = ButtonStyle.GREEN
            disabled = True

        btns.append(Button(
            custom_id=time,
            style=style,
            label=time,
            disabled=disabled))

    btns.append(Button(custom_id="Finish", style=ButtonStyle.BLUE, label="Finished"))
    btns.append(Button(custom_id="Cancel", style=ButtonStyle.BLUE, label="Cancel"))
    components = [
        [btns[0], btns[1], btns[2], btns[3]],
        [btns[4], btns[5], btns[6], btns[7]],
        [btns[8], btns[9], btns[10], btns[11]]
    ]

    await ctx.send(embed=embeds.standard_embed(
        text="",
        title="Stay a while...",
        deckard=True,
        url=None,
        color=interactions.Color.from_hex("#0A20EB"),
        footer=datetime.now().strftime("%m/%d/%Y %H:%M")
    ), ephemeral=True)
    msg = await ctx.user.send(embed=embeds.standard_embed(
        text="Select your helltimers, once complete select finish.",
        title="And listen...",
        deckard=True,
        url=None,
        color=interactions.Color.from_hex("#0A20EB"),
        footer=datetime.now().strftime("%m/%d/%Y %H:%M")
    ), components=components)

    notification_times = []
    selecting = True
    while selecting:
        try:
            component_time = await bot.wait_for_component(components=components, timeout=180
                                                          )

            if component_time.ctx.custom_id == "Finish":
                formatted_time_list = [time.time().strftime("%H:%M") for time in notification_times]
                await component_time.ctx.send(embed=embeds.standard_embed(
                    text=f"You will be notified at these times: {', '.join(formatted_time_list)}",
                    color=interactions.Color.from_hex("#910620"),
                    title="**__The Armies of Hell Approach__**",
                    footer=datetime.now().strftime("%m/%d/%Y %H:%M")))

                time_splits = find_time_splits(notification_times)
                await notifier(time_splits, user_id)

                return
            elif component_time.ctx.custom_id == "Cancel":
                await msg.delete()
                return

            time_diff = time_library[component_time.ctx.custom_id] - timedelta(minutes=time_prior_notification)
            notification_times.append(time_diff)

            helltide_library[user_id].append(component_time.ctx.custom_id)

            await msg.delete()
            for row in components:
                for component in row:
                    if component.custom_id == component_time.ctx.custom_id:
                        component.style = ButtonStyle.GREEN
                        component.disabled = True

            msg = await ctx.user.send(embed=embeds.standard_embed(
                text="__NEXT AVAILABLE HELLTIMERS__ ",
                title="And listen...",
                deckard=True,
                url=None,
                color=interactions.Color.from_hex("#0A20EB"),
                footer=datetime.now().strftime("%m/%d/%Y %H:%M")
            ), components=components)

        except asyncio.TimeoutError:
            await msg.delete()
            return


# @bot.tree.command(name="helltimer", description="Sets the base loop time of the helltide timer")
# @app_commands.describe(time_of_next_helltide="Time of next helltide event in a 24 hour format; '13:15'")
# async def helltimer(inter: discord.Interaction, time_of_next_helltide: str):
#     global HELLTIDE_BASE_TIME
#     given_helltide_time = datetime.strptime(time_of_next_helltide, "%H:%M").time()
#     helltide_start_time = datetime.combine(datetime.today().date(), given_helltide_time)
#     HELLTIDE_BASE_TIME = helltide_start_time
#
#     await inter.response.send_message(embed=embeds.standard_embed(
#         text=f"The Helltide loop has been reset to start at {helltide_start_time.time()}",
#         title="**__Helltimer__**",
#         deckard=True,
#         footer=datetime.now().strftime("%m/%d/%Y %H:%M")
#     ))
#
#     author = inter.user.name
#     admin = await bot.fetch_user(208970082594848771)
#     await admin.send(embed=embeds.standard_embed(
#         text=f"{author} has changed the helltide base timer to loop around {helltide_start_time}",
#         title="**__Helltimer Change__**",
#         deckard=True,
#         footer=datetime.now().strftime("%m/%d/%Y %H:%M")
#     ))


# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
bot.start()
