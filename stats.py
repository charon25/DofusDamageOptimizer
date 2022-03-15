from enum import Enum
import json

class Elements(str, Enum):
    STRENGTH = 0
    INTELLIGENCE = 1
    LUCK = 2
    AGILITY = 3
    POWER = 4

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
        self.elements = {}
        self.damages = {}

        if from_scratch:
            self._fill_empty_dicts()
    
    def _fill_empty_dicts(self):
        for element in Elements:
            self.elements[element] = 0
        
        for damage in Damages:
            self.damages[damage] = 0


    @classmethod
    def from_json_string(self, json_string):
        json_data = json.loads(json_string)
        stats = Stats(from_scratch=False)
        stats.elements = json_data['elements']
        stats.damages = json_data['damages']

        return stats
