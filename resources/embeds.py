import discord
from datetime import datetime, time


def standard_embed(text: str,
                   title="",
                   deckard = False,
                   url: str = None,
                   color: discord.Colour = discord.Colour.og_blurple(),
                   footer: str = None,
                   image: str = None
                   ):
    """
    Returns a discord embed with a basic textual inclusion
    :param text: String phrase to include in body of embed
    :return: Customized embed object for use with discord.py message class
    """
    base = discord.Embed(
        description=text,
        colour=color,
        title=title
    )
    if url is not None:
        base.add_field(name=url, value="", inline=False)

    if deckard:
        base.set_author(
            name="Deckard Cain",
            icon_url="https://static.wikia.nocookie.net/diablo/images/4/4e/Cain_Portrait.png/revision/latest?cb=20180811161630")
    else:
        base.set_author(
            name="UberDiablo",
            icon_url="https://www.giantbomb.com/a/uploads/scale_small/15/155745/2263101-diablo_head________.jpg"
        )

    if footer:
        base.set_footer(text=footer)

    if image:
        base.set_image(url=image)
    return base


def timer_embed(times_list: list, color: discord.Colour = discord.Colour.og_blurple()):
    base = discord.Embed(
        description=f"**__Upcoming Helltide Times__**",
        colour=color,
        title="**And Listen...**"
    )
    return base