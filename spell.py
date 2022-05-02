from dataclasses import dataclass, field, replace
import json
import os
import re
from typing import Dict, List, Set, Tuple

from damages import compute_damage
from damages_parameters import DamageParameters
from stats import Characteristics, Stats


@dataclass
class SpellOutput:
    damages: Dict[str, int] = field(default_factory=lambda: {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0})
    stats: Dict[str, Stats] = field(default_factory=lambda: {'__all__': Stats()})
    parameters: Dict[str, DamageParameters] = field(default_factory=lambda: {'__all__': DamageParameters()})
    states: Set[str] = field(default_factory=lambda: {})

    def update_stats(self, new_stats: Dict[str, Stats]):
        for name in new_stats:
            self.stats[name] += new_stats[name]

    def update_parameters(self, new_parameters: Dict[str, DamageParameters]):
        for name in new_parameters:
            self.parameters[name] += new_parameters[name]


@dataclass
class SpellParameters:
    base_damages: Dict[Characteristics, Dict[str, int]] = field(default_factory=lambda: {})
    pa: int = 1
    crit_chance: float = 0.0
    uses_per_target: int = -1
    uses_per_turn: int = -1
    is_weapon: bool = False
    po: Tuple[int, int] = field(default_factory=lambda: (0, 1024))


    def get_max_uses_single_target(self, max_used_pa: int) -> int:
        if self.uses_per_target == -1:
            return max_used_pa // self.pa
        else:
            return min(max_used_pa // self.pa, self.uses_per_target)

    def get_max_uses_multiple_targets(self, max_used_pa: int) -> int:
        if self.uses_per_turn == -1:
            return max_used_pa // self.pa
        else:
            return min(max_used_pa // self.pa, self.uses_per_turn)


class SpellBuff:
    def __init__(self) -> None:
        self.trigger_states: Set[str] = set()
        self.base_damages: Dict[Characteristics, int] = {characteristic: 0 for characteristic in Characteristics}
        self.stats: Dict[str, Stats] = {'__all__': Stats()}
        self.damage_parameters: Dict[str, DamageParameters] = {'__all__': DamageParameters()}
        self.new_output_states: Set[str] = set()
        self.removed_output_states: Set[str] = set() # Must be a subset of self.trigger_states
        self.has_stats = False
        self.has_parameters = False

    def add_trigger_state(self, state: str):
        self.trigger_states.add(state)

    def set_base_damages(self, characteristic: Characteristics, base_damages: int):
        self.base_damages[characteristic] = base_damages

    def add_stats(self, stats: Stats, spell: str = '__all__'):
        self.has_stats = True
        self.stats[spell] = self.stats.get(spell, Stats()) + stats

    def add_damage_parameters(self, damage_parameters: DamageParameters, spell: str = '__all__'):
        self.has_parameters = True
        self.damage_parameters[spell] = self.damage_parameters.get(spell, DamageParameters()) + damage_parameters

    def add_new_output_state(self, state: str):
        self.new_output_states.add(state)

    def add_removed_output_state(self, state: str):
        self.removed_output_states.add(state)

    def trigger(self, states: Set[str]) -> bool:
        return self.trigger_states == states


class Spell():
    def __init__(self, from_scratch=True) -> None:
        self.parameters = SpellParameters()
        self.buffs: List[SpellBuff] = list()
        self.name = ''
        self.short_name = ''

        if from_scratch:
            for characteristic in Characteristics:
                self.parameters.base_damages[characteristic] = {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0}


    def get_detailed_damages(self, stats: Stats, parameters: DamageParameters):
        average_damage = 0.0
        average_damage_crit = 0.0

        damages_by_characteristic: Dict[Characteristics, Dict[str, float]] = dict()

        for characteristic in Characteristics:
            min_damage = compute_damage(self.parameters.base_damages[characteristic]['min'], stats, characteristic, is_weapon=self.parameters.is_weapon, parameters=parameters)
            max_damage = compute_damage(self.parameters.base_damages[characteristic]['max'], stats, characteristic, is_weapon=self.parameters.is_weapon, parameters=parameters)
            average_damage += (min_damage + max_damage) / 2

            min_damage_crit = compute_damage(self.parameters.base_damages[characteristic]['crit_min'], stats, characteristic, is_weapon=self.parameters.is_weapon, is_crit=True, parameters=parameters)
            max_damage_crit = compute_damage(self.parameters.base_damages[characteristic]['crit_max'], stats, characteristic, is_weapon=self.parameters.is_weapon, is_crit=True, parameters=parameters)
            average_damage_crit += (min_damage_crit + max_damage_crit) / 2

            damages_by_characteristic[characteristic] = {
                'min': min_damage,
                'max': max_damage,
                'crit_min': min_damage_crit,
                'crit_max': max_damage_crit
            }

        damages_total: Dict[str, float] = dict()
        for field in ('min', 'max', 'crit_min', 'crit_max'):
            damages_total[field] = sum(damages_by_characteristic[characteristic][field] for characteristic in damages_by_characteristic)

        return (damages_by_characteristic, damages_total, (average_damage, average_damage_crit))


    def get_average_damages(self, stats: Stats, parameters: DamageParameters):
        _, _, (average_damage, average_damage_crit) = self.get_detailed_damages(stats, parameters)

        final_crit_chance = self.parameters.crit_chance + stats.bonus_crit_chance
        if final_crit_chance > 1.0:
            final_crit_chance = 1.0

        return (1 - final_crit_chance) * average_damage + final_crit_chance * average_damage_crit


    def get_damages_and_buffs_with_states(self, stats: Stats, damage_parameters: DamageParameters, states: Set[str]) -> SpellOutput:
        # Générer les buffs de ce sort liés aux états ok
        # Retirer les états utilisés et ajoutés les nouveaux ok
        # Générer les buffs pour les sorts suivants

        output = SpellOutput()

        computation_parameters = DamageParameters.from_existing(damage_parameters)
        computation_stats = Stats.from_existing(stats)
        output.states.update(states)

        for buff in self.buffs:
            if buff.trigger(states):
                computation_parameters.add_base_damages(buff.base_damages)

                if buff.has_stats:
                    output.update_stats(buff.stats)

                if buff.has_parameters:
                    output.update_parameters(buff.damage_parameters)

                output.states -= buff.removed_output_states
                output.states.update(buff.new_output_states)

        _, damages, _ = self.get_detailed_damages(computation_stats, computation_parameters)
        output.damages = damages

        return None


    def get_max_uses_single_target(self, max_used_pa):
        if not isinstance(max_used_pa, int):
            raise TypeError(f"Max used pa is not an int ('{max_used_pa}' of type '{type(max_used_pa)}' given instead).")

        if max_used_pa < 0:
            raise ValueError(f"Max used pa should be non negative ('{max_used_pa}' given instead).")

        return self.parameters.get_max_uses_single_target(max_used_pa)

    def get_max_uses_multiple_targets(self, max_used_pa):
        if not isinstance(max_used_pa, int):
            raise TypeError(f"Max used pa is not an int ('{max_used_pa}' of type '{type(max_used_pa)}' given instead).")

        if max_used_pa < 0:
            raise ValueError(f"Max used pa should be non negative ('{max_used_pa}' given instead).")

        return self.parameters.get_max_uses_multiple_targets(max_used_pa)


    def can_reach_po(self, min_po, max_po):
        return not (self.get_min_po() > max_po or self.get_max_po() < min_po)

    def save_to_file(self, filepath):
        json_valid_data = {
            'base_damages': self.parameters.base_damages,
            'pa': self.parameters.pa,
            'crit_chance': self.parameters.crit_chance,
            'uses_per_target': self.parameters.uses_per_target,
            'uses_per_turn': self.parameters.uses_per_turn,
            'is_weapon': self.parameters.is_weapon,
            'name': self.name,
            'short_name': self.short_name,
            'po': list(self.parameters.po)
        }

        with open(filepath, 'w', encoding='utf-8') as fo:
            json.dump(json_valid_data, fo)


    def get_pa(self):
        return self.parameters.pa

    def set_pa(self, pa):
        if not isinstance(pa, int):
            raise TypeError(f"PA count is not an int ('{pa}' of type '{type(pa)}' given instead).")
        if pa <= 0:
            raise ValueError(f"PA count should be a positive int ('{pa}' given instead).")

        self.parameters.pa = pa


    def get_base_damages(self, characteristic):
        if not isinstance(characteristic, Characteristics):
            raise TypeError(f"'{characteristic} is not a valid characteristic.")

        return self.parameters.base_damages[characteristic]

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

        self.parameters.base_damages[characteristic] = base_damages


    def get_crit_chance(self):
        return self.parameters.crit_chance

    def set_crit_chance(self, crit_chance):
        if not (isinstance(crit_chance, float) or isinstance(crit_chance, int)):
            raise TypeError(f"Crit chance is not a float ('{crit_chance}' of type '{type(crit_chance)}' given instead).")

        if not (0.0 <= crit_chance <= 1.0):
            raise ValueError(f"Crit chance should be between 0 and 1 inclusive ('{crit_chance}' given instead).")

        self.parameters.crit_chance = float(crit_chance)


    def get_uses_per_target(self):
        return self.parameters.uses_per_target

    def set_uses_per_target(self, uses_per_target):
        if not isinstance(uses_per_target, int):
            raise TypeError(f"Uses per target is not a int ('{uses_per_target}' of type '{type(uses_per_target)}' given instead).")
        if uses_per_target == 0 or uses_per_target < -1:
            raise ValueError(f"Uses per target should be -1 or a positive int ('{uses_per_target}' given instead).")

        self.parameters.uses_per_target = uses_per_target


    def get_uses_per_turn(self):
        return self.parameters.uses_per_turn

    def set_uses_per_turn(self, uses_per_turn):
        if not isinstance(uses_per_turn, int):
            raise TypeError(f"Uses per turn is not a int ('{uses_per_turn}' of type '{type(uses_per_turn)}' given instead).")
        if uses_per_turn == 0 or uses_per_turn < -1:
            raise ValueError(f"Uses per turn should be -1 or a positive int ('{uses_per_turn}' given instead).")

        self.parameters.uses_per_turn = uses_per_turn


    def set_weapon(self, is_weapon):
        if not (isinstance(is_weapon, bool) or (isinstance(is_weapon, int) and is_weapon in (0, 1))):
            raise TypeError(f"is_weapon is not a bool ('{is_weapon}' of type '{type(is_weapon)}' given instead).")

        self.parameters.is_weapon = bool(is_weapon)


    def get_min_po(self):
        return self.parameters.po[0]

    def get_max_po(self):
        return self.parameters.po[1]

    def set_po(self, min_po=None, max_po=None):
        if min_po is None:
            min_po = self.get_min_po()

        if max_po is None:
            max_po = self.get_max_po()

        if not (isinstance(min_po, int) and isinstance(max_po, int)):
            raise TypeError(f"Minimum PO or maximum PO is not an int or None ('{min_po}' and '{max_po}' of types '{type(min_po)}' and '{type(max_po)}' given instead).")

        if min_po < 0 or max_po < 0 or max_po < min_po:
            raise ValueError(f"Minimum PO and maximum PO should be non negative and minimum should be <= than maximum ('{min_po}' and '{max_po}' given instead).")

        self.parameters.po = (min_po, max_po)


    def get_name(self):
        return self.name

    def set_name(self, name):
        if len(str(name)) == 0:
            raise ValueError('Name cannot be an empty string.')

        self.name = str(name)


    def get_short_name(self):
        return self.short_name

    def get_safe_name(self):
        return re.sub(r'\W', '_', self.short_name)

    def set_short_name(self, short_name):
        if len(str(short_name)) == 0:
            raise ValueError('Short name cannot be an empty string.')

        self.short_name = str(short_name)



    @classmethod
    def check_json_validity(cls, json_data):
        for key in ('base_damages', 'pa', 'crit_chance', 'uses_per_target', 'uses_per_turn', 'is_weapon', 'name', 'short_name', 'po'):
            if not key in json_data:
                raise KeyError(f"JSON string does not contain a '{key}' key.")

        for characteristic in Characteristics:
            if not characteristic in json_data['base_damages']:
                raise KeyError(f"JSON string 'base_damages' array does not contains '{characteristic}'.")

    @classmethod
    def from_json_string(cls, json_string):
        json_data = json.loads(json_string)
        Spell.check_json_validity(json_data)

        spell = Spell(from_scratch=False)
        for characteristic in Characteristics:
            spell.set_base_damages(characteristic, json_data['base_damages'][characteristic])
        spell.set_pa(json_data['pa'])
        spell.set_crit_chance(json_data['crit_chance'])
        spell.set_uses_per_target(json_data['uses_per_target'])
        spell.set_uses_per_turn(json_data['uses_per_turn'])
        spell.set_weapon(json_data['is_weapon'])
        spell.set_name(json_data['name'])
        spell.set_short_name(json_data['short_name'])
        spell.set_po(min_po=json_data['po'][0], max_po=json_data['po'][1])

        return spell

    @classmethod
    def from_file(cls, filepath):
        if not (os.path.isfile(filepath) and os.access(filepath, os.R_OK)):
            raise FileNotFoundError(f"Cannot create spell from file {filepath}: file not found or innaccessible.")

        with open(filepath, 'r', encoding='utf-8') as fi:
            json_string = fi.read()

        return Spell.from_json_string(json_string)
