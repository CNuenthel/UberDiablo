import discord
from datetime import datetime, time


def standard_embed(text: str, url: str = None, color: discord.Colour = discord.Colour.og_blurple()):
    """
    Returns a discord embed with a basic textual inclusion
    :param text: String phrase to include in body of embed
    :return: Customized embed object for use with discord.py message class
    """
    base = discord.Embed(
        description=text,
        colour=color
    )
    if url is not None:
        base.add_field(name=url, value="", inline=False)

    return base

