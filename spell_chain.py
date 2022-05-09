from dataclasses import dataclass, field
from math import perm
from typing import Dict, List, Set, Tuple

from damage_parameters import DamageParameters
from spell import Spell
from spell_set import SpellSet
from stats import Stats


@dataclass
class ComputationData:
    permutation: Tuple[str] = field(default_factory=lambda: tuple())
    already_computed_count: int = 0
    damages: Dict[str, int] = field(default_factory=lambda: {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0})
    average_damages: float = 0.0
    stats: Dict[str, Stats] = field(default_factory=lambda: {'__all__': Stats()})
    parameters: Dict[str, DamageParameters] = field(default_factory=lambda: {'__all__': DamageParameters()})
    states: Set[str] = field(default_factory=lambda: set())


class SpellChains:
    def __init__(self) -> None:
        self.spells: List[Spell] = list()
        self.indexes: Dict[str, int] = dict()


    def add_spell(self, spell: Spell):
        self.indexes[spell.get_short_name()] = len(self.spells)
        self.spells.append(spell)


    def _get_permutations(self, parameters: DamageParameters) -> List[int]:
        """Generate a list of list containing the indices of the spells."""
        max_used_pa = parameters.pa

        # Associate a unique integer by "spell family" (indentical spell present multiple times)
        spells_short_names_unique_id = {short_name: k for k, short_name in enumerate(set([spell.get_short_name() for spell in self.spells]))}

        spells = [(i, spell.get_pa(), spells_short_names_unique_id[spell.get_short_name()]) for i, spell in enumerate(self.spells)] # Assign a unique index for each spell (so the algorithm works on integers)

        all_permutations = {0: [[]]}
        for pa in range(1, max_used_pa + 1):
            pa_permutations = []
            for spell_index, spell_pa, _ in spells:
                if pa >= spell_pa:
                    previous_permutations = all_permutations[pa - spell_pa]
                    pa_permutations.extend(permutation + [spell_index] for permutation in previous_permutations if spell_index not in permutation)

            all_permutations[pa] = []
            permutations_already_seen = set()
            # Remove "identical" permutation : permutation where the same spell is present at the same index but it is not the same instance
            for permutation in pa_permutations:
                unique_permutation_tuple = tuple(spells[spell_index][2] for spell_index in permutation)
                if not unique_permutation_tuple in permutations_already_seen:
                    permutations_already_seen.add(unique_permutation_tuple)
                    all_permutations[pa].append(permutation)

            # all_permutations[pa] = pa_permutations

        all_permutations_list = list()
        for pa in all_permutations:
            all_permutations_list.extend(all_permutations[pa])

        return all_permutations_list


    def _get_detailed_damages_of_permutation(self, permutation: List[int], stats: Stats, parameters: DamageParameters, previous_data: ComputationData = None) -> ComputationData: #Tuple[Dict[str, int], float]:
        spells = [self.spells[index] for index in permutation] # Convert the list of indices into a list of spells

        if previous_data is None:
            previous_data = ComputationData()
            previous_data.states = set(parameters.starting_states)

        damages: Dict[str, int] = previous_data.damages.copy()
        average_damages = previous_data.average_damages
        stats_buff: Dict[str, Stats] = {name: stats for name, stats in previous_data.stats.items()}
        parameters_buff: Dict[str, DamageParameters] = {name: parameters for name, parameters in previous_data.parameters.items()}
        current_states: Set[str] = set(previous_data.states)

        for index, spell in enumerate(spells[previous_data.already_computed_count:], start=previous_data.already_computed_count):
            spell_stats = stats + stats_buff['__all__'] + stats_buff.get(spell.short_name, Stats())
            spell_parameters = parameters + parameters_buff['__all__'] + parameters_buff.get(spell.short_name, DamageParameters())
            spell_output = spell.get_damages_and_buffs_with_states(spell_stats, spell_parameters, current_states)

            final_crit_chance = spell.parameters.crit_chance + spell_stats.bonus_crit_chance
            if final_crit_chance > 1.0:
                final_crit_chance = 1.0

            current_states = spell_output.states

            for name in spell_output.stats:
                stats_buff[name] = stats_buff.get(name, Stats()) + spell_output.stats[name]

            for name in spell_output.parameters:
                parameters_buff[name] = parameters_buff.get(name, DamageParameters()) + spell_output.parameters[name]

            for field in damages:
                damages[field] += spell_output.damages[field]

            average_damages += (1 - final_crit_chance) * spell_output.average_damage + final_crit_chance * spell_output.average_damage_crit

        computation_data = ComputationData()
        computation_data.permutation = tuple(self.spells[index].short_name for index in permutation)
        computation_data.already_computed_count = len(permutation)
        computation_data.average_damages = average_damages
        computation_data.damages = damages
        computation_data.stats = stats_buff
        computation_data.parameters = parameters_buff
        computation_data.states = current_states

        return computation_data


    def get_detailed_damages(self, stats: Stats, parameters: DamageParameters) -> Dict[Tuple[str], Dict[str, int]]:
        permutations = self._get_permutations(parameters)
        previous_computation_data: Dict[int, ComputationData] = {}
        
        # If the same spell can be used multiple times, there may be multiple "identical" permutations as they do not have the same index
        # Example, if self.spells = ["s1", "s2", "s2"] (and there are enough AP), the permutations will have both [0, 1, 2] and [0, 2, 1] which are really the same
        # So we remove them based on the spells short names
        unique_permutations = set()
        for permutation in permutations:
            unique_permutations.add(tuple(self.spells[index].short_name for index in permutation))
            if not len(permutation) in previous_computation_data:
                previous_computation_data[len(permutation)] = None

        # The permutations is then once again transformed into indices
        unique_permutations = [tuple(self.indexes[short_name] for short_name in permutation) for permutation in sorted(unique_permutations)]

        damages = dict()
        for index, permutation in enumerate(unique_permutations):
            permutation_length = len(permutation)
            if permutation_length == 0:
                continue

            previous_data = previous_computation_data[permutation_length - 1] if permutation_length > 1 else None

            computation_data = self._get_detailed_damages_of_permutation(permutation, stats, parameters, previous_data=previous_data)
            damages[index] = (computation_data.average_damages, computation_data.damages.copy())
            previous_computation_data[len(permutation)] = computation_data

        damages = {tuple(self.spells[index].short_name for index in unique_permutations[key]): value for key, value in sorted(damages.items(), key=lambda key_value: key_value[1][0], reverse=True)}

        return damages


if __name__ == '__main__':
    filenames = ['profiling_spells\\1pa.json', 'profiling_spells\\1pa_.json', 'profiling_spells\\2pa.json', 'profiling_spells\\2pa__.json', 'profiling_spells\\2pa_.json', 'profiling_spells\\2pa___.json', 'profiling_spells\\3pa.json']
    spells = [Spell.from_file(filename) for filename in filenames]

    spell_set = SpellSet()
    for spell in spells:
        spell_set.add_spell(spell)
    
    stats = Stats()
    parameters = DamageParameters.from_string('-pa 9')
    spell_list = spell_set.get_spell_list_single_target(parameters)

    spell_chain = SpellChains()
    for spell in spell_list:
        spell_chain.add_spell(spell)

    dmg = spell_chain.get_detailed_damages(stats, parameters)

    # for k, c in enumerate(dmg):
    #     print(c, dmg[c])
    #     if k > 5:
    #         break