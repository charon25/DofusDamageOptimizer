import json
import os
import unittest

from characteristics_damages import *
from damage_parameters import DamageParameters
from item import Item
from spell import Spell


class TestItem(unittest.TestCase):

    def test_create_empty(self):
        item = Item()

        self.assertEqual(item.name, '')
        self.assertEqual(item.id, 0)
        self.assertEqual(item.set, None)
        self.assertEqual(item.type, '')
        self.assertEqual(len(item.stats), 2)
        self.assertEqual(len(item.other_stats), 2)

    def test_create_from_valid_json(self):
        valid_json_string = '{"name": "Kanigloups", "id": 0, "set": 1000267, "type": "Familier", "stats": {"min": {"characteristics": [0, 0, 120, 0, 0], "damages": [0, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0, 0, 0, 0], "bonus_crit_chance": 0.0, "name": "", "short_name": ""}, "max": {"characteristics": [0, 0, 120, 0, 0], "damages": [0, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0, 0, 0, 0], "bonus_crit_chance": 0.0, "name": "", "short_name": ""}}, "other_stats": {"min": {}, "max": {}}}'

        Item.from_json_data(json.loads(valid_json_string))


if __name__ == '__main__':
    unittest.main()
