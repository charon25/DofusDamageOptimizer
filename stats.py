from enum import Enum
import json
import os
import re
from typing import Dict
from uuid import uuid1


class Characteristics(str, Enum):
    STRENGTH = 0
    INTELLIGENCE = 1
    LUCK = 2
    AGILITY = 3
    NEUTRAL = 4

class Damages(str, Enum):
    POWER = 9
    BASIC = 5
    CRIT = 8
    EARTH = 0
    FIRE = 1
    WATER = 2
    AIR = 3
    NEUTRAL = 4
    SPELL = 6
    WEAPON = 7
    WEAPON_POWER = 10
    RANGE = 12
    MELEE = 13
    FINAL = 11


class Stats:
    def __init__(self) -> None:
        self.characteristics: Dict[Characteristics, int] = dict()
        self.damages: Dict[Characteristics, int] = dict()
        self.bonus_crit_chance = 0.0
        self.name = ''
        self.short_name = ''

        self._fill_empty_dicts()

    def _fill_empty_dicts(self):
        for characteristic in Characteristics:
            self.characteristics[characteristic] = 0

        for damage in Damages:
            self.damages[damage] = 0

    def to_dict(self):
        return {
            'characteristics': self.characteristics,
            'damages': self.damages,
            'bonus_crit_chance': self.bonus_crit_chance,
            'name': self.name,
            'short_name': self.short_name
        }

    def to_compact_string(self, indentation: str = ''):
        output_lines = []
        characteristic_lines = []
        for characteristic in Characteristics:
            if characteristic == Characteristics.NEUTRAL:
                continue
            if self.get_characteristic(characteristic) != 0:
                characteristic_lines.append(f'{indentation * 2}{characteristic.name}: {self.get_characteristic(characteristic)}')
        if characteristic_lines:
            output_lines.append(f'{indentation}-> Characteristics')
            output_lines.extend(characteristic_lines)

        damage_lines = []
        for damage in Damages:
            if self.get_damage(damage) != 0:
                damage_lines.append(f'{indentation * 2}{damage.name}: {self.get_damage(damage)}')
        if damage_lines:
            output_lines.append(f'{indentation}-> Damages')
            output_lines.extend(damage_lines)

        if self.bonus_crit_chance > 0.0:
            output_lines.append(f'{indentation}-> Bonus crit chance: {100 * self.bonus_crit_chance:.0f} %')

        return '\n'.join(output_lines) if output_lines else None


    def save_to_file(self, filepath):
        json_valid_data = self.to_dict()

        with open(filepath, 'w', encoding='utf-8') as fo:
            json.dump(json_valid_data, fo)


    def __add__(self, other: 'Stats'):
        if isinstance(other, int):  # Useful when doing stats + sum([]) - No matter the integer, return the stats
            return Stats.from_existing(self)
        elif not isinstance(other, Stats):
            raise TypeError(f"unsupported operand type(s) for +: 'Stats' and '{type(other)}'.")

        result = Stats()
        for characteristic in Characteristics:
            if characteristic != Characteristics.NEUTRAL:
                result.characteristics[characteristic] = self.characteristics[characteristic] + other.characteristics[characteristic]

        for damage in Damages:
            result.damages[damage] = self.damages[damage] + other.damages[damage]

        result.bonus_crit_chance = self.bonus_crit_chance + other.bonus_crit_chance
        result.name = self.name

        return result

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self + other


    def get_characteristic(self, characteristic):
        if not isinstance(characteristic, Characteristics):
            raise TypeError(f"'{characteristic} is not a valid characteristic.")

        return self.characteristics[characteristic]

    def set_characteristic(self, characteristic, value):
        if not isinstance(characteristic, Characteristics):
            raise TypeError(f"'{characteristic} is not a valid characteristic.")

        if characteristic == Characteristics.NEUTRAL:
            raise TypeError('Neutral caracteritics cannot be changed on its own.')

        if not isinstance(value, int):
            raise TypeError(f"Value should be an int ('{value}' of type '{type(value)}' given instead).")

        self.characteristics[characteristic] = value

        if characteristic == Characteristics.STRENGTH:
            self.characteristics[Characteristics.NEUTRAL] = value


    def get_damage(self, damage):
        if not isinstance(damage, Damages):
            raise TypeError(f"'{damage} is not a valid damage.")

        return self.damages[damage]

    def set_damage(self, damage, value):
        if not isinstance(damage, Damages):
            raise TypeError(f"'{damage}' is not a valid damage.")

        if not isinstance(value, int):
            raise TypeError(f"Value should be an int ('{value}' of type '{type(value)}' given instead).")

        self.damages[damage] = value


    def get_bonus_crit_chance(self):
        return self.bonus_crit_chance

    def set_bonus_crit_chance(self, bonus_crit_chance):
        if not (isinstance(bonus_crit_chance, float) or isinstance(bonus_crit_chance, int)):
            raise TypeError(f"Bonus crit chance is not a float ('{bonus_crit_chance}' of type '{type(bonus_crit_chance)}' given instead).")

        if not (0.0 <= bonus_crit_chance <= 1.0):
            raise ValueError(f"Bonus crit chance should be between 0 and 1 inclusive ('{bonus_crit_chance}' given instead).")

        self.bonus_crit_chance = float(bonus_crit_chance)

    def get_name(self):
        return self.name

    def set_name(self, name):
        if name == '':
            name = 'Unnamed stats'

        self.name = str(name)


    def get_short_name(self):
        return self.short_name

    def get_safe_name(self):
        return re.sub(r'\W', '_', self.short_name)

    def set_short_name(self, short_name):
        if short_name == '':
            short_name = str(uuid1())

        self.short_name = str(short_name)


    def copy(self):
        return Stats.from_existing(self)

    @classmethod
    def from_existing(cls, other_stats: 'Stats'):
        # This function does not use the getters and setters to minimize the execution time
        stats = Stats()

        for characteristic in Characteristics:
            stats.characteristics[characteristic] = other_stats.characteristics[characteristic]

        for damage in Damages:
            stats.damages[damage] = other_stats.damages[damage]

        stats.bonus_crit_chance = other_stats.bonus_crit_chance
        stats.name = other_stats.name
        stats.short_name = other_stats.short_name

        return stats


    @classmethod
    def check_json_validity(cls, json_data):
        for key in ('characteristics', 'damages', 'name', 'bonus_crit_chance', 'short_name'):
            if not key in json_data:
                raise KeyError(f"JSON string does not contain a '{key}' key.")

        for characteristic in Characteristics:
            if not characteristic in json_data['characteristics']:
                raise KeyError(f"JSON string 'characteristics' array does not contains '{characteristic}'.")

        if json_data['characteristics'][Characteristics.NEUTRAL] != json_data['characteristics'][Characteristics.STRENGTH]:
            raise ValueError("Neutral and Strength characteristics have to be equal.")

        for damage in Damages:
            if not damage in json_data['damages']:
                raise KeyError(f"JSON string 'damages' array does not contains '{damage}'.")

    @classmethod
    def from_json_string(cls, json_string):
        json_data = json.loads(json_string)
        Stats.check_json_validity(json_data)

        stats = Stats()

        for characteristic in Characteristics:
            if characteristic != Characteristics.NEUTRAL:
                stats.set_characteristic(characteristic, json_data['characteristics'][characteristic])

        for damage in Damages:
            stats.set_damage(damage, json_data['damages'][damage])

        stats.set_bonus_crit_chance(json_data['bonus_crit_chance'])
        stats.set_name(json_data['name'])
        stats.set_short_name(json_data['short_name'])

        return stats

    @classmethod
    def from_file(cls, filepath):
        if not (os.path.isfile(filepath) and os.access(filepath, os.R_OK)):
            raise FileNotFoundError(f"Cannot create stats from file {filepath}: file not found or innaccessible.")

        with open(filepath, 'r', encoding='utf-8') as fi:
            json_string = fi.read()

        return Stats.from_json_string(json_string)

    @classmethod
    def from_dict(cls, data):
        return Stats.from_json_string(json.dumps(data))
