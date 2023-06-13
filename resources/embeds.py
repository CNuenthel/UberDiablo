import discord
from datetime import datetime, time
import interactions

def standard_embed(text: str = "",
                   title="",
                   deckard=False,
                   url=None,
                   color: interactions.Color = interactions.Color.from_hex("#0A20EB"),
                   footer: str = None,
                   image: str = None
                   ):
    """
    Returns a discord embed with a basic textual inclusion
    :param text: String phrase to include in body of embed
    :return: Customized embed object for use with discord.py message class
    """
    base = interactions.Embed(
        description=text,
        color=color,
        title=title
    )
    if url:
        base.add_field(name=url, value=" ")

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

