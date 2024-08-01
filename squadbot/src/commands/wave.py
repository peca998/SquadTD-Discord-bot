import dataclasses
import json
from pathlib import Path
import logging
import sys
import difflib

import discord
from discord.ext import commands

from squadbot.src.utils import unit, ability


@dataclasses.dataclass
class Wave(unit.Unit):
    index: int
    bounty: float
    count: int


logger = logging.getLogger(__name__)


class WaveCommand(commands.Cog):
    def __init__(self, bot: discord.Bot, filename: Path):
        self.bot = bot
        self.data = self.load_data(filename)

    def load_data(cls, filename: Path) -> dict[str, Wave]:
        ret = {}
        try:
            with open(filename, 'r') as fp:
                data = json.load(fp)
                logger.debug('------- loading waves -------')
                for k, v in data.items():
                    temp = {}
                    temp = unit.load_unit_dict(v)
                    temp['bounty'] = v['bounty']
                    temp['index'] = v['index']
                    temp['count'] = v['count']
                    ret[str(temp['index'])] = Wave(**temp)
                    logger.debug(ret)
        except OSError:
            logger.error('failed to load %s', str(filename))
            sys.exit(1)
        return ret

    @commands.slash_command(guild_ids=[543294798430339102], name='wave', description='provides wave info')
    @discord.option('num', description='enter wave number')
    @discord.option(
        name='non_adr',
        description='enable this to show non-adrenaline info',
        required=False,
        choices=[True]
    )
    @discord.option(
        name='x1',
        description='enable this to show 1x count',
        required=False,
        choices=[True]
    )
    async def wave(self, ctx: discord.ApplicationContext, num: str, non_adr: bool = False, x1: bool = False):
        if num.lower() in self.data:
            resp = self.get_response(num, non_adr, x1)
            await ctx.respond(embed=resp)
        else:
            possible = difflib.get_close_matches(num.lower(), self.data.keys(), n=3, cutoff=0.7)
            if possible:
                closest = possible[0]
                resp = self.get_response(closest, non_adr, x1)
                await ctx.respond(embed=resp)
            else:
                await ctx.respond(f'There is no wave named **{num}**')

    def get_response(self, name: str, non_adr: bool = True, x1: bool = True) -> discord.Embed:
        ref = self.data[name]
        info = ''
        e = discord.Embed(
            color=discord.Color.blue(),
            description=f'*{ref.name}\n{ref.armor}, {ref.wpn.dmg_type}*',
            title=f'Wave {ref.index} ({"Non-adrenaline" if non_adr else "Adrenaline"})'
        )
        info += '__**Basic Info**__\n'
        info += f'**Count ({"1x" if x1 else "3x"}): **{round(ref.count / 3) if x1 else ref.count}\n'
        info += f'**Bounty: **{ref.bounty} minerals\n'
        info += f'**Speed: **{ref.move_speed}\n'
        info += f'**HP: **{ref.hp if non_adr else round(ref.hp * (1+0.02*ref.index))}\n'
        if ref.shields > 0:
            info += f'**Shields: **{ref.shields}\n'
        if ref.energy > 0:
            info += f'**Energy: **{ref.energy}\n'
        info += '\n__**Weapon**__\n'
        info += f'**Damage: **{ref.wpn.dmg_min if non_adr else round(ref.wpn.dmg_min * (1+0.02*ref.index))}-{ref.wpn.dmg_max if non_adr else round(ref.wpn.dmg_max*(1+0.02*ref.index))}\n'
        info += f'**Attack Speed: **{ref.wpn.period if non_adr else round(ref.wpn.period/1.01**ref.index, 2)}\n'
        info += f'**Range: **{ref.wpn.wpn_range}\n'
        if len(ref.abilities) > 0:
            info += '\n__**Abilities**__\n'
            info += f'{ability.format_abilities(ref.abilities)}'
        e.add_field(name='\u200b', value=info)
        return e


def setup(bot: discord.Bot):
    file = Path(__file__).parent.parent / 'data/waves.json'
    bot.add_cog(WaveCommand(bot, file))
