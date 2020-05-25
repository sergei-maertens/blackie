import logging

import discord

from .formatting import parse_codeblocks, CodeBlock

logger = logging.getLogger(__name__)

client = discord.Client()

SIZE_CUTOFF = 100


@client.event
async def on_ready():
    logger.info("Ready to format messages.")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # don't bother with short messages
    if len(message.content) < SIZE_CUTOFF:
        return

    blocks = parse_codeblocks(message.content)
    if blocks is None:  # nothing to do
        return

    for block in blocks:
        block.blacken()

    formatted = "\n".join(
        [str(block) for block in blocks if isinstance(block, CodeBlock)]
    )
    if formatted == message.content:  # nothing to do, already formatted properly
        return

    content = "Here, i've blackened the code:\n{}".format(formatted)
    await message.channel.send(content)
