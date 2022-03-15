import unittest

from spell import Spell
from stats import Characteristics


class TestStats(unittest.TestCase):

    def test_create_empty(self):
        empty_damages = {characteristic: {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0} for characteristic in Characteristics}

        spell = Spell()

        self.assertDictEqual(spell.damages, empty_damages)
        self.assertEqual(spell.crit_chance, 0.0)
        self.assertEqual(spell.uses_per_target, -1)
        self.assertEqual(spell.uses_per_turn, -1)

    def test_create_from_invalid_json(self):
        invalid_json_string = '{'

        with self.assertRaises(ValueError):
            Spell.from_json_string(invalid_json_string)

    def test_create_from_incomplete_json(self):
        json_missing_all = '{}'
        json_missing_scalar_parameter = '{"damages": {}}'
        json_missing_damages = '{"crit_chance": 0, "uses_per_target": -1, "uses_per_turn": -1}'
        # Double { and } because of .format
        json_missing_one_characteristic = '{{"crit_chance": 0, "uses_per_target": -1, "uses_per_turn": -1, "damages": {0}}}'.format(
            {characteristic.value: {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0} for characteristic in Characteristics if characteristic != Characteristics.LUCK}
        ).replace("'", '"')

        with self.assertRaises(KeyError):
            Spell.from_json_string(json_missing_all)
        with self.assertRaises(KeyError):
            Spell.from_json_string(json_missing_scalar_parameter)
        with self.assertRaises(KeyError):
            Spell.from_json_string(json_missing_damages)
        with self.assertRaises(KeyError):
            Spell.from_json_string(json_missing_one_characteristic)
    
    def test_create_from_valid_json(self):
        valid_json_string = '{{"crit_chance": 0, "uses_per_target": -1, "uses_per_turn": -1, "damages": {0}}}'.format(
            {characteristic.value: {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0} for characteristic in Characteristics}
        ).replace("'", '"')

        Spell.from_json_string(valid_json_string)
    
    def test_get_damages(self):
        stats = Spell()
        empty_damages = {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0}

        self.assertDictEqual(stats.get_damages(Characteristics.STRENGTH), empty_damages)

        with self.assertRaises(TypeError):
            stats.get_damages("string")
    
    def test_set_characteristic(self):
        stats = Spell()
        damage = {'min': 10, 'max': 20, 'crit_min': 12, 'crit_max': 22}

        stats.set_damages(Characteristics.INTELLIGENCE, damage)
        self.assertDictEqual(stats.get_damages(Characteristics.INTELLIGENCE), damage)

        with self.assertRaises(TypeError):
            stats.set_damages("string", damage)
        with self.assertRaises(TypeError):
            stats.set_damages(Characteristics.STRENGTH, 0)
        with self.assertRaises(KeyError):
            stats.set_damages(Characteristics.LUCK, {})
        with self.assertRaises(TypeError):
            stats.set_damages(Characteristics.AGILITY, {'min': 10, 'max': 20, 'crit_min': "string", 'crit_max': 22})
        with self.assertRaises(ValueError):
            stats.set_damages(Characteristics.AGILITY, {'min': -10, 'max': 20, 'crit_min': 12, 'crit_max': 22})


if __name__ == '__main__':
    unittest.main()
