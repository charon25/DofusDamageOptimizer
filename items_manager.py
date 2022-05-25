from ctypes import Union
import json
from typing import Dict, List, Tuple
from unicodedata import normalize

from damage_parameters import DamageParameters
from item import Equipment, Item
from item_set import ItemSet
from spell_chain import ComputationData, SpellChains
from stats import Stats


class ItemsManager:

    def __init__(self, filepaths: Dict[str, str]) -> None:
        self.items: Dict[int, Item] = {}
        self.items_by_type: Dict[str, List[Item]] = {}
        self.item_sets: Dict[int, ItemSet] = {}
        self.item_sets_combinations: List[List[int]] = []

        self._load_items(filepaths)

    def _load_items(self, filepaths: Dict[str, str]):
        assert 'items' in filepaths
        assert 'item_sets' in filepaths
        assert 'item_sets_combinations' in filepaths

        with open(filepaths['item_sets'], 'r', encoding='utf-8') as fi:
            json_item_sets = json.load(fi)

        for json_item_set in json_item_sets:
            item_set: ItemSet = ItemSet.from_json_data(json_item_set)
            self.item_sets[item_set.id] = item_set


        with open(filepaths['items'], 'r', encoding='utf-8') as fi:
            json_items = json.load(fi)

        for json_item in json_items:
            item: Item = Item.from_json_data(json_item)
            self.items[item.id] = item

            if not item.type in self.items_by_type:
                self.items_by_type[item.type] = []
            self.items_by_type[item.type].append(item)

            if item.set is not None:
                self.item_sets[item.set].items[item.type] = self.item_sets[item.set].items.get(item.type, []) + [item]
                self.item_sets[item.set].level = max(self.item_sets[item.set].level, item.level)

        with open(filepaths['item_sets_combinations'], 'r', encoding='utf-8') as fi:
            self.item_sets_combinations = json.load(fi)


    def _get_normalised_string(self, string: str) -> str:
        return normalize('NFKD', string.lower()).encode('ASCII', 'ignore')


    def search(self, search_phrase: str) -> List[Item]:
        results = []
        search_phrase = self._get_normalised_string(search_phrase)
        for item in self.items.values():
            if search_phrase in self._get_normalised_string(item.name):
                results.append(item)
        
        return sorted(results, key=lambda item:item.name)


    def _get_total_stats_from_items(self, items: List[Item], parameters: DamageParameters) -> Stats:
        total_stats = sum(item.stats[parameters.stuff_stats_mode] for item in items)

        item_sets_counter = {}
        for item in items:
            if item.set is not None:
                if not item.set in item_sets_counter:
                    item_sets_counter[item.set] = 1
                else:
                    item_sets_counter[item.set] += 1

        return total_stats + sum(self.item_sets[item_set_id].get_stats(quantity) for item_set_id, quantity in item_sets_counter.items())


    def _is_item_set_combination_possible(self, item_set_ids: List[int], parameters: DamageParameters) -> Tuple[bool, Dict[str, int]]:
        count = {item_type: (0 if item_type in parameters.stuff else 1) for item_type in Item.TYPES}
        for item_set_id in item_set_ids:
            for item_type, items in self.item_sets[item_set_id].items.items():
                count[item_type] += len(items)
        
        return (all(count[item_type] <= Item.QUANTITY[item_type] for item_type in count), count)


    def _get_n_best_items_from_damages(self, damages: Dict[Tuple[str], Tuple[float, Dict[str, int]]], n: int = 1) -> List[Item]:
        return list(self.items[item_id] for item_id in list(damages.keys())[:n])


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


    def get_best_stuff_from_spells(self, spell_chain: SpellChains, base_stats: Stats, parameters: DamageParameters, equipments: Dict[str, Equipment]) -> Tuple[List[Item], Tuple[float, Dict[str, int]]]:
        # base_stats are the stats given by the parameters (from stats page)
        # initial_stats are the base stats plus the stats given by the initial equipment
        initial_stats = base_stats + parameters.get_equipment_stats(self.items, self.item_sets, equipments)

        permutation = list(range(len(spell_chain.spells)))  # Permutation of all specified spells in the specified order

        best_items_by_type: Dict[str, List[Item]] = {}
        for item_type in parameters.stuff:
            damages = self._get_best_stuff_part_from_spells(item_type, spell_chain, initial_stats, parameters)
            best_items_by_type[item_type] = self._get_n_best_items_from_damages(damages, n=10000)

        damages_by_items: Dict[Tuple[int], Tuple[float, Dict[str, int]]] = {}
        for item_set_ids in self.item_sets_combinations:
            is_item_set_possible, item_types_count = self._is_item_set_combination_possible(item_set_ids, parameters)

            if is_item_set_possible and all(parameters.level[0] <= self.item_sets[item_set_id].level <= parameters.level[1] for item_set_id in item_set_ids):
                items = [item for item_set_id in item_set_ids for items in self.item_sets[item_set_id].items.values() for item in items]

                for item_type in Item.TYPES:
                    count_left = Item.QUANTITY[item_type] - item_types_count[item_type]
                    current_index = 0
                    while count_left > 0:
                        current_item = best_items_by_type[item_type][current_index]
                        if not current_item in items:
                            items.append(current_item)
                            count_left -= 1
                        current_index += 1

                # print(items, item_types_count)
                total_stats = base_stats + self._get_total_stats_from_items(items, parameters)

                computation_data = spell_chain._get_detailed_damages_of_permutation(permutation, total_stats, parameters, previous_data=None)
                damages_by_items[tuple(item.id for item in items)] = (computation_data.average_damages, computation_data.damages)

        damages_by_items = {key: value for key, value in sorted(damages_by_items.items(), key=lambda key_value: key_value[1][0], reverse=True)}
        best_items = next(iter(damages_by_items))

        return ([self.items[item_id] for item_id in best_items], damages_by_items[best_items])
