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
