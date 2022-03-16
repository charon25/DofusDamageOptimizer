from enum import Enum
import json
from typing import Dict


class Characteristics(str, Enum):
    STRENGTH = 0
    INTELLIGENCE = 1
    LUCK = 2
    AGILITY = 3
    NEUTRAL = 4

class Damages(str, Enum):
    EARTH = 0
    FIRE = 1
    WATER = 2
    AIR = 3
    NEUTRAL = 4
    BASIC = 5
    SPELLS = 6
    WEAPON = 7
    CRIT = 8
    POWER = 9
    WEAPON_POWER = 10


class Stats:
    def __init__(self) -> None:
        self.characteristics: Dict[Characteristics, int] = {}
        self.damages: Dict[Characteristics, int] = {}
        self.name = ''

        self._fill_empty_dicts()
    
    def _fill_empty_dicts(self):
        for characteristic in Characteristics:
            self.characteristics[characteristic] = 0
        
        for damage in Damages:
            self.damages[damage] = 0
    
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

        if value < 0:
            raise ValueError(f"Value should be non negative ('{value}' given instead).")

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

        if value < 0:
            raise ValueError(f"Value should be non negative ('{value}' given instead).")

        self.damages[damage] = value
    
    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = str(name)


    @classmethod
    def check_json_validity(cls, json_data):
        for key in ('characteristics', 'damages', 'name'):
            if not key in json_data:
                raise KeyError(f"JSON string does not contain a '{key}' key.")

        for characteristic in Characteristics:
            if not characteristic in json_data['characteristics']:
                raise KeyError(f"JSON string 'characteristics' array does not contains '{characteristic}'.")

        if json_data['characteristics'][Characteristics.NEUTRAL] != json_data['characteristics'][Characteristics.STRENGTH]:
            raise ValueError("Neutral and Strength caracteristics have to be equal.")

        for damage in Damages:
            if not damage in json_data['damages']:
                raise KeyError(f"JSON string 'damages' array does not contains '{damage}'.")

    @classmethod
    def from_json_string(cls, json_string):
        json_data = json.loads(json_string)
        cls.check_json_validity(json_data)

        stats = Stats()
        
        for characteristic in Characteristics:
            if characteristic != Characteristics.NEUTRAL:
                stats.set_characteristic(characteristic, json_data['characteristics'][characteristic])
        
        for damage in Damages:
            stats.set_damage(damage, json_data['damages'][damage])
        
        stats.set_name(json_data['name'])

        return stats
