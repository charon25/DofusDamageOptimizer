from ctypes import Union
import json
from typing import Dict, List, Tuple
from unicodedata import normalize

from damage_parameters import DamageParameters
from item import Item
from item_set import ItemSet
from spell_chain import ComputationData, SpellChains
from stats import Stats


class ItemsManager:

    def __init__(self, items_filepath: str, item_sets_filepath: str) -> None:
        self.items: Dict[int, Item] = {}
        self.items_by_type: Dict[str, List[Item]] = {}
        self.item_sets: Dict[int, ItemSet] = {}

        self._load_items(items_filepath, item_sets_filepath)

    def _load_items(self, items_filepath: str, item_sets_filepath: str):
        with open(item_sets_filepath, 'r', encoding='utf-8') as fi:
            json_item_sets = json.load(fi)

        for json_item_set in json_item_sets:
            item_set: ItemSet = ItemSet.from_json_data(json_item_set)
            self.item_sets[item_set.id] = item_set


        with open(items_filepath, 'r', encoding='utf-8') as fi:
            json_items = json.load(fi)

        for json_item in json_items:
            item: Item = Item.from_json_data(json_item)
            self.items[item.id] = item

            if not item.type in self.items_by_type:
                self.items_by_type[item.type] = []
            self.items_by_type[item.type].append(item)

            if item.set is not None:
                try:
                    self.item_sets[item.set].items[item.type] = self.item_sets[item.set].items.get(item.type, []) + [item]
                except:pass


    def _get_normalised_string(self, string: str) -> str:
        return normalize('NFKD', string.lower()).encode('ASCII', 'ignore')


    def search(self, search_phrase: str) -> List[Item]:
        results = []
        search_phrase = self._get_normalised_string(search_phrase)
        for item in self.items.values():
            if search_phrase in self._get_normalised_string(item.name):
                results.append(item)
        
        return sorted(results, key=lambda item:item.name)


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
        complete_stuff: List[Item] = []
        for stuff_type in parameters.stuff:
            damages = self._get_best_stuff_part_from_spells(stuff_type, spell_chain, stats, parameters)
            complete_stuff.extend(self._get_n_best_items_from_damages(damages, n=Item.QUANTITY[stuff_type]))

        total_stats = stats + sum(self.items[item_id].stats[parameters.stuff_stats_mode] for item_id in complete_stuff)
        computation_data = spell_chain._get_detailed_damages_of_permutation(list(range(len(spell_chain.spells))), total_stats, parameters, previous_data=None)

        return ([self.items[item_id] for item_id in complete_stuff], (computation_data.average_damages, computation_data.damages))


class Code:
    TYPES = Item.TYPES[:-1]
    QUANTITY = (1, 1, 1, 2, 1, 1, 1, 1, 1)
    MAX_CODE = 2 ** len(TYPES)

    def __init__(self, code) -> None:
        self.code: Tuple[int] = tuple(code)
        assert len(self.code) == len(Code.QUANTITY)

    def __and__(self, other: 'Code') -> int:
        return sum(self.code[i] + other.code[i] > Code.QUANTITY[i] for i in range(len(Code.TYPES)))

    def __or__(self, other: 'Code') -> 'Code':
        return Code(tuple(self.code[i] + other.code[i] for i in range(len(Code.TYPES))))

    def __repr__(self) -> str:
        return str(self.code)

    def __hash__(self) -> int:
        return hash(self.code)

    def plus_one_ring(self) -> 'Code':
        return Code(tuple(x + 1 if k == 3 else x for k, x in enumerate(self.code)))

    def __eq__(self, other: 'Code'):
        return self.code == other.code

    def __ne__(self, other: 'Code'):
        return self.code != other.code

if __name__ == '__main__':
    manager = ItemsManager('stuff_data\\all_items.json', 'stuff_data\\all_item_sets.json')
    TYPES = Item.TYPES[:-1]
    MAX_CODE = 2 ** len(TYPES)
    ALL_CODES = [Code(tuple(map(int, f'{n:>09b}'))) for n in range(MAX_CODE)]
    ALL_CODES += [code.plus_one_ring() for code in ALL_CODES if code.code[3] == 1]

    AVAILABLE: Dict[Code, List[int]] = {code: [] for code in ALL_CODES}


    CODES: Dict[int, Code] = {}

    combinations: List[List[Tuple[Tuple[int], int]]] = [[((), -1)], []]

    for item_set in manager.item_sets.values():
        code = Code((len(item_set.items.get(item_type, [])) for item_type in TYPES))
        CODES[item_set.id] = code
        for inverse_code in ALL_CODES:
            if code & inverse_code == 0:
                AVAILABLE[inverse_code].append(item_set.id)
        combinations[1].append(((item_set.id, ), code))

    previous_size = 1
    while True:
        current_size_combinations = []
        for item_set_ids, code in combinations[previous_size]:
            current_size_combinations.extend([(item_set_ids + (new_item_set_id, ), code | CODES[new_item_set_id]) for new_item_set_id in AVAILABLE[code]])

        if len(current_size_combinations) == 0:
            break

        combinations.append(current_size_combinations)
        previous_size += 1

    flattened_combinations = []
    for sized_combinations in combinations:
        print(len(sized_combinations))
        flattened_combinations.extend([combination[0] for combination in sized_combinations])
    print(len(flattened_combinations))
    with open('stuff_data\\item_sets_combinations.json', 'w', encoding='utf-8') as fo:
        json.dump(flattened_combinations, fo, ensure_ascii=False)
