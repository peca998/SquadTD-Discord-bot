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
class Send(unit.Unit):
    bounty: float
    income: float
    cost: int


logger = logging.getLogger(__name__)


class SendCommand(commands.Cog):
    def __init__(self, bot: discord.Bot, filename: Path):
        self.bot = bot
        self.data = self.load_data(filename)

    def load_data(cls, filename: Path) -> dict[str, Send]:
        ret = {}
        try:
            with open(filename, 'r') as fp:
                data = json.load(fp)
                logger.debug('------- loading sends -------')
                for k, v in data.items():
                    temp = {}
                    temp = unit.load_unit_dict(v)
                    temp['bounty'] = v['bounty']
                    temp['income'] = v['income']
                    temp['cost'] = round(v['cost']['vespene'])
                    ret[k] = Send(**temp)
                    logger.debug(ret)
        except OSError:
            logger.error('failed to load %s', str(filename))
            sys.exit(1)
        return ret

    @commands.slash_command(guild_ids=[767297341455073290], name='send')
    @discord.option('name', description='enter name of the send')
    async def send(self, ctx: discord.ApplicationContext, name: str):
        if name.lower() in self.data:
            resp = self.get_response(name)
            await ctx.respond(embed=resp)
        else:
            possible = difflib.get_close_matches(name.lower(), self.data.keys(), n=3, cutoff=0.7)
            if possible:
                closest = possible[0]
                resp = self.get_response(closest)
                await ctx.respond(embed=resp)
            else:
                await ctx.respond(f'There is no send named **{name}**')

    def get_response(self, name: str) -> discord.Embed:
        ref = self.data[name]
        info = ''
        e = discord.Embed(
            color=discord.Color.blue(),
            description=f'*Send\n{ref.armor}, {ref.wpn.dmg_type}*',
            title=f'{ref.name}'
        )
        info += '__**Basic Info**__\n'
        info += f'**Cost: ** {ref.cost} vespene\n'
        info += f'**Bounty: **{ref.bounty} minerals\n'
        info += f'**Income: **{ref.income}\n'
        info += f'**Speed: **{ref.move_speed}\n'
        info += f'**HP: **{ref.hp}\n'
        if ref.shields > 0:
            info += f'**Shields: **{ref.shields}\n'
        if ref.energy > 0:
            info += f'**Energy: **{ref.energy}\n'
        info += '\n__**Weapon**__\n'            
        info += f'**Damage: **{ref.wpn.dmg_min}-{ref.wpn.dmg_max}\n'
        info += f'**Attack Speed: **{ref.wpn.period}\n'
        info += f'**Range: **{ref.wpn.wpn_range}\n'
        if len(ref.abilities) > 0:
            info += '\n__**Abilities**__\n'
            info += f'{ability.format_abilities(ref.abilities)}'
        e.add_field(name='\u200b', value=info)
        return e

def setup(bot: discord.Bot):
    file = Path(__file__).parent.parent / 'data/sends.json'
    bot.add_cog(SendCommand(bot, file))
