import logging
import re

import discord

from .formatting import parse_codeblocks, CodeBlock

logger = logging.getLogger(__name__)

client = discord.Client()

FORMAT_REGEX = re.compile(r"format (?P<post>\w+)")


@client.event
async def on_ready():
    logger.info("Ready to format messages.")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # only act on mentions
    if client.user not in message.mentions:
        return

    match = FORMAT_REGEX.search(message.content)
    if match is None:
        return

    post = match.group("post")
    if post == "last":
        msgs = await message.channel.history(limit=2).flatten()
        msg = msgs[1]
    else:
        if not post.isnumeric():
            logger.info(f"{post} is not a number!")
            return
            
        post_id = int(post)
        async for msg in message.channel.history(limit=50):
            if msg.id == post_id:
                break
        else:
            return

    blocks = parse_codeblocks(msg.content, force_py=True)
    if blocks is None:
        # let's just assume it's a code block and try...
        block = CodeBlock(lang="py", body=msg.content)
        block.blacken()
        await message.channel.send(str(block))

    formatted_blocks = []
    for block in blocks:
        if not isinstance(block, CodeBlock):
            continue
        if block.blacken():
            formatted_blocks.append(block)

    if not formatted_blocks:
        await message.channel.send("Looks fine to me, or you provided gibberish!")
        return

    formatted = "\n".join([str(block) for block in formatted_blocks])
    content = "Here, i've blackened the code:\n{}".format(formatted)
    await message.channel.send(content)
