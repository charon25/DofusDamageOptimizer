from ctypes import Union
import json
from typing import Dict, List, Tuple

from damage_parameters import DamageParameters
from item import Item
from spell_chain import ComputationData, SpellChains
from stats import Stats


class ItemsManager:

    def __init__(self, filepath: str) -> None:
        self.items: Dict[int, Item] = {}
        self.items_by_type: Dict[str, List[Item]] = {}

        self._load_items(filepath)

    def _load_items(self, filepath: str):
        with open(filepath, 'r', encoding='utf-8') as fi:
            json_items = json.load(fi)

        for json_item in json_items:
            item: Item = Item.from_json_data(json_item)
            self.items[item.id] = item

            if not item.type in self.items_by_type:
                self.items_by_type[item.type] = []
            self.items_by_type[item.type].append(item)


    def _get_n_best_items_from_damages(self, damages: Dict[Tuple[str], Tuple[float, Dict[str, int]]], n: int = 1) -> List[Item]:
        return list(item_id for item_id in list(damages.keys())[:n])


    def _get_best_stuff_part_from_spells(self, stuff_part: str, spell_chain: SpellChains, stats: Stats, parameters: DamageParameters) -> Dict[Tuple[str], Tuple[float, Dict[str, int]]]:
        if not stuff_part in self.items_by_type:
            raise KeyError(f"Stuff part '{stuff_part}' is not valid.")

        permutation = list(range(len(spell_chain.spells)))  # Permutation of all specified spells in the specified order
        stuff_stats_mode = parameters.stuff_stats_mode
        min_level, max_level = parameters.level

        damages = dict()
        for item in self.items_by_type[stuff_part]:
            if not (min_level <= item.level <= max_level):
                continue

            permutation_stats = stats + item.stats[stuff_stats_mode]

            computation_data = spell_chain._get_detailed_damages_of_permutation(permutation, permutation_stats, parameters, previous_data=None)
            damages[item.id] = (computation_data.average_damages, computation_data.damages.copy())

        damages = {key: value for key, value in sorted(damages.items(), key=lambda key_value: (key_value[1][0], -self.items[key_value[0]].level), reverse=True)}

        return damages


    def get_best_stuff_from_spells(self, spell_chain: SpellChains, stats: Stats, parameters: DamageParameters) -> Tuple[List[Item], Tuple[float, Dict[str, int]]]:
        if parameters.stuff == 'all':
            damages = {}
            for stuff_type in Item.TYPES:
                damages[stuff_type] = self._get_best_stuff_part_from_spells(stuff_type, spell_chain, stats, parameters)

            complete_stuff: List[Item] = [
                *self._get_n_best_items_from_damages(damages['hat'], n=1),
                *self._get_n_best_items_from_damages(damages['amulet'], n=1),
                *self._get_n_best_items_from_damages(damages['cloak'], n=1),
                *self._get_n_best_items_from_damages(damages['ring'], n=2),
                *self._get_n_best_items_from_damages(damages['weapon'], n=1),
                *self._get_n_best_items_from_damages(damages['shield'], n=1),
                *self._get_n_best_items_from_damages(damages['belt'], n=1),
                *self._get_n_best_items_from_damages(damages['boots'], n=1),
                *self._get_n_best_items_from_damages(damages['pet'], n=1),
                *self._get_n_best_items_from_damages(damages['dofus'], n=6),
            ]

            total_stats = stats + sum(self.items[item_id].stats[parameters.stuff_stats_mode] for item_id in complete_stuff)
            computation_data = spell_chain._get_detailed_damages_of_permutation(list(range(len(spell_chain.spells))), total_stats, parameters, previous_data=None)

            return ([self.items[item_id] for item_id in complete_stuff], (computation_data.average_damages, computation_data.damages))

        else:
            damages = self._get_best_stuff_part_from_spells(parameters.stuff, spell_chain, stats, parameters)
            best_item_ids = self._get_n_best_items_from_damages(damages, n=6)
            return ((self.items[item_id], damages[item_id]) for item_id in best_item_ids)