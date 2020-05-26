import logging
from typing import List, Optional

from black import format_str, FileMode

logger = logging.getLogger(__name__)

TOKEN = "```"

PY_LANGS = ("py", "python")


MODE = FileMode()


class Block:
    def blacken(self):
        pass


class TextBlock(Block):
    __slots__ = ("body",)

    def __init__(self, body: str):
        self.body = body

    def __str__(self):
        return self.body


class CodeBlock(Block):
    __slots__ = ("lang", "body")

    def __init__(self, lang: str, body: str):
        self.lang = lang.strip()
        self.body = body

    def __repr__(self):
        return "<{0} lang={1!r} body={2!r}>".format(
            self.__class__.__name__, self.lang, self.body[:20]
        )

    def __str__(self):
        body = "{token}{lang}\n{body}\n{token}".format(
            token=TOKEN, lang=self.lang, body=self.body,
        )
        return body

    def blacken(self) -> bool:
        if self.lang and self.lang.lower() not in PY_LANGS:
            return

        # TODO: best guess?
        if not self.lang:
            return

        # at this point - yes, it's probably python
        old_body = self.body
        try:
            reformatted = format_str(self.body, mode=MODE)
            self.body = reformatted.strip()
        except Exception:
            logger.exception("Formatting failed")
            return False

        return old_body != self.body  # indicate if it was changed


def parse_codeblocks(body: str, force_py=False) -> Optional[List[Block]]:
    if TOKEN not in body:
        return None

    # malformatted markup - don't bother, every three backticks need to be matched by
    # another closing set
    if body.count(TOKEN) % 2 != 0:
        return None

    blocks = []

    # scan string
    text_lines = []
    lines = []
    in_codeblock = False
    language = ""

    for line in body.splitlines():
        if not in_codeblock:
            #  start of a code block
            if line.startswith(TOKEN):
                in_codeblock = True
                language = line[len(TOKEN) :].strip()
                if not language and force_py:
                    language = "py"
                lines = []

                if text_lines:
                    blocks.append(TextBlock(body="\n".join(text_lines)))
                    text_lines = []

            # regular text
            else:
                text_lines.append(line)
        else:
            # clean up - end of code block
            if line.startswith(TOKEN):
                in_codeblock = False
                body = "\n".join(lines)
                blocks.append(CodeBlock(lang=language, body=body))

            # regular line of code
            else:
                lines.append(line)

    if text_lines:
        blocks.append(TextBlock(body="\n".join(text_lines)))
    return blocks
