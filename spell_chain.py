from typing import Dict, List, Set

from damages_parameters import DamageParameters
from spell import Spell
from stats import Stats


class SpellChains:
    def __init__(self) -> None:
        self.spells: List[Spell] = list()


    def add_spell(self, spell: Spell):
        self.spells.append(spell)


    def _get_permutations(self, parameters: DamageParameters) -> List[int]:
        """Generate a list of list containing the indices of the spells."""
        max_used_pa = parameters.pa

        spells = [(i, spell.get_pa()) for i, spell in enumerate(self.spells)] # Assign a unique index for each spell (so the algorithm works on integers)

        all_permutations = {0: [[]]}
        for pa in range(1, max_used_pa + 1):
            pa_permutations = []
            for spell_index, spell_pa in spells:
                if pa >= spell_pa:
                    previous_permutations = all_permutations[pa - spell_pa]
                    pa_permutations.extend(permutation + [spell_index] for permutation in previous_permutations if spell_index not in permutation)

            all_permutations[pa] = pa_permutations

        all_permutations_list = list()
        for pa in all_permutations:
            all_permutations_list.extend(all_permutations[pa])

        return all_permutations_list


    def _get_detailed_damages_of_permutation(self, permutation: List[int], stats: Stats, parameters: DamageParameters) -> None:
        spells = [self.spells[index] for index in permutation] # Convert the list of indices into a list of spells

        current_stats = Stats.from_existing(stats)
        current_parameters = DamageParameters.from_existing(parameters)
        stats_buff: Dict[str, Stats] = {'__all__': []}
        parameters_buff: Dict[str, Stats] = {'__all__': []}
        current_states: Set[str] = {}

        for spell in spells:
            spell_stats = current_stats + sum(stats_buff['__all__']) + sum(stats_buff.get(spell.short_name, []))
            spell_parameters = current_parameters + sum(parameters_buff['all']) + sum(parameters_buff.get(spell.short_name, []))

            _, damages, _ = spell.get_damages_and_buffs_with_states(spell_stats, spell_parameters, current_states)


    # Résultats pour chaque permutation ou pour la meilleure ?? TODO
    def get_detailed_damages(self, stats: Stats, parameters: DamageParameters):
        permutations = self._get_permutations(parameters)

        for permutation in permutations:
            self._get_detailed_damages_of_permutation(permutation, stats, parameters)
