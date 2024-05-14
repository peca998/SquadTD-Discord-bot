import dataclasses
import logging


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Weapon:
    period: float
    targets: int
    wpn_range: float
    dmg_min: int
    dmg_max: int
    dmg_type: str
    melee: bool


@dataclasses.dataclass
class Unit:
    name: str
    wpn: Weapon
    hp: int
    shields: int
    energy: int
    armor: str
    move_speed: float
    abilities: list[str]


def load_unit_wpn_dict(wpn: dict) -> Weapon:
    ret: dict = {}
    ret['period'] = wpn['period']
    ret['targets'] = wpn['targets']
    ret['wpn_range'] = wpn['range']
    ret['dmg_min'] = round(wpn['damage']['min'])
    ret['dmg_max'] = round(wpn['damage']['max'])
    ret['dmg_type'] = wpn['damage']['dmg_type']
    ret['melee'] = wpn['melee']
    return Weapon(**ret)


def load_unit_dict(unit: dict) -> dict:
    """
    load into memory only fields we need for bot
    """
    ret: dict = {}
    ret['name'] = unit['name']
    ret['hp'] = round(unit['hp'])
    ret['shields'] = round(unit['shields'])
    ret['energy'] = round(unit['energy'])
    ret['armor'] = unit['armor']
    ret['move_speed'] = unit['move_speed']
    ret['abilities'] = unit['abilities']
    ret['wpn'] = load_unit_wpn_dict(unit['wpn'])
    return ret
