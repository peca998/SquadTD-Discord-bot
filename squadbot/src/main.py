import typing
import os
import logging
from pathlib import Path
import argparse

import dotenv
import discord

logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.members = True
bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    logger.info('Bot started. Username: %s, ID: %s', bot.user, bot.user.id)


def configure_logger(level: int = logging.INFO) -> None:
    logging.basicConfig(format='%(levelname)-8s %(filename)s:%(lineno)-4d %(asctime)s %(message)s', level=level)


def main(args: argparse.Namespace) -> None:
    dotenv.load_dotenv()
    token: typing.Final[str] = os.getenv('DISCORD_TOKEN', '')
    logger.info('------- loading data -------')
    commands = Path(__file__).parent / 'commands'
    for f in commands.iterdir():
        if f.suffix == '.py' and f.stem != '__init__':
            logger.debug('loading %s', f.stem)
            bot.load_extension(f'commands.{f.stem}')
    logger.info('------- finished loading -------')

    bot.run(token=token)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ll', dest='log_level', default='INFO', help='Set the logging level')
    arguments = parser.parse_args()
    configure_logger(arguments.log_level)
    main(arguments)
