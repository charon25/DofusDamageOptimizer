from hashlib import sha1
from typing import Dict, List, Set, Tuple

try:
    from tqdm import tqdm as progress_bar
except ImportError:  # If the 'tqdm' module is not installed, define the progress bar as the identity function
    def progress_bar(iterator, *args, **kwargs): return iterator

from damage_parameters import DamageParameters
from spell import Spell
from spell_set import SpellSet
from stats import Stats


class ComputationData:

    def __init__(self) -> None:
        self.permutation: Tuple[str] = ()
        self.already_computed_count: int = 0
        self.damages: Dict[str, int] = {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0}
        self.average_damages: float = 0.0
        self.stats: Dict[str, Stats] = {'__all__': Stats()}
        self.parameters: Dict[str, DamageParameters] = {'__all__': DamageParameters()}
        self.states: Set[str] = set()


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


    def _get_computation_hash(self, parameters: DamageParameters) -> str:
        return sha1(str(sorted(spell.short_name for spell in self.spells) + [parameters.pa]).encode('ascii')).hexdigest()


    def _is_combination_possible(self, spells: List[Spell]) -> bool:
        # First member is the minimum of the maximum range of the spells, and inversely for the second member
        return min(spell.parameters.po[1] for spell in spells) >= max(spell.parameters.po[0] for spell in spells)


    def _get_detailed_damages_of_permutation(self, permutation: List[int], stats: Stats, parameters: DamageParameters, previous_data: ComputationData = None) -> ComputationData: #Tuple[Dict[str, int], float]:
        spells = [self.spells[index] for index in permutation] # Convert the list of indices into a list of spells

        if not self._is_combination_possible(spells):
            return None

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


    def get_detailed_damages(self, stats: Stats, parameters: DamageParameters, cache: Dict[int, List[Tuple[int, ...]]] = None) -> Dict[Tuple[str], Tuple[float, Dict[str, int]]]:
        if cache is None:
            cache = {}

        computation_hash = self._get_computation_hash(parameters)

        if not computation_hash in cache:
            permutations = self._get_permutations(parameters)
            
            # If the same spell can be used multiple times, there may be multiple "identical" permutations as they do not have the same index
            # Example, if self.spells = ["s1", "s2", "s2"] (and there are enough AP), the permutations will have both [0, 1, 2] and [0, 2, 1] which are really the same
            # So we remove them based on the spells short names
            unique_permutations = set()
            for permutation in permutations:
                unique_permutations.add(tuple(self.spells[index].short_name for index in permutation))

            # The permutations is then once again transformed into indices
            unique_permutations = [tuple(self.indexes[short_name] for short_name in permutation) for permutation in sorted(unique_permutations)]
            cache[computation_hash] = unique_permutations
        else:
            unique_permutations = cache[computation_hash]

        previous_computation_data: Dict[int, ComputationData] = {}
        permutations_iterator = progress_bar(enumerate(unique_permutations), total=len(unique_permutations), leave=False) if len(unique_permutations) > 20000 else enumerate(unique_permutations)

        damages = dict()
        for index, permutation in permutations_iterator:
            permutation_length = len(permutation)
            if permutation_length == 0:
                continue

            previous_data = previous_computation_data[permutation_length - 1] if permutation_length > 1 else None

            computation_data = self._get_detailed_damages_of_permutation(permutation, stats, parameters, previous_data=previous_data)
            if computation_data is None:
                continue

            damages[index] = (computation_data.average_damages, computation_data.damages.copy())
            previous_computation_data[len(permutation)] = computation_data

        # Sort first by damages decreasing, then by permutation length increase
        damages = {tuple(self.spells[index].short_name for index in unique_permutations[key]): value for key, value in sorted(damages.items(), key=lambda key_value: (key_value[1][0], -len(unique_permutations[key_value[0]])), reverse=True)}

        return damages
