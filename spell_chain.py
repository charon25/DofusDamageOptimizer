from typing import Dict, List, Set

from damage_parameters import DamageParameters
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


    def _get_detailed_damages_of_permutation(self, permutation: List[int], stats: Stats, parameters: DamageParameters, test=False) -> Dict[str, int]:
        spells = [self.spells[index] for index in permutation] # Convert the list of indices into a list of spells

        stats_buff: Dict[str, Stats] = {'__all__': Stats()}
        parameters_buff: Dict[str, DamageParameters] = {'__all__': DamageParameters()}
        current_states: Set[str] = set() # TODO : vérifier les 50 de puissance donnés par les états hupper
        damages = {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0}

        for k, spell in enumerate(spells):
            spell_stats = stats + stats_buff['__all__'] + stats_buff.get(spell.short_name, Stats())
            spell_parameters = parameters + parameters_buff['__all__'] + parameters_buff.get(spell.short_name, DamageParameters())

            spell_output = spell.get_damages_and_buffs_with_states(spell_stats, spell_parameters, current_states)

            current_states = spell_output.states

            for name in spell_output.stats:
                stats_buff[name] = stats_buff.get(name, Stats()) + spell_output.stats[name]

            for name in spell_output.parameters:
                parameters_buff[name] = parameters_buff.get(name, DamageParameters()) + spell_output.parameters[name]

            for field in damages:
                damages[field] += spell_output.damages[field]
        
        return damages


    # Résultats pour chaque permutation ou pour la meilleure ?? TODO
    def get_detailed_damages(self, stats: Stats, parameters: DamageParameters):
        permutations = self._get_permutations(parameters)

        for permutation in permutations:
            self._get_detailed_damages_of_permutation(permutation, stats, parameters)
