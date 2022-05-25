import json
import os
from typing import Dict, List

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


    def get_stats(self, quantity: int) -> Stats:
        if quantity <= 1:
            return Stats()
        
        return self.stats[quantity]


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

        item_set.other_stats = json_data['other_stats']

        return item_set

    @classmethod
    def from_file(cls, filepath):
        if not (os.path.isfile(filepath) and os.access(filepath, os.R_OK)):
            raise FileNotFoundError(f"Cannot create item set from file {filepath}: file not found or innaccessible.")

        with open(filepath, 'r', encoding='utf-8') as fi:
            json_data = json.load(fi)

        return ItemSet.from_json_data(json_data)
