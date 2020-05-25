#!/usr/bin/env python
import os

from dotenv import load_dotenv

from bot.client import client


def main():
    load_dotenv()
    client.run(os.environ["BOT_TOKEN"])


if __name__ == "__main__":
    main()
