from dataclasses import dataclass, field, replace
import json
import os
import re
from typing import Dict, List, Literal, Set, Tuple
from uuid import uuid1

from characteristics_damages import *
# from damages import compute_damage
from damages import compute_damages
from damage_parameters import DamageParameters
from stats import Stats


@dataclass
class SpellOutput:
    damages_by_characteristic: List[Dict[str, int]] = field(default_factory=lambda: [{'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0} for _ in range(CHARACTERISTICS_COUNT)])
    damages: Dict[str, int] = field(default_factory=lambda: {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0})
    stats: Dict[str, Stats] = field(default_factory=lambda: {'__all__': Stats()})
    parameters: Dict[str, DamageParameters] = field(default_factory=lambda: {'__all__': DamageParameters()})
    states: Set[str] = field(default_factory=lambda: set())
    average_damage: float = 0.0
    average_damage_crit: float = 0.0

    def update_stats(self, new_stats: Dict[str, Stats]):
        for name in new_stats:
            self.stats[name] = self.stats.get(name, Stats()) + new_stats[name]

    def update_parameters(self, new_parameters: Dict[str, DamageParameters]):
        for name in new_parameters:
            self.parameters[name] = self.parameters.get(name, DamageParameters()) + new_parameters[name]

    def update_damages_from_existing(self, other: 'SpellOutput'):
        for field in ('min', 'max', 'crit_min', 'crit_max'):
            for characteristic in range(CHARACTERISTICS_COUNT):
                self.damages_by_characteristic[characteristic][field] = other.damages_by_characteristic[characteristic][field]
            self.damages[field] = other.damages[field]

        self.average_damage = other.average_damage
        self.average_damage_crit = other.average_damage_crit


@dataclass
class SpellParameters:
    base_damages: List[Dict[str, int]] = field(default_factory=lambda: [{} for _ in range(CHARACTERISTICS_COUNT)])
    damaging_characteristics: List[int] = field(default_factory=lambda: [])
    pa: int = 1
    crit_chance: float = 0.0
    uses_per_target: int = -1
    uses_per_turn: int = -1
    is_weapon: bool = False
    po: Tuple[int, int] = field(default_factory=lambda: (0, 1024))
    position: Literal['all', 'line', 'diag'] = 'all'


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

@dataclass
class SpellBuff:
    trigger_states: Set[str] = field(default_factory=lambda: set())
    forbidden_states: Set[str] = field(default_factory=lambda: set())
    base_damages: List[int] = field(default_factory=lambda: [0 for _ in range(CHARACTERISTICS_COUNT)])
    additional_damaging_characteristics: List[int] = field(default_factory=lambda: [])
    stats: Dict[str, Stats] = field(default_factory=lambda: {'__all__': Stats()})
    damage_parameters: Dict[str, DamageParameters] = field(default_factory=lambda: {'__all__': DamageParameters()})

    new_output_states: Set[str] = field(default_factory=lambda: set())
    removed_output_states: Set[str] = field(default_factory=lambda: set())

    has_stats: bool = False
    has_parameters: bool = False

    is_huppermage_states: bool = False


    def add_trigger_state(self, state: str):
        self.trigger_states.add(state)

    def add_trigger_states(self, states: Set[str]):
        self.trigger_states.update(states)

    def remove_trigger_state(self, state: str):
        self.trigger_states -= {state,}

    def add_forbidden_state(self, state: str):
        self.forbidden_states.add(state)

    def add_forbidden_states(self, states: Set[str]):
        self.forbidden_states.update(states)

    def remove_forbidden_state(self, state: str):
        self.forbidden_states -= {state,}

    def set_base_damages(self, characteristic: int, base_damages: int):
        self.base_damages[characteristic] = base_damages

    def add_additional_damaging_characteristic(self, characteristic: int):
        if not characteristic in self.additional_damaging_characteristics:
            self.additional_damaging_characteristics.append(characteristic)

    def remove_additional_damaging_characteristic(self, characteristic: int):
        if characteristic in self.additional_damaging_characteristics:
            self.additional_damaging_characteristics.remove(characteristic)

    def has_additional_damaging_characteristic(self, characteristic: int):
        return characteristic in self.additional_damaging_characteristics

    def add_stats(self, stats: Stats, spell: str = '__all__'):
        self.has_stats = True
        self.stats[spell] = self.stats.get(spell, Stats()) + stats

    def add_damage_parameters(self, damage_parameters: DamageParameters, spell: str = '__all__'):
        self.has_parameters = True
        self.damage_parameters[spell] = self.damage_parameters.get(spell, DamageParameters()) + damage_parameters

    def add_new_output_state(self, state: str):
        self.new_output_states.add(state)

    def add_new_output_states(self, states: Set[str]):
        self.new_output_states.update(states)

    def remove_new_output_state(self, state: str):
        self.new_output_states -= {state,}

    def add_removed_output_state(self, state: str):
        self.removed_output_states.add(state)

    def add_removed_output_states(self, states: Set[str]):
        self.removed_output_states.update(states)

    def remove_removed_output_state(self, state: str):
        self.removed_output_states -= {state,}

    def trigger(self, states: Set[str]) -> bool:
        # Operator '&' is set intersection, so the test returns true if there is no intersection between the sets
        # It is slightly faster than .intersection
        return states.issuperset(self.trigger_states) and not (states & self.forbidden_states)


    def to_compact_string(self, only_states=False):
        if self.is_huppermage_states:
            return f'Huppermage states : ({", ".join(sorted(self.new_output_states))})'
        else:
            return f'({", ".join(sorted(self.trigger_states))},{" " if self.forbidden_states else ""}{", ".join(f"!{state}" for state in sorted(self.forbidden_states))}) -> ({", ".join(sorted((self.trigger_states - self.removed_output_states) | self.new_output_states))}){"(Stats buff)" if self.has_stats and not only_states else ""}{"(Parameters buff)" if self.has_parameters and not only_states else ""}'


    def to_dict(self) -> Dict:
        return {
            'trigger_states': list(self.trigger_states),
            'forbidden_states': list(self.forbidden_states),
            'base_damages': self.base_damages,
            'additional_damaging_characteristics': self.additional_damaging_characteristics,
            'stats': {spell: stats.to_dict() for spell, stats in self.stats.items()},
            'damage_parameters': {spell: damage_parameters.to_string() for spell, damage_parameters in self.damage_parameters.items()},
            'new_output_states': list(self.new_output_states),
            'removed_output_states': list(self.removed_output_states),
            'is_huppermage_states': self.is_huppermage_states,
            'has_stats': self.has_stats,
            'has_parameters': self.has_parameters
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'SpellBuff':
        spell_buff = SpellBuff()

        for state in data.get('trigger_states', []):
            spell_buff.add_trigger_state(state)

        for state in data.get('forbidden_states', []):
            spell_buff.add_forbidden_state(state)

        for characteristic in range(CHARACTERISTICS_COUNT):
            spell_buff.set_base_damages(characteristic, data.get('base_damages', [0] * CHARACTERISTICS_COUNT)[characteristic])

        for characteristic in data.get('additional_damaging_characteristics', []):
            spell_buff.add_additional_damaging_characteristic(characteristic)

        for spell in data.get('stats', []):
            spell_buff.add_stats(Stats.from_dict(data['stats'][spell]), spell=spell)

        for spell in data.get('damage_parameters', []):
            spell_buff.add_damage_parameters(DamageParameters.from_string(data['damage_parameters'][spell]), spell=spell)

        for state in data.get('new_output_states', []):
            spell_buff.add_new_output_state(state)

        for state in data.get('removed_output_states', []):
            spell_buff.add_removed_output_state(state)

        spell_buff.is_huppermage_states = data.get('is_huppermage_states', False)
        spell_buff.has_stats = data.get('has_stats', False)
        spell_buff.has_parameters = data.get('has_parameters', False)

        return spell_buff


class Spell():
    def __init__(self, from_scratch=True) -> None:
        self.parameters = SpellParameters()
        self.buffs: List[SpellBuff] = list()
        self.name = ''
        self.short_name = ''

        if from_scratch:
            for characteristic in range(CHARACTERISTICS_COUNT):
                self.parameters.base_damages[characteristic] = {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0}
            self.set_short_name('')


    def get_detailed_damages(self, stats: Stats, parameters: DamageParameters, additional_damaging_characteristics: List[int] = None):
        spell_output = SpellOutput()

        if not additional_damaging_characteristics:
            additional_damaging_characteristics = []

        for characteristic in set(self.parameters.damaging_characteristics + additional_damaging_characteristics):
            min_damage, max_damage, min_damage_crit, max_damage_crit = compute_damages(self.parameters.base_damages[characteristic], stats, characteristic, parameters, self.parameters.is_weapon)
            spell_output.average_damage += (min_damage + max_damage) / 2
            spell_output.average_damage_crit += (min_damage_crit + max_damage_crit) / 2

            spell_output.damages_by_characteristic[characteristic] = {
                'min': min_damage,
                'max': max_damage,
                'crit_min': min_damage_crit,
                'crit_max': max_damage_crit
            }

        for field in ('min', 'max', 'crit_min', 'crit_max'):
            spell_output.damages[field] = sum(spell_output.damages_by_characteristic[characteristic][field] for characteristic in range(CHARACTERISTICS_COUNT))

        return spell_output


    def get_average_damages(self, stats: Stats, parameters: DamageParameters):
        spell_output = self.get_detailed_damages(stats, parameters)

        final_crit_chance = self.parameters.crit_chance + stats.bonus_crit_chance
        if final_crit_chance > 1.0:
            final_crit_chance = 1.0

        return (1 - final_crit_chance) * spell_output.average_damage + final_crit_chance * spell_output.average_damage_crit


    def get_damages_and_buffs_with_states_single(self, stats: Stats, damage_parameters: DamageParameters) -> SpellOutput:
        return self.get_damages_and_buffs_with_states(stats, damage_parameters, damage_parameters.starting_states)


    def get_damages_and_buffs_with_states(self, stats: Stats, damage_parameters: DamageParameters, states: Set[str]) -> SpellOutput:
        output = SpellOutput()

        computation_parameters = DamageParameters.from_existing(damage_parameters)
        computation_stats = Stats.from_existing(stats)
        output.states.update(states)
        additional_damaging_characteristics = []

        for buff in self.buffs:
            if buff.trigger(states):
                if buff.is_huppermage_states:
                    # Huppermage state is one of 'h:a', 'h:e', 'h:f', 'h:w' (respectively air, earth, fire and water)
                    for huppermage_state in sorted(buff.new_output_states):  # sorted() returns a list
                        huppermage_state = f'h:{huppermage_state[-1]}'  # State is of the form r"h:\w" or r"h:\d\w" but the eventual digit is not kept
                        current_huppermage_state = next((state for state in output.states if state.startswith('h:')), None)
                        if current_huppermage_state is None:
                            output.states.add(huppermage_state)
                        elif current_huppermage_state != huppermage_state: # If element has already been applied, do nothing
                            output.states -= {current_huppermage_state,}
                            # Concatenate the letter after the 'h:' in alphabetical order
                            if current_huppermage_state < huppermage_state:
                                combined = f'H:{current_huppermage_state[-1]}{huppermage_state[-1]}'
                            else:
                                combined = f'H:{huppermage_state[-1]}{current_huppermage_state[-1]}'
                            # If the combination has not been seen yet, add 50 power.
                            # If it is a fire/earth combination, also add 15% vulnerability
                            if not combined in output.states:
                                output.states.add(combined)
                                output.stats['__all__'].damages[POWER] += 50
                                if combined == 'H:ef':
                                    output.parameters['__all__'].vulnerability += 15
                else:
                    computation_parameters.add_base_damages(buff.base_damages)
                    additional_damaging_characteristics.extend(buff.additional_damaging_characteristics)

                    if buff.has_stats:
                        output.update_stats(buff.stats)

                    if buff.has_parameters:
                        output.update_parameters(buff.damage_parameters)

                    output.states -= buff.removed_output_states
                    output.states.update(buff.new_output_states)

        simple_output = self.get_detailed_damages(computation_stats, computation_parameters, additional_damaging_characteristics)
        output.update_damages_from_existing(simple_output)

        return output


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


    def can_reach(self, min_po: int, max_po: int, position: str):
        can_reach_po = not (self.get_min_po() > max_po or self.get_max_po() < min_po)
        can_reach_position = (self.parameters.position == 'all') or (position == 'unspecified') or (self.parameters.position == position)
        return can_reach_po and can_reach_position


    def to_dict(self):
        return {
            'base_damages': self.parameters.base_damages,
            'damaging_characteristics': self.parameters.damaging_characteristics,
            'pa': self.parameters.pa,
            'crit_chance': self.parameters.crit_chance,
            'uses_per_target': self.parameters.uses_per_target,
            'uses_per_turn': self.parameters.uses_per_turn,
            'is_weapon': self.parameters.is_weapon,
            'name': self.name,
            'short_name': self.short_name,
            'po': list(self.parameters.po),
            'position': self.parameters.position,
            'buffs': [buff.to_dict() for buff in self.buffs]
        }

    def save_to_file(self, filepath):
        json_valid_data = self.to_dict()

        with open(filepath, 'w', encoding='utf-8') as fo:
            json.dump(json_valid_data, fo)


    def add_buff(self, buff: SpellBuff):
        self.buffs.append(buff)


    def get_pa(self):
        return self.parameters.pa

    def set_pa(self, pa):
        if not isinstance(pa, int):
            raise TypeError(f"PA count is not an int ('{pa}' of type '{type(pa)}' given instead).")
        if pa <= 0:
            raise ValueError(f"PA count should be a positive int ('{pa}' given instead).")

        self.parameters.pa = pa


    def get_base_damages(self, characteristic: int):
        if not isinstance(characteristic, int) or characteristic >= CHARACTERISTICS_COUNT:
            raise TypeError(f"'{characteristic} is not a valid characteristic.")

        return self.parameters.base_damages[characteristic]

    def set_base_damages(self, characteristic: int, base_damages: Dict[str, int]):
        if not isinstance(characteristic, int) or characteristic >= CHARACTERISTICS_COUNT:
            raise TypeError(f"'{characteristic} is not a valid characteristic.")

        if not isinstance(base_damages, dict):
            raise TypeError(f"base_damages is not a dict ('{base_damages}' of type '{type(base_damages)}' given instead).")

        for field in ('min', 'max', 'crit_min', 'crit_max'):
            if not field in base_damages:
                raise KeyError(f"Field '{field}' missing in base_damages.")
            if not isinstance(base_damages[field], int):
                raise TypeError(f"Field '{field}' is not an int ('{base_damages[field]}' of type '{type(base_damages[field])}' given instead).")

        self.parameters.base_damages[characteristic] = base_damages


    def add_damaging_characteristic(self, characteristic: int):
        if not isinstance(characteristic, int) or characteristic >= CHARACTERISTICS_COUNT:
            raise TypeError(f"'{characteristic} is not a valid characteristic.")

        if not characteristic in self.parameters.damaging_characteristics:
            self.parameters.damaging_characteristics.append(characteristic)

    def remove_damaging_characteristic(self, characteristic: int):
        if not isinstance(characteristic, int) or characteristic >= CHARACTERISTICS_COUNT:
            raise TypeError(f"'{characteristic} is not a valid characteristic.")

        if characteristic in self.parameters.damaging_characteristics:
            self.parameters.damaging_characteristics.remove(characteristic)

    def does_damage_in_characteristic(self, characteristic: int):
        if not isinstance(characteristic, int) or characteristic >= CHARACTERISTICS_COUNT:
            raise TypeError(f"'{characteristic} is not a valid characteristic.")

        return characteristic in self.parameters.damaging_characteristics


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


    def set_position(self, position: str):
        if not position in ('all', 'line', 'diag'):
            raise ValueError(f"position is not one of 'all', 'line' or 'diag' ('{position}' given instead).")

        self.parameters.position = position


    def get_name(self):
        return self.name

    def set_name(self, name):
        if name == '':
            name = 'Unnamed spell'

        self.name = str(name)


    def get_short_name(self):
        return self.short_name

    def get_safe_name(self):
        return re.sub(r'\W', '_', self.short_name)

    def set_short_name(self, short_name):
        if short_name == '':
            short_name = str(uuid1())

        self.short_name = str(short_name)


    def __repr__(self) -> str:
        return f"Spell '{self.short_name}'"


    @classmethod
    def check_json_validity(cls, json_data):
        for field in ('base_damages', 'damaging_characteristics', 'pa', 'crit_chance', 'uses_per_target', 'uses_per_turn', 'is_weapon', 'name', 'short_name', 'po', 'position', 'buffs'):
            if not field in json_data:
                raise KeyError(f"JSON string does not contain a '{field}' field (Spell.check_json_validity).")

        if len(json_data['base_damages']) < CHARACTERISTICS_COUNT:
            raise KeyError(f"JSON string 'base_damages' array does not contains every characteristics ({len(json_data['base_damages'])} instead of {CHARACTERISTICS_COUNT}).")

    @classmethod
    def from_json_string(cls, json_string):
        json_data = json.loads(json_string)
        Spell.check_json_validity(json_data)

        spell = Spell(from_scratch=False)
        for characteristic in range(CHARACTERISTICS_COUNT):
            spell.set_base_damages(characteristic, json_data['base_damages'][characteristic])
        for characteristic in json_data['damaging_characteristics']:
            spell.add_damaging_characteristic(characteristic)
        spell.set_pa(json_data['pa'])
        spell.set_crit_chance(json_data['crit_chance'])
        spell.set_uses_per_target(json_data['uses_per_target'])
        spell.set_uses_per_turn(json_data['uses_per_turn'])
        spell.set_weapon(json_data['is_weapon'])
        spell.set_name(json_data['name'])
        spell.set_short_name(json_data['short_name'])
        spell.set_po(min_po=json_data['po'][0], max_po=json_data['po'][1])
        spell.set_position(json_data['position'])
        for buff in json_data['buffs']:
            spell.add_buff(SpellBuff.from_dict(buff))

        return spell

    @classmethod
    def from_file(cls, filepath):
        if not (os.path.isfile(filepath) and os.access(filepath, os.R_OK)):
            raise FileNotFoundError(f"Cannot create spell from file {filepath}: file not found or innaccessible.")

        with open(filepath, 'r', encoding='utf-8') as fi:
            json_string = fi.read()

        return Spell.from_json_string(json_string)
