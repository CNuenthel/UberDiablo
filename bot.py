"""
Limitations:
    Use of a saved file system to record user_id data within concurrent discord command
    usage allows for possible errors on attempts to access the same folder due to simultaneous
    commands being issued or bot operations involving the folder

    If a player activates the helltide opt in command while the bot is simultaneously accessing
    the datafile to issue notifications, it is possible to prevent either operation from
    accessing the file. Unlikely but not impossible.
"""


# Package Imports
import asyncio
import json
from discord.ext import commands, tasks
import discord
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


# ----------------------------------------------------------------------------------------------------------------------
# TASKS


@tasks.loop(minutes=135)
async def timer_task():
    """
    Activates the notification operation of all opt-in players that helltide is about to begin. Will activate 2h15m
    from start time provided and continuously loop thereafter
    :return: None
    """
    await notify_players()


# ----------------------------------------------------------------------------------------------------------------------
# BASE FUNCTIONS


def load_file(filename: str):
    """
    I'm just sick of writing this, so it's a function. Imagine that.
    :return: json dict
    """
    with open(filename, "r") as f:
        return json.load(f)


def save_file(filename: str, data: dict):
    """
    Saves given data to given filename
    :param filename: Filename to manipulate data from
    :param data: json formatted dictionary
    :return: None
    """
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def user_in_opt_board(user_id: str, filename: str = "resources/optin-db.json"):
    """
    Checks for a given user id in optin database
    :param user_id: String - discord user id from message context
    :param filename: Filename to manipulate data from
    :return: None
    """
    data = load_file(filename)

    if user_id in data["opted_in"]:
        return True
    return False


def opt_in(user_id: str, filename: str = "resources/optin-db.json"):
    """
    Adds Discord user id to opt-in database
    :param user_id: Discord user id
    :param filename: Filename to manipulate data from
    :return: None
    """
    data = load_file(filename)

    if user_id not in data["opted_in"]:
        data["opted_in"].append(user_id)

    save_file(filename, data)


def opt_out(user_id: str, filename: str = "resources/optin-db.json"):
    """
    Removes Discord user id from opt-in database
    :param user_id: Discord user id
    :param filename: Filename to manipulate data from
    :return: None
    """
    data = load_file(filename)

    if user_id in data["opted_in"]:
        data["opted_in"].remove(user_id)

    save_file(filename, data)


async def notify_players():
    """
    Notify opt-in players that helltide is about to begin through direct message
    :return: None
    """
    filename = "resources/optin-db.json"
    data = load_file(filename)

    for user_id in data["opted_in"]:
        if user_id == "test" or user_id == "test_user_id":
            continue

        discord_user = bot.get_user(user_id)
        await discord_user.send(
            embed=embeds.standard_embed("Helltide will begin soon", "http://diablo4.life/trackers/helltide"))


# ----------------------------------------------------------------------------------------------------------------------
# BOT COMMANDS

@bot.command(aliases=[])
async def helltide(ctx):
    """
    Allows a discord user to opt in to helltide reminders through direct message.
    :param ctx: Discord message context
    :return: None
    """
    author = ctx.message.author
    if not user_in_opt_board(author.id):
        msg = await ctx.send(
            embed=embeds.standard_embed(
                "React to opt in to Helltide notifications.", color=discord.Color.green()))
        await msg.add_reaction("✅")

        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=15)

            if reaction.emoji == "✅" and user.id == author.id:
                opt_in(author.id)
                await msg.delete()
                await ctx.send(
                    embed=embeds.standard_embed(
                        f"You have been added to the notification list, {author.name.title()[:-4]}", color=discord.Color.green()))
                return

        except asyncio.TimeoutError:
            await msg.delete()
            return

    msg = await ctx.send(
        embed=embeds.standard_embed(
            "React to opt out of helltide notifications.", color=discord.Color.red()))
    await msg.add_reaction("❌")

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=15)

        if reaction.emoji == "❌" and user.id == author.id:
            opt_out(author.id)
            await msg.delete()
            await ctx.send(
                embed=embeds.standard_embed(
                    f"You have been removed from the notification list, {author.name.title()[:-4]}", color=discord.Color.red()))
            return

    except asyncio.TimeoutError:
        await msg.delete()
        return


@bot.command(aliases=["hts"])
async def helltide_start(ctx):
    """
    Starts the helltide timer task
    :param ctx: Discord message context
    :return: None
    """
    timer_task.start()

    now = datetime.now()
    then = now+timedelta(minutes=135)
    now_formatted = now.strftime("%H:%M")
    then_formatted = then.strftime("%H:%M")

    await ctx.send(embed=embeds.standard_embed(
        f"The timer was started at {now_formatted}. The next notification will be at {then_formatted}")
    )


@bot.command(aliases=["notest"])
async def notification_test(ctx):
    """
    Activates notification for helltide opt in users regardless of timer setting
    :param ctx: Discord message context
    :return: None
    """
    if ctx.author.id == 208970082594848771:
        await notify_players()

# ----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    bot.run(config["token"])
