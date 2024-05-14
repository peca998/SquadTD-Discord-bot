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
class Tower(unit.Unit):
    builder: str
    tier: str
    upgrades: list[str]
    cost: int
    supply: float
    predecessors: list[str]


logger = logging.getLogger(__name__)


class TowerCommand(commands.Cog):
    def __init__(self, bot: discord.Bot, filename: Path):
        self.bot = bot
        self.data = self.load_data(filename)

    def load_data(cls, filename: Path) -> dict[str, Tower]:
        ret = {}
        try:
            with open(filename, 'r') as fp:
                data = json.load(fp)
                logger.debug('------- loading towers -------')
                for k, v in data.items():
                    temp = {}
                    temp = unit.load_unit_dict(v)
                    temp['builder'] = v['builder']
                    temp['tier'] = v['tier']
                    temp['upgrades'] = v['upgrades']
                    temp['cost'] = round(v['cost']['minerals'])
                    temp['supply'] = v['cost']['supply']
                    temp['predecessors'] = v['predecessors']
                    ret[k] = Tower(**temp)
                    logger.debug(ret)
        except OSError:
            logger.error('failed to load %s', str(filename))
            sys.exit(1)
        return ret

    def get_cost(self, t: Tower) -> int:
        total = t.cost
        for p in t.predecessors:
            total -= self.data[p].cost
        return total

    def format_upgrades(self, t: Tower) -> str:
        val = ''
        for i, u in enumerate(t.upgrades):
            if i > 0:
                val += ', '
            val += f'{self.data[u].name}'
        return val

    @commands.slash_command(guild_ids=[767297341455073290], name='tower')
    @discord.option('name', description='enter name of the tower')
    async def tower(self, ctx: discord.ApplicationContext, name: str):
        if name.lower() in self.data:
            resp = self.get_response(name)
            await ctx.respond(embed=resp)
        else:
            possible = difflib.get_close_matches(name.lower(), self.data.keys(), n=3, cutoff=0.55)
            if possible:
                closest = possible[0]
                resp = self.get_response(closest)
                await ctx.respond(embed=resp)
            else:
                await ctx.respond(f'There is no tower named **{name}**')

    def get_response(self, name: str) -> discord.Embed:
        ref = self.data[name]
        info = ''
        e = discord.Embed(
            color=discord.Color.blue(),
            description=f'*{ref.builder}, Tier {ref.tier}\n{ref.armor}, {ref.wpn.dmg_type}*',
            title=f'{ref.name}'
        )
        info += '__**Basic Info**__\n'
        info += f'**Cost: ** {self.get_cost(ref)} minerals\n'
        info += f'**Total Cost: ** {ref.cost} minerals\n'
        info += f'**Supply: ** {-ref.supply}\n'
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
        if len(ref.upgrades) > 0:
            info += '\n\n__**Upgrades:**__ '
            info += self.format_upgrades(ref)
        e.add_field(name='\u200b', value=info)
        return e


def setup(bot: discord.Bot):
    file = Path(__file__).parent.parent / 'data/towers.json'
    bot.add_cog(TowerCommand(bot, file))
