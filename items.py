import json
import os
import re
from typing import Dict

from characteristics_damages import *
from stats import Stats


class Item:
    def __init__(self) -> None:
        self.name: str = ''
        self.id: int = ''
        self.set: int = None
        self.type: str = ''
        self.stats: Dict[str, Stats] = {'min': Stats(), 'max': Stats()}
        self.other_stats: Dict[str, Dict[str, int]] = {'min': {}, 'max': {}}


    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'id': self.id,
            'set': self.set,
            'type': self.type,
            'stats': {field: self.stats[field].to_dict() for field in self.stats},
            'other_stats': self.other_stats
        }



    @classmethod
    def check_json_validity(cls, json_data):
        for field in ('name', 'type', 'id', 'set', 'stats', 'other_stats'):
            if not field in json_data:
                raise KeyError(f"JSON string does not contain a '{field}' field (Spell.check_json_validity).")

    @classmethod
    def from_json_data(cls, json_data):
        Item.check_json_validity(json_data)

        item = Item()
        item.name = json_data['name']
        item.id = json_data['id']
        item.set = json_data['set']
        item.type = json_data['type']
        item.stats['min'] = Stats.from_dict(json_data['stats']['min'])
        item.stats['max'] = Stats.from_dict(json_data['stats']['max'])
        item.other_stats = json_data['other_stats']

        return item

    @classmethod
    def from_file(cls, filepath):
        if not (os.path.isfile(filepath) and os.access(filepath, os.R_OK)):
            raise FileNotFoundError(f"Cannot create item from file {filepath}: file not found or innaccessible.")

        with open(filepath, 'r', encoding='utf-8') as fi:
            json_data = json.load(fi)

        return Item.from_json_data(json_data)
