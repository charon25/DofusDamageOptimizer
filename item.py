import json
import os
import re
from typing import Dict, List

from characteristics_damages import *
from stats import Stats


class Equipment:
    def __init__(self) -> None:
        self.items: Dict[str, int] = {}
        self.name: str = ''


    def add_item(self, item_type: str, item_id: int):
        if not item_type in Item.TYPES:
            raise ValueError(f"Item type should be one of {Item.TYPES} ('{item_type}' given instead).")

        self.items[item_type] = item_id

    def remove_item(self, item_id_to_remove: int):
        removed_type = None
        for item_type, item_id in self.items.items():
            if item_id == item_id_to_remove:
                removed_type = item_type
        
        if removed_type is not None:
            self.items.pop(removed_type)
        
        return removed_type is not None


    def to_dict(self) -> Dict:
        return {
            'items': self.items,
            'name': self.name
        }


    def copy(self, new_name: str) -> 'Equipment':
        new_equipment = Equipment()
        new_equipment.items = {item_type: item_id for item_type, item_id in self.items.items()}
        new_equipment.name = new_name

        return new_equipment


    def __len__(self):
        return len(self.items)

    def __contains__(self, item_type: str):
        return item_type in self.items


    @classmethod
    def from_dict(cls, data: Dict) -> 'Equipment':
        equipment = Equipment()
        for item_type in data['items']:
            equipment.add_item(item_type, data['items'][item_type])
        equipment.name = data['name']
        return equipment


class Item:
    TYPES = ('hat', 'amulet', 'cloak', 'ring', 'weapon', 'shield', 'belt', 'boots', 'pet', 'dofus')
    QUANTITY = {'hat': 1, 'amulet': 1, 'cloak': 1, 'ring': 2, 'weapon': 1, 'shield': 1, 'belt': 1, 'boots': 1, 'pet': 1, 'dofus': 6}

    def __init__(self) -> None:
        self.name: str = ''
        self.id: int = -1
        self.set: int = None
        self.type: str = ''
        self.level: int = 1
        self.stats: Dict[str, Stats] = {'min': Stats(), 'ave': Stats(), 'max': Stats()}
        self.other_stats: Dict[str, Dict[str, float]] = {'min': {}, 'ave': {}, 'max': {}}


    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'id': self.id,
            'set': self.set,
            'type': self.type,
            'level': self.level,
            'stats': {field: self.stats[field].to_dict() for field in ('min', 'max')},
            'other_stats': {field: self.other_stats[field] for field in ('min', 'max')}
        }


    def __repr__(self) -> str:
        return f"Item '{self.name}' ({self.id})"


    @classmethod
    def check_json_validity(cls, json_data):
        for field in ('name', 'type', 'id', 'set', 'level', 'stats', 'other_stats'):
            if not field in json_data:
                raise KeyError(f"JSON string does not contain a '{field}' field (Item.check_json_validity).")

    @classmethod
    def from_json_data(cls, json_data):
        Item.check_json_validity(json_data)

        item = Item()
        item.name = json_data['name']
        item.id = json_data['id']
        item.set = json_data['set']
        item.type = json_data['type']
        item.level = json_data['level']
        item.stats['min'] = Stats.from_dict(json_data['stats']['min'])
        item.stats['max'] = Stats.from_dict(json_data['stats']['max'])
        item.stats['ave'] = (item.stats['min'] + item.stats['max'] ) / 2
        item.other_stats = json_data['other_stats']
        item.other_stats['ave'] = {}
        for field in item.other_stats['min']:
            item.other_stats['ave'][field] = (item.other_stats['min'][field] + item.other_stats['max'][field]) / 2

        return item

    @classmethod
    def from_file(cls, filepath):
        if not (os.path.isfile(filepath) and os.access(filepath, os.R_OK)):
            raise FileNotFoundError(f"Cannot create item from file {filepath}: file not found or innaccessible.")

        with open(filepath, 'r', encoding='utf-8') as fi:
            json_data = json.load(fi)

        return Item.from_json_data(json_data)
