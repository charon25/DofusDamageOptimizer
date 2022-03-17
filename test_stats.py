import os
import unittest

from stats import Damages, Characteristics, Stats


class TestStats(unittest.TestCase):

    def test_create_empty(self):
        empty_damages = {damage: 0 for damage in Damages}
        empty_characteristics = {characteristic: 0 for characteristic in Characteristics}

        stats = Stats()

        self.assertDictEqual(stats.characteristics, empty_characteristics)
        self.assertDictEqual(stats.damages, empty_damages)

    def test_create_from_invalid_json(self):
        invalid_json_string = '{'

        with self.assertRaises(ValueError):
            Stats.from_json_string(invalid_json_string)

    def test_create_from_incomplete_json(self):
        json_missing_both_fields = '{}'
        json_missing_characteristics_field = '{"name": "name", "damages": {}}'
        json_missing_damages_field = '{"short_name": "sn", "bonus_crit_chance": 0, "name": "name", "characteristics": {}}'
        json_missing_bonus_crit_chance_field = '{"short_name": "sn", "name": "name", "damages": {}, "characteristics": {}}'
        json_missing_name_field = '{"short_name": "sn", "bonus_crit_chance": 0, "damages": {}, "characteristics": {}}'
        json_missing_short_name_field = '{"name": "name", "bonus_crit_chance": 0, "damages": {}, "characteristics": {}}'
        json_missing_characteristics = '{"bonus_crit_chance": 0, "damages": {}, "characteristics": {}, "name": ""}'
        # Double { and } because of .format
        json_missing_damages = '{{"short_name": "sn", "bonus_crit_chance": 0, "name": "name", "damages": {{}}, "characteristics": {0}}}'.format({characteristic.value: 0 for characteristic in Characteristics}).replace("'", '"')

        with self.assertRaises(KeyError):
            Stats.from_json_string(json_missing_both_fields)
        with self.assertRaises(KeyError):
            Stats.from_json_string(json_missing_characteristics_field)
        with self.assertRaises(KeyError):
            Stats.from_json_string(json_missing_bonus_crit_chance_field)
        with self.assertRaises(KeyError):
            Stats.from_json_string(json_missing_name_field)
        with self.assertRaises(KeyError):
            Stats.from_json_string(json_missing_short_name_field)
        with self.assertRaises(KeyError):
            Stats.from_json_string(json_missing_damages_field)
        with self.assertRaises(KeyError):
            Stats.from_json_string(json_missing_characteristics)
        with self.assertRaises(KeyError):
            Stats.from_json_string(json_missing_damages)

    def test_create_from_valid_json(self):
        valid_json_string = '{{"short_name": "sn", "bonus_crit_chance": 0, "name": "name", "damages": {0}, "characteristics": {1}}}'.format(
            {damage.value: 0 for damage in Damages},
            {characteristic.value: 0 for characteristic in Characteristics}
        ).replace("'", '"')

        Stats.from_json_string(valid_json_string)

    def test_different_neutral_strength(self):
        json_string = '{{"short_name": "sn", "bonus_crit_chance": 0, "name": "", "damages": {0}, "characteristics": {1}}}'.format(
            {damage.value: 0 for damage in Damages},
            {characteristic.value: (100 if characteristic == Characteristics.NEUTRAL else 0) for characteristic in Characteristics}
        ).replace("'", '"')

        with self.assertRaises(ValueError):
            Stats.from_json_string(json_string)

    def test_create_from_file(self):
        filepath = 'test_files\\test_stats.json'
        # Check if the file still exists and is accessible
        assert os.path.isfile(filepath) and os.access(filepath, os.R_OK)
        stats = Stats.from_file(filepath)

        self.assertEqual(stats.get_name(), 'test stats')
    
    def test_get_characteristic(self):
        stats = Stats()

        self.assertEqual(stats.get_characteristic(Characteristics.STRENGTH), 0)

        with self.assertRaises(TypeError):
            stats.get_characteristic("string")
    
    def test_set_characteristic(self):
        stats = Stats()

        stats.set_characteristic(Characteristics.INTELLIGENCE, 100)
        self.assertEqual(stats.get_characteristic(Characteristics.INTELLIGENCE), 100)

        with self.assertRaises(TypeError):
            stats.set_characteristic("string", 0)
        with self.assertRaises(TypeError):
            stats.set_characteristic(Characteristics.LUCK, "string")
        with self.assertRaises(ValueError):
            stats.set_characteristic(Characteristics.AGILITY, -100)

    def test_neutral_strength_equality(self):
        stats = Stats()

        stats.set_characteristic(Characteristics.STRENGTH, 150)
        self.assertEqual(stats.get_characteristic(Characteristics.NEUTRAL), 150)

        with self.assertRaises(TypeError):
            stats.set_characteristic(Characteristics.NEUTRAL, 100)

    def test_set_bonus_crit_chance(self):
        stats = Stats()

        stats.set_bonus_crit_chance(0.56)
        self.assertEqual(stats.get_bonus_crit_chance(), 0.56)
        stats.set_bonus_crit_chance(1)
        self.assertEqual(stats.get_bonus_crit_chance(), 1.0)

        with self.assertRaises(TypeError):
            stats.set_bonus_crit_chance("string")
        with self.assertRaises(ValueError):
            stats.set_bonus_crit_chance(1.5)

    def test_set_name(self):
        stats = Stats()

        stats.set_name("name")
        self.assertEqual(stats.get_name(), "name")

        stats.set_name(42)
        self.assertEqual(stats.get_name(), "42")
    

    def test_valid_simple_addition(self):
        stats1 = Stats()
        stats1.set_characteristic(Characteristics.INTELLIGENCE, 100)
        stats1.set_damage(Damages.BASIC, 20)
        stats1.set_bonus_crit_chance(0.3)
        stats1.set_name("stats1")

        stats2 = Stats()
        stats2.set_characteristic(Characteristics.INTELLIGENCE, 80)
        stats2.set_damage(Damages.BASIC, 15)
        stats2.set_bonus_crit_chance(0.5)
        stats2.set_name("stats2")

        stats3 = stats1 + stats2

        self.assertEqual(stats3.get_characteristic(Characteristics.INTELLIGENCE), 100 + 80)
        self.assertEqual(stats3.get_damage(Damages.BASIC), 20 + 15)
        self.assertAlmostEqual(stats3.get_bonus_crit_chance(), 0.3 + 0.5)
        self.assertEqual(stats3.get_name(), "stats1")
    
    def test_valid_sum(self):
        stats1 = Stats()
        stats1.set_characteristic(Characteristics.AGILITY, 40)
        stats1.set_name('stats1')

        stats2 = Stats()
        stats2.set_characteristic(Characteristics.AGILITY, 50)

        stats3 = sum([stats1, stats2])

        self.assertEqual(stats3.get_characteristic(Characteristics.AGILITY), 40 + 50)
    
    def test_invalid_sum(self):
        stats1 = Stats()

        with self.assertRaises(TypeError):
            stats2 = stats1 + 1
            stats2 = stats1 + "string"


if __name__ == '__main__':
    unittest.main()
