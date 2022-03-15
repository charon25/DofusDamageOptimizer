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

    @classmethod
    def check_json_validity(cls, json_data):
        for key in ('damages', 'crit_chance', 'uses_per_target', 'uses_per_turn'):
            if not key in json_data:
                raise KeyError(f"JSON string does not contain a '{key}' key.")
        
        for characteristic in Characteristics:
            if not characteristic in json_data['damages']:
                raise KeyError(f"JSON string 'damages' array does not contains '{characteristic}'.")
            for field in ('min', 'max', 'crit_min', 'crit_max'):
                if not field in json_data['damages'][characteristic]:
                    raise KeyError(f"Field '{field}' missing in json_data['damages'][{characteristic}].")
        

    @classmethod
    def from_json_string(cls, json_string):
        json_data = json.loads(json_string)
        cls.check_json_validity(json_data)

        stats = Spell(from_scratch=False)
        stats.damages = json_data['damages']

        return stats
