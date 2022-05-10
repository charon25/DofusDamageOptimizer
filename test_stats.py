from copy import copy, deepcopy
import os
import time
import unittest

from characteristics_damages import *
from stats import Stats


class TestStats(unittest.TestCase):

    def test_create_empty(self):
        empty_characteristics = [0 for _ in range(CHARACTERISTICS_COUNT)]
        empty_damages = [0 for _ in range(DAMAGES_COUNT)]

        stats = Stats()

        self.assertListEqual(stats.characteristics, empty_characteristics)
        self.assertListEqual(stats.damages, empty_damages)

    def test_create_from_invalid_json(self):
        invalid_json_string = '{'

        with self.assertRaises(ValueError):
            Stats.from_json_string(invalid_json_string)

    def test_create_from_incomplete_json(self):
        json_missing_all_fields = '{}'
        json_missing_characteristics_field = '{"name": "name", "damages": {}}'
        json_missing_damages_field = '{"short_name": "sn", "bonus_crit_chance": 0, "name": "name", "characteristics": {}}'
        json_missing_bonus_crit_chance_field = '{"short_name": "sn", "name": "name", "damages": {}, "characteristics": {}}'
        json_missing_name_field = '{"short_name": "sn", "bonus_crit_chance": 0, "damages": {}, "characteristics": {}}'
        json_missing_short_name_field = '{"name": "name", "bonus_crit_chance": 0, "damages": {}, "characteristics": {}}'
        json_missing_characteristics = '{"bonus_crit_chance": 0, "damages": {}, "characteristics": {}, "name": ""}'
        # Double { and } because of .format
        json_missing_damages = '{{"short_name": "sn", "bonus_crit_chance": 0, "name": "name", "damages": {{}}, "characteristics": {0}}}'.format([0 for _ in range(CHARACTERISTICS_COUNT)]).replace("'", '"')

        with self.assertRaises(KeyError):
            Stats.from_json_string(json_missing_all_fields)
            Stats.from_json_string(json_missing_characteristics_field)
            Stats.from_json_string(json_missing_bonus_crit_chance_field)
            Stats.from_json_string(json_missing_name_field)
            Stats.from_json_string(json_missing_short_name_field)
            Stats.from_json_string(json_missing_damages_field)
            Stats.from_json_string(json_missing_characteristics)
            Stats.from_json_string(json_missing_damages)

    def test_create_from_valid_json(self):
        valid_json_string = '{{"short_name": "sn", "bonus_crit_chance": 0, "name": "name", "damages": {0}, "characteristics": {1}}}'.format(
            [0 for _ in range(DAMAGES_COUNT)],
            [0 for _ in range(CHARACTERISTICS_COUNT)]
        ).replace("'", '"')

        Stats.from_json_string(valid_json_string)

    def test_different_neutral_strength(self):
        json_string = '{{"short_name": "sn", "bonus_crit_chance": 0, "name": "", "damages": {0}, "characteristics": {1}}}'.format(
            [0 for _ in range(DAMAGES_COUNT)],
            [100 * (characteristic == NEUTRAL) for characteristic in range(CHARACTERISTICS_COUNT)]
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

        self.assertEqual(stats.get_characteristic(STRENGTH), 0)

        with self.assertRaises(TypeError):
            stats.get_characteristic("string")

    def test_set_characteristic(self):
        stats = Stats()

        stats.set_characteristic(INTELLIGENCE, 100)
        self.assertEqual(stats.get_characteristic(INTELLIGENCE), 100)

        with self.assertRaises(TypeError):
            stats.set_characteristic("string", 0)
            stats.set_characteristic(LUCK, "string")

    def test_neutral_strength_equality(self):
        stats = Stats()

        stats.set_characteristic(STRENGTH, 150)
        self.assertEqual(stats.get_characteristic(NEUTRAL), 150)

        with self.assertRaises(TypeError):
            stats.set_characteristic(NEUTRAL, 100)

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

    def test_set_short_name(self):
        stats = Stats()

        stats.set_short_name("name")
        self.assertEqual(stats.get_short_name(), "name")

        stats.set_short_name(42)
        self.assertEqual(stats.get_short_name(), "42")


    def test_valid_simple_addition(self):
        stats1 = Stats()
        stats1.set_characteristic(INTELLIGENCE, 100)
        stats1.set_damage(BASIC, 20)
        stats1.set_bonus_crit_chance(0.3)
        stats1.set_name("stats1")

        stats2 = Stats()
        stats2.set_characteristic(INTELLIGENCE, 80)
        stats2.set_damage(BASIC, 15)
        stats2.set_bonus_crit_chance(0.5)
        stats2.set_name("stats2")

        stats3 = stats1 + stats2

        self.assertEqual(stats3.get_characteristic(INTELLIGENCE), 100 + 80)
        self.assertEqual(stats3.get_damage(BASIC), 20 + 15)
        self.assertAlmostEqual(stats3.get_bonus_crit_chance(), 0.3 + 0.5)
        self.assertEqual(stats3.get_name(), "stats1")

    def test_valid_sum(self):
        stats1 = Stats()
        stats1.set_characteristic(AGILITY, 40)
        stats1.set_name('stats1')

        stats2 = Stats()
        stats2.set_characteristic(AGILITY, 50)

        stats3 = sum([stats1, stats2])

        self.assertEqual(stats3.get_characteristic(AGILITY), 40 + 50)

    def test_invalid_sum(self):
        stats1 = Stats()

        with self.assertRaises(TypeError):
            stats2 = stats1 + 1
            stats2 = stats1 + "string"

    def test_performance_deep_copy(self):
        stats = Stats()

        stats.set_characteristic(AGILITY, 779)
        stats.set_characteristic(LUCK, 86)
        stats.set_characteristic(STRENGTH, 101)
        stats.set_characteristic(INTELLIGENCE, 81)

        stats.set_damage(POWER, 121)
        stats.set_damage(BASIC, 17)
        stats.set_damage(NEUTRAL, 29)
        stats.set_damage(EARTH, 31)
        stats.set_damage(FIRE, 7)
        stats.set_damage(WATER, 7)
        stats.set_damage(AIR, 49)
        stats.set_damage(SPELL, 7)

        N = 10000

        t0 = time.perf_counter_ns()
        for _ in range(N):
            stats_copied = Stats.from_existing(stats)
        t1 = time.perf_counter_ns()

        print(f"\n{N} repetitions : {1e-6 * (t1 - t0):.1f} ms total ({1e-3 * (t1 - t0) / N:.1f} µs / copy)")

    def test_hash(self):
        stats = Stats()

        stats.set_characteristic(AGILITY, 779)
        stats.set_characteristic(LUCK, 86)
        stats.set_characteristic(STRENGTH, 101)
        stats.set_characteristic(INTELLIGENCE, 81)

        stats.set_damage(POWER, 121)
        stats.set_damage(BASIC, 17)
        stats.set_damage(NEUTRAL, 29)
        stats.set_damage(EARTH, 31)
        stats.set_damage(FIRE, 7)
        stats.set_damage(WATER, 7)
        stats.set_damage(AIR, 49)
        stats.set_damage(SPELL, 7)

        stats.set_bonus_crit_chance(0.54)

        stats2 = stats.copy()
        stats2.set_bonus_crit_chance(0.53)

        self.assertEqual(type(hash(stats)), int)
        self.assertNotEqual(hash(stats), hash(stats2))


if __name__ == '__main__':
    unittest.main()
