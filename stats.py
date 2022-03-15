from enum import Enum
import json


class Characteristics(str, Enum):
    STRENGTH = 0
    INTELLIGENCE = 1
    LUCK = 2
    AGILITY = 3
    POWER = 4
    WEAPON_POWER = 5

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


class Stats:
    def __init__(self, from_scratch=True) -> None:
        self.characteristics = {}
        self.damages = {}

        if from_scratch:
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

        if not isinstance(value, int):
            raise TypeError(f"Value should be an int ('{value}' of type '{type(value)}' given).")

        if value < 0:
            raise ValueError(f"Value should be non negative ('{value}' given).")

        self.characteristics[characteristic] = value


    @classmethod
    def check_json_validity(cls, json_data):
        if not 'characteristics' in json_data:
            raise ValueError(f"JSON string does not contain an 'characteristics' key.")

        for characteristic in Characteristics:
            if not characteristic in json_data['characteristics']:
                raise ValueError(f"JSON string 'characteristics' array does not contains '{characteristic}'.")
        
        if not 'damages' in json_data:
            raise ValueError("JSON string does not contain a 'damages' key.")

        for damage in Damages:
            if not damage in json_data['damages']:
                raise ValueError(f"JSON string 'damages' array does not contains '{damage}'.")

    @classmethod
    def from_json_string(cls, json_string):
        json_data = json.loads(json_string)
        cls.check_json_validity(json_data)

        stats = Stats(from_scratch=False)
        stats.characteristics = json_data['characteristics']
        stats.damages = json_data['damages']

        return stats
