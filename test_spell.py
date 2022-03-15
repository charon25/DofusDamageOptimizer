import unittest

from spell import Spell
from stats import Characteristics


class TestSpell(unittest.TestCase):

    def test_create_empty(self):
        empty_base_damages = {characteristic: {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0} for characteristic in Characteristics}

        spell = Spell()

        self.assertDictEqual(spell.base_damages, empty_base_damages)
        self.assertEqual(spell.crit_chance, 0.0)
        self.assertEqual(spell.uses_per_target, -1)
        self.assertEqual(spell.uses_per_turn, -1)

    def test_create_from_invalid_json(self):
        invalid_json_string = '{'

        with self.assertRaises(ValueError):
            Spell.from_json_string(invalid_json_string)

    def test_create_from_incomplete_json(self):
        json_missing_all = '{}'
        json_missing_scalar_parameter = '{"base_damages": {}}'
        json_missing_base_damages = '{"crit_chance": 0, "uses_per_target": -1, "uses_per_turn": -1}'
        # Double { and } because of .format
        json_missing_one_characteristic = '{{"crit_chance": 0, "uses_per_target": -1, "uses_per_turn": -1, "base_damages": {0}}}'.format(
            {characteristic.value: {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0} for characteristic in Characteristics if characteristic != Characteristics.LUCK}
        ).replace("'", '"')

        with self.assertRaises(KeyError):
            Spell.from_json_string(json_missing_all)
        with self.assertRaises(KeyError):
            Spell.from_json_string(json_missing_scalar_parameter)
        with self.assertRaises(KeyError):
            Spell.from_json_string(json_missing_base_damages)
        with self.assertRaises(KeyError):
            Spell.from_json_string(json_missing_one_characteristic)
    
    def test_create_from_valid_json(self):
        valid_json_string = '{{"crit_chance": 0, "uses_per_target": -1, "uses_per_turn": -1, "base_damages": {0}}}'.format(
            {characteristic.value: {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0} for characteristic in Characteristics}
        ).replace("'", '"')

        Spell.from_json_string(valid_json_string)
    
    def test_get_base_damages(self):
        spell = Spell()
        empty_base_damages = {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0}

        self.assertDictEqual(spell.get_base_damages(Characteristics.STRENGTH), empty_base_damages)

        with self.assertRaises(TypeError):
            spell.get_base_damages("string")
    
    def test_set_characteristic(self):
        spell = Spell()
        damage = {'min': 10, 'max': 20, 'crit_min': 12, 'crit_max': 22}

        spell.set_base_damages(Characteristics.INTELLIGENCE, damage)
        self.assertDictEqual(spell.get_base_damages(Characteristics.INTELLIGENCE), damage)

        with self.assertRaises(TypeError):
            spell.set_base_damages("string", damage)
        with self.assertRaises(TypeError):
            spell.set_base_damages(Characteristics.STRENGTH, 0)
        with self.assertRaises(KeyError):
            spell.set_base_damages(Characteristics.LUCK, {})
        with self.assertRaises(TypeError):
            spell.set_base_damages(Characteristics.AGILITY, {'min': 10, 'max': 20, 'crit_min': "string", 'crit_max': 22})
        with self.assertRaises(ValueError):
            spell.set_base_damages(Characteristics.AGILITY, {'min': -10, 'max': 20, 'crit_min': 12, 'crit_max': 22})
    
    def test_set_crit_chance(self):
        spell = Spell()
        
        spell.set_crit_chance(0.5)
        self.assertEqual(spell.get_crit_chance(), 0.5)
        spell.set_crit_chance(1)
        self.assertEqual(spell.get_crit_chance(), 1.0)

        with self.assertRaises(TypeError):
            spell.set_crit_chance("string")
        with self.assertRaises(ValueError):
            spell.set_crit_chance(1.5)

    def test_set_uses_per_target(self):
        spell = Spell()
        
        spell.set_uses_per_target(-1)
        self.assertEqual(spell.get_uses_per_target(), -1)
        spell.set_uses_per_target(2)
        self.assertEqual(spell.get_uses_per_target(), 2)

        with self.assertRaises(TypeError):
            spell.set_uses_per_target("string")
        with self.assertRaises(ValueError):
            spell.set_uses_per_target(0)
        with self.assertRaises(ValueError):
            spell.set_uses_per_target(-5)

    def test_set_uses_per_turn(self):
        spell = Spell()
        
        spell.set_uses_per_turn(-1)
        self.assertEqual(spell.get_uses_per_turn(), -1)
        spell.set_uses_per_turn(2)
        self.assertEqual(spell.get_uses_per_turn(), 2)

        with self.assertRaises(TypeError):
            spell.set_uses_per_turn("string")
        with self.assertRaises(ValueError):
            spell.set_uses_per_turn(0)
        with self.assertRaises(ValueError):
            spell.set_uses_per_turn(-5)


if __name__ == '__main__':
    unittest.main()
