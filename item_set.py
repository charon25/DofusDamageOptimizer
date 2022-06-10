import json
import os
from typing import Dict, List, Union

from characteristics_damages import *
from item import Item
from stats import Stats


class ItemSet:
    def __init__(self) -> None:
        self.name: str = ''
        self.id: int = -1
        self.stats: Dict[int, Stats] = {}
        self.other_stats: Dict[int, Dict[str, float]] = {}
        # May be empty
        self.items: Dict[str, List[Item]] = {}
        # May be wrong
        self.level: int = 1


    def get_stats_page(self, quantity: int) -> Stats:
        if quantity <= 1:
            return Stats()
        
        return self.stats[quantity]

    def get_stats(self, quantity: int, stats: str) -> Union[int, float]:
        if quantity <= 1:
            return 0

        if stats in CHARACTERISTICS_ID:
            return self.stats[quantity].get_characteristic(CHARACTERISTICS_ID[stats])

        if stats in DAMAGES_ID:
            return self.stats[quantity].get_damage(DAMAGES_ID[stats])

        if stats in ('crit', '%crit'):
            return self.stats[quantity].get_bonus_crit_chance()

        if stats == 'pods':
            return self.other_stats[quantity].get('pods', 0) + self.stats[quantity].get_characteristic(STRENGTH) * 5
        elif stats in ('dodge', 'lock'):
            return self.other_stats[quantity].get(stats, 0) + self.stats[quantity].get_characteristic(AGILITY) / 10
        elif stats == 'prospec':
            return self.other_stats[quantity].get('prospec', 0) + self.stats[quantity].get_characteristic(LUCK) / 10
        elif stats in ('ap parry', 'mp parry', 'ap reduction', 'mp reduction'):
            return self.other_stats[quantity].get(stats, 0) + self.other_stats[quantity].get('wisdom', 0) / 10
        elif stats == 'init':
            return self.other_stats[quantity].get(stats, 0) + sum(self.stats[quantity].get_characteristic(characteristic) for characteristic in (STRENGTH, INTELLIGENCE, LUCK, AGILITY))

        return self.other_stats[quantity].get(stats, 0)


    def get_heuristic(self, quantity: int, heuristic: Dict[str, float]) -> float:
        return sum(self.get_stats(quantity, stats) * weight for stats, weight in heuristic.items())



    def to_dict(self):
        return {
            'name': self.name,
            'id': self.id,
            'stats': {quantity: stats.to_dict() for quantity, stats in self.stats.items()},
            'other_stats': self.other_stats
        }


    def __repr__(self) -> str:
        return f"Item set '{self.name}' ({self.id})"



    @classmethod
    def check_json_validity(cls, json_data):
        for field in ('name', 'id', 'stats', 'other_stats'):
            if not field in json_data:
                raise KeyError(f"JSON string does not contain a '{field}' field (ItemSet.check_json_validity).")

    @classmethod
    def from_json_data(cls, json_data: Dict) -> 'ItemSet':
        ItemSet.check_json_validity(json_data)
        
        item_set = ItemSet()
        item_set.name = json_data['name']
        item_set.id = json_data['id']

        for quantity, stats_data in json_data['stats'].items():
            quantity = int(quantity)
            item_set.stats[quantity] = Stats.from_dict(stats_data)

        item_set.other_stats = {int(key): value for key, value in json_data['other_stats'].items()}

        return item_set

    @classmethod
    def from_file(cls, filepath):
        if not (os.path.isfile(filepath) and os.access(filepath, os.R_OK)):
            raise FileNotFoundError(f"Cannot create item set from file {filepath}: file not found or innaccessible.")

        with open(filepath, 'r', encoding='utf-8') as fi:
            json_data = json.load(fi)

        return ItemSet.from_json_data(json_data)
