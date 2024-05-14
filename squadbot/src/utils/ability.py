import dataclasses
import sys
import json
import logging
from pathlib import Path


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Ability:
    name: str
    desc: str


def load_abils() -> dict[str, Ability]:
    file = Path(__file__).parent.parent / 'data/abils.json'
    ret = {}
    logger.debug('------- loading abilities -------')
    try:
        with open(file, 'r') as fp:
            data = json.load(fp)
            for k, v in data.items():
                ret[k] = Ability(**v)
    except OSError:
        logger.error('failed to load %s', str(file))
        sys.exit(1)
    return ret


def format_abilities(abils: list[str]) -> str:
    val = ''
    for i, v in enumerate(abils):
        if i > 0:
            val += '\n'
        val += f'**{_gAbils[v].name}**: '
        val += f'{_gAbils[v].desc}'
    return val


_gAbils = load_abils()
