import json
from typing import Dict

from damages import compute_damage
from stats import Characteristics, Stats


class Spell():
    def __init__(self, from_scratch=True) -> None:
        self.base_damages: Dict[Characteristics, Dict] = {}
        self.pa = 1
        self.crit_chance = 0.0
        self.uses_per_target = -1
        self.uses_per_turn = -1
        self.is_melee = False
        self.name = ''
        self.short_name = ''

        if from_scratch:
            self._fill_empty_dict()
    
    def _fill_empty_dict(self):
        for characteristic in Characteristics:
            self.base_damages[characteristic] = {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0}

    def get_average_damages(self, stats: Stats):
        average_damage = 0.0
        average_damage_crit = 0.0

        for characteristic in Characteristics:
            min_damage = compute_damage(self.base_damages[characteristic]['min'], stats, characteristic, is_melee=self.is_melee)
            max_damage = compute_damage(self.base_damages[characteristic]['max'], stats, characteristic, is_melee=self.is_melee)
            average_damage += (min_damage + max_damage) / 2

            min_damage_crit = compute_damage(self.base_damages[characteristic]['crit_min'], stats, characteristic, is_melee=self.is_melee, is_crit=True)
            max_damage_crit = compute_damage(self.base_damages[characteristic]['crit_max'], stats, characteristic, is_melee=self.is_melee, is_crit=True)
            average_damage_crit += (min_damage_crit + max_damage_crit) / 2

        final_crit_chance = self.crit_chance + stats.bonus_crit_chance
        if final_crit_chance > 1.0:
            final_crit_chance = 1.0

        return (1 - final_crit_chance) * average_damage + final_crit_chance * average_damage_crit

    
    def save_to_file(self, filepath):
        json_valid_data = {
            'base_damages': self.base_damages,
            'pa': self.pa,
            'crit_chance': self.crit_chance,
            'uses_per_target': self.uses_per_target,
            'uses_per_turn': self.uses_per_turn,
            'is_melee': self.is_melee,
            'name': self.name,
            'short_name': self.short_name
        }
        json.dump(json_valid_data, open(filepath, 'w', encoding='utf-8'))


    def get_pa(self):
        return self.pa
    
    def set_pa(self, pa):
        if not isinstance(pa, int):
            raise TypeError(f"PA count is not an int ('{pa}' of type '{type(pa)}' given instead).")
        if pa <= 0:
            raise ValueError(f"PA count should be a positive int ('{pa}' given instead).")
        
        self.pa = pa


    def get_base_damages(self, characteristic):
        if not isinstance(characteristic, Characteristics):
            raise TypeError(f"'{characteristic} is not a valid characteristic.")
        
        return self.base_damages[characteristic]
    
    def set_base_damages(self, characteristic, base_damages):
        if not isinstance(characteristic, Characteristics):
            raise TypeError(f"'{characteristic} is not a valid characteristic.")
        
        if not isinstance(base_damages, dict):
            raise TypeError(f"base_damages is not a dict ('{base_damages}' of type '{type(base_damages)}' given instead).")
        
        for field in ('min', 'max', 'crit_min', 'crit_max'):
            if not field in base_damages:
                raise KeyError(f"Field '{field}' missing in base_damages.")
            if not isinstance(base_damages[field], int):
                raise TypeError(f"Field '{field}' is not an int ('{base_damages[field]}' of type '{type(base_damages[field])}' given instead).")
            if base_damages[field] < 0:
                raise ValueError(f"Field '{field}' should be non negative ('{base_damages[field]}' given instead).")
        
        self.base_damages[characteristic] = base_damages


    def get_crit_chance(self):
        return self.crit_chance

    def set_crit_chance(self, crit_chance):
        if not (isinstance(crit_chance, float) or isinstance(crit_chance, int)):
            raise TypeError(f"Crit chance is not a float ('{crit_chance}' of type '{type(crit_chance)}' given instead).")

        if not (0.0 <= crit_chance <= 1.0):
            raise ValueError(f"Crit chance should be between 0 and 1 inclusive ('{crit_chance}' given instead).")

        self.crit_chance = float(crit_chance)


    def get_uses_per_target(self):
        return self.uses_per_target

    def set_uses_per_target(self, uses_per_target):
        if not isinstance(uses_per_target, int):
            raise TypeError(f"Uses per target is not a int ('{uses_per_target}' of type '{type(uses_per_target)}' given instead).")
        if uses_per_target == 0 or uses_per_target < -1:
            raise ValueError(f"Uses per target should be -1 or a positive int ('{uses_per_target}' given instead).")
        
        self.uses_per_target = uses_per_target


    def get_uses_per_turn(self):
        return self.uses_per_turn

    def set_uses_per_turn(self, uses_per_turn):
        if not isinstance(uses_per_turn, int):
            raise TypeError(f"Uses per turn is not a int ('{uses_per_turn}' of type '{type(uses_per_turn)}' given instead).")
        if uses_per_turn == 0 or uses_per_turn < -1:
            raise ValueError(f"Uses per turn should be -1 or a positive int ('{uses_per_turn}' given instead).")
        
        self.uses_per_turn = uses_per_turn


    def set_melee(self, is_melee):
        if not (isinstance(is_melee, bool) or (isinstance(is_melee, int) and is_melee in [0, 1])):
            raise TypeError(f"is_melee is not a bool ('{is_melee}' of type '{type(is_melee)}' given instead).")
        
        self.is_melee = bool(is_melee)


    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = str(name)


    def get_short_name(self):
        return self.short_name
    
    def set_short_name(self, short_name):
        self.short_name = str(short_name)



    @classmethod
    def check_json_validity(cls, json_data):
        for key in ('base_damages', 'pa', 'crit_chance', 'uses_per_target', 'uses_per_turn', 'is_melee', 'name', 'short_name'):
            if not key in json_data:
                raise KeyError(f"JSON string does not contain a '{key}' key.")
        
        for characteristic in Characteristics:
            if not characteristic in json_data['base_damages']:
                raise KeyError(f"JSON string 'base_damages' array does not contains '{characteristic}'.")

    @classmethod
    def from_json_string(cls, json_string):
        json_data = json.loads(json_string)
        cls.check_json_validity(json_data)

        spell = Spell(from_scratch=False)
        for characteristic in Characteristics:
            spell.set_base_damages(characteristic, json_data['base_damages'][characteristic])
        spell.set_pa(json_data['pa'])
        spell.set_crit_chance(json_data['crit_chance'])
        spell.set_uses_per_target(json_data['uses_per_target'])
        spell.set_uses_per_turn(json_data['uses_per_turn'])
        spell.set_melee(json_data['is_melee'])
        spell.set_name(json_data['name'])
        spell.set_short_name(json_data['short_name'])

        return spell

    @classmethod
    def from_file(cls, filepath):
        with open(filepath, 'r', encoding='utf-8') as fi:
            json_string = fi.read()
        return Spell.from_json_string(json_string)
