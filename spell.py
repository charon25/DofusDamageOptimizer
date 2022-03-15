import json

from stats import Characteristics


class Spell():
    def __init__(self, from_scratch=True) -> None:
        self.damages = {}
        self.crit_chance = 0.0
        self.uses_per_target = -1
        self.uses_per_turn = -1

        if from_scratch:
            self._fill_empty_dict()
    
    def _fill_empty_dict(self):
        for characteristic in Characteristics:
            self.damages[characteristic] = {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0}

    def get_damages(self, characteristic):
        if not isinstance(characteristic, Characteristics):
            raise TypeError(f"'{characteristic} is not a valid characteristic.")
        
        return self.damages[characteristic]
    
    def set_damages(self, characteristic, damages):
        if not isinstance(characteristic, Characteristics):
            raise TypeError(f"'{characteristic} is not a valid characteristic.")
        
        if not isinstance(damages, dict):
            raise TypeError(f"Damages is not a dict ('{damages}' of type '{type(damages)}' given instead).")
        
        for field in ('min', 'max', 'crit_min', 'crit_max'):
            if not field in damages:
                raise KeyError(f"Field '{field}' missing in damages.")
            if not isinstance(damages[field], int):
                raise TypeError(f"Field '{field}' is not an int ('{damages[field]}' of type '{type(damages[field])}' given instead).")
            if damages[field] < 0:
                raise ValueError(f"Field '{field}' should be non negative ('{damages[field]}' given instead).")
        
        self.damages[characteristic] = damages

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


    @classmethod
    def check_json_validity(cls, json_data):
        for key in ('damages', 'crit_chance', 'uses_per_target', 'uses_per_turn'):
            if not key in json_data:
                raise KeyError(f"JSON string does not contain a '{key}' key.")
        
        if not (isinstance(json_data['crit_chance'], float) or isinstance(json_data['crit_chance'], int)):
            raise TypeError(f"json_data['crit_chance'] is not a float ('{json_data['crit_chance']}' of type '{type(json_data['crit_chance'])}' given instead).")
        if not (0.0 <= json_data['crit_chance'] <= 1.0):
            raise ValueError(f"json_data['crit_chance'] should be between 0 and 1 inclusive ('{json_data['crit_chance']}' given instead).")
        
        if not isinstance(json_data['uses_per_target'], int):
            raise TypeError(f"json_data['uses_per_target'] is not a int ('{json_data['uses_per_target']}' of type '{type(json_data['uses_per_target'])}' given instead).")
        if json_data['uses_per_target'] == 0 or json_data['uses_per_target'] < -1:
            raise ValueError(f"json_data['uses_per_target'] should be -1 or a positive int ('{json_data['uses_per_target']}' given instead).")

        if not isinstance(json_data['uses_per_turn'], int):
            raise TypeError(f"json_data['uses_per_turn'] is not a int ('{json_data['uses_per_turn']}' of type '{type(json_data['uses_per_turn'])}' given instead).")
        if json_data['uses_per_turn'] == 0 or json_data['uses_per_turn'] < -1:
            raise ValueError(f"json_data['uses_per_turn'] should be -1 or a positive int ('{json_data['uses_per_turn']}' given instead).")
        
        for characteristic in Characteristics:
            if not characteristic in json_data['damages']:
                raise KeyError(f"JSON string 'damages' array does not contains '{characteristic}'.")
            for field in ('min', 'max', 'crit_min', 'crit_max'):
                if not field in json_data['damages'][characteristic]:
                    raise KeyError(f"Field '{field}' missing in json_data['damages'][{characteristic}].")
                field_value = json_data['damages'][characteristic][field]
                if not isinstance(field_value, int):
                    raise TypeError(f"json_data['damages'][{characteristic}][{field}] is not an int ('{field_value}' of type '{type(field_value)}' given instead).")
                if field_value < 0:
                    raise ValueError(f"json_data['damages'][{characteristic}][{field}] should be non negative ('{field_value}' given instead).")
        

    @classmethod
    def from_json_string(cls, json_string):
        json_data = json.loads(json_string)
        cls.check_json_validity(json_data)

        stats = Spell(from_scratch=False)
        stats.damages = json_data['damages']
        stats.crit_chance = float(json_data['crit_chance'])
        stats.uses_per_target = json_data['uses_per_target']
        stats.uses_per_turn = json_data['uses_per_turn']

        return stats
