import os
import unittest

from characteristics_damages import *
from damage_parameters import DamageParameters
from spell import Spell
from stats import Stats


class TestSpell(unittest.TestCase):

    def test_create_empty(self):
        empty_base_damages = [{'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0} for _ in range(CHARACTERISTICS_COUNT)]

        spell = Spell()

        self.assertListEqual(spell.parameters.base_damages, empty_base_damages)
        self.assertEqual(spell.parameters.crit_chance, 0.0)
        self.assertEqual(spell.parameters.uses_per_target, -1)
        self.assertEqual(spell.parameters.uses_per_turn, -1)

    def test_create_from_invalid_json(self):
        invalid_json_string = '{'

        with self.assertRaises(ValueError):
            Spell.from_json_string(invalid_json_string)

    def test_create_from_incomplete_json(self):
        json_missing_all_fields = '{}'
        json_missing_scalar_parameter = '{"base_damages": {}}'
        json_missing_base_damages = '{"short_name": "sn", "name": "name", "pa": 1, "crit_chance": 0, "uses_per_target": -1, "uses_per_turn": -1, "is_weapon": true}'
        # Double { and } because of .format
        json_missing_one_characteristic = '{{"pa": 1, "short_name": "sn", "name": "name", "crit_chance": 0, "uses_per_target": -1, "uses_per_turn": -1, "is_weapon": true, "base_damages": {0}}}'.format(
            [{'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0} for characteristic in range(CHARACTERISTICS_COUNT) if characteristic != LUCK]
        ).replace("'", '"')

        with self.assertRaises(KeyError):
            Spell.from_json_string(json_missing_all_fields)
            Spell.from_json_string(json_missing_scalar_parameter)
            Spell.from_json_string(json_missing_base_damages)
            Spell.from_json_string(json_missing_one_characteristic)

    def test_create_from_valid_json(self):
        valid_json_string = '{{"position": "all", "buffs": [], "short_name": "sn", "pa": 1, "po": [1, 5], "name": "name", "crit_chance": 0, "uses_per_target": -1, "uses_per_turn": -1, "is_weapon": false, "base_damages": {0}, "damaging_characteristics": []}}'.format(
             [{'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0} for characteristic in range(CHARACTERISTICS_COUNT)]
        ).replace("'", '"')

        Spell.from_json_string(valid_json_string)

    def test_create_from_file(self):
        filepath = 'test_files\\test_spell.json'
        # Check if the file still exists and is accessible
        assert os.path.isfile(filepath) and os.access(filepath, os.R_OK)
        spell = Spell.from_file(filepath)

        self.assertEqual(spell.get_name(), 'test spell')

    def test_get_base_damages(self):
        spell = Spell()
        empty_base_damages = {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0}

        self.assertDictEqual(spell.get_base_damages(STRENGTH), empty_base_damages)

        with self.assertRaises(TypeError):
            spell.get_base_damages("string")

    def test_set_characteristic(self):
        spell = Spell()
        damage = {'min': 10, 'max': 20, 'crit_min': 12, 'crit_max': 22}

        spell.set_base_damages(INTELLIGENCE, damage)
        self.assertDictEqual(spell.get_base_damages(INTELLIGENCE), damage)

        with self.assertRaises(TypeError):
            spell.set_base_damages("string", damage)
            spell.set_base_damages(STRENGTH, 0)
            spell.set_base_damages(AGILITY, {'min': 10, 'max': 20, 'crit_min': "string", 'crit_max': 22})

        with self.assertRaises(KeyError):
            spell.set_base_damages(LUCK, {})

    def test_set_pa(self):
        spell = Spell()

        spell.set_pa(4)
        self.assertEqual(spell.get_pa(), 4)

        with self.assertRaises(TypeError):
            spell.set_pa("string")

        with self.assertRaises(ValueError):
            spell.set_pa(0)

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
            spell.set_uses_per_turn(-5)

    def test_set_name(self):
        spell = Spell()

        spell.set_name("name")
        self.assertEqual(spell.get_name(), "name")

        spell.set_name(42)
        self.assertEqual(spell.get_name(), "42")

        spell.set_name('')
        self.assertNotEqual(spell.get_name(), "")

    def test_set_short_name(self):
        spell = Spell()

        spell.set_short_name("name")
        self.assertEqual(spell.get_short_name(), "name")

        spell.set_short_name(42)
        self.assertEqual(spell.get_short_name(), "42")

    def test_set_po(self):
        spell = Spell()

        spell.set_po(1, 5)

        self.assertEqual(spell.get_min_po(), 1)
        self.assertEqual(spell.get_max_po(), 5)

        spell.set_po(max_po=8)
        self.assertEqual(spell.get_min_po(), 1)
        self.assertEqual(spell.get_max_po(), 8)

        spell.set_po(min_po=3)
        self.assertEqual(spell.get_min_po(), 3)
        self.assertEqual(spell.get_max_po(), 8)

        spell.set_po(min_po=5, max_po=5)
        self.assertEqual(spell.get_min_po(), 5)
        self.assertEqual(spell.get_max_po(), 5)

        with self.assertRaises(TypeError):
            spell.set_po(min_po="string")
            spell.set_po(max_po="string")

        with self.assertRaises(ValueError):
            spell.set_po(min_po=-5)
            spell.set_po(max_po=-1)
            spell.set_po(min_po = 5, max_po=4)

    def test_no_damage(self):
        stats = Stats()
        spell = Spell()
        parameters = DamageParameters()

        self.assertAlmostEqual(spell.get_average_damages(stats, parameters), 0.0)

    def test_damage_simple_no_crit(self):
        stats = Stats()
        spell = Spell()
        parameters = DamageParameters()

        spell.add_damaging_characteristic(AGILITY)
        spell.set_base_damages(AGILITY, {'min': 10, 'max': 10, 'crit_min': 10, 'crit_max': 10})
        damage_no_var = spell.get_average_damages(stats, parameters) # (10 + 10) / 2

        spell.set_base_damages(AGILITY, {'min': 10, 'max': 16, 'crit_min': 10, 'crit_max': 10})
        damage_var = spell.get_average_damages(stats, parameters) # (10 + 16) / 2

        self.assertAlmostEqual(damage_no_var, 10)
        self.assertAlmostEqual(damage_var, 13)

    def test_damage_multiline_no_crit(self):
        stats = Stats()
        spell = Spell()
        parameters = DamageParameters()

        spell.add_damaging_characteristic(AGILITY)
        spell.add_damaging_characteristic(INTELLIGENCE)
        spell.set_base_damages(AGILITY, {'min': 10, 'max': 18, 'crit_min': 10, 'crit_max': 10})
        spell.set_base_damages(INTELLIGENCE, {'min': 20, 'max': 30, 'crit_min': 10, 'crit_max': 10})
        damage = spell.get_average_damages(stats, parameters) # (10 + 18) / 2 + (20 + 30) / 2

        self.assertAlmostEqual(damage, 39)

    def test_damage_crit(self):
        stats = Stats()
        spell = Spell()
        parameters = DamageParameters()

        spell.add_damaging_characteristic(LUCK)
        spell.set_base_damages(LUCK, {'min': 10, 'max': 20, 'crit_min': 50, 'crit_max': 70})
        spell.set_crit_chance(0.5)
        damage_no_bonus = spell.get_average_damages(stats, parameters) # 0.5 * (10 + 20) / 2 + 0.5 * (50 + 70) / 2

        stats.set_bonus_crit_chance(0.1)
        damage_bonus = spell.get_average_damages(stats, parameters) # 0.4 * (10 + 20) / 2 + 0.6 * (50 + 70) / 2

        self.assertAlmostEqual(damage_bonus, 42.0)

    def test_damage_too_much_crit_chance(self):
        stats = Stats()
        spell = Spell()
        parameters = DamageParameters()

        spell.add_damaging_characteristic(STRENGTH)
        spell.set_base_damages(STRENGTH, {'min': 10, 'max': 20, 'crit_min': 100, 'crit_max': 110})
        spell.set_crit_chance(0.8)
        stats.set_bonus_crit_chance(0.9)
        damage = spell.get_average_damages(stats, parameters) # 0 * (10 + 20) / 2 + 1 * (100 + 110) / 2

        self.assertAlmostEqual(damage, 105.0)

    def test_damage_multi_characteristics(self):
        stats = Stats()
        spell = Spell()
        parameters = DamageParameters()

        spell.add_damaging_characteristic(INTELLIGENCE)
        spell.add_damaging_characteristic(LUCK)
        spell.add_damaging_characteristic(STRENGTH)
        spell.set_base_damages(INTELLIGENCE, {'min': 10, 'max': 20, 'crit_min': 10, 'crit_max': 20})
        spell.set_base_damages(LUCK, {'min': 20, 'max': 30, 'crit_min': 20, 'crit_max': 30})
        spell.set_base_damages(STRENGTH, {'min': 30, 'max': 40, 'crit_min': 30, 'crit_max': 40})
        stats.set_characteristic(INTELLIGENCE, 100)
        stats.set_characteristic(LUCK, 200)

        damage = spell.get_average_damages(stats, parameters) # 15 * 2 + 25 * 3 + 35 * 1

        self.assertAlmostEqual(damage, 140.0)

    def test_damage_weapon(self):
        stats = Stats()
        spell = Spell()
        parameters = DamageParameters()

        spell.set_weapon(True)
        spell.add_damaging_characteristic(AGILITY)
        spell.set_base_damages(AGILITY, {'min': 10, 'max': 20, 'crit_min': 10, 'crit_max': 20})
        stats.set_damage(SPELL, 100)
        stats.set_damage(WEAPON_POWER, 300)

        damage = spell.get_average_damages(stats, parameters) # 15 * 4

        self.assertAlmostEqual(damage, 60.0)

    def test_neutral_damage(self):
        stats = Stats()
        spell = Spell()
        parameters = DamageParameters()

        spell.add_damaging_characteristic(NEUTRAL)
        spell.set_base_damages(NEUTRAL, {'min': 10, 'max': 20, 'crit_min': 10, 'crit_max': 20})
        stats.set_characteristic(STRENGTH, 200)
        stats.set_characteristic(INTELLIGENCE, 100)

        damage = spell.get_average_damages(stats, parameters) # 15 * 3

        self.assertAlmostEqual(damage, 45.0)

    def test_max_uses_single_target(self):
        spell = Spell()
        spell.set_pa(4)
        max_used_pa = 10

        spell.set_uses_per_target(-1) # Unlimited uses per target
        self.assertEqual(spell.get_max_uses_single_target(max_used_pa), 2) # 10 // 4

        spell.set_uses_per_target(1) # 1 use per target
        self.assertEqual(spell.get_max_uses_single_target(max_used_pa), 1) # min(1, 10 // 4)

        spell.set_uses_per_target(3) # 3 uses per target
        self.assertEqual(spell.get_max_uses_single_target(max_used_pa), 2) # min(3, 10 // 4)

    def test_max_uses_multiple_targets(self):
        spell = Spell()
        spell.set_pa(4)
        max_used_pa = 10

        spell.set_uses_per_turn(-1) # Unlimited uses per target
        self.assertEqual(spell.get_max_uses_multiple_targets(max_used_pa), 2) # 10 // 4

        spell.set_uses_per_turn(1) # 1 use per target
        self.assertEqual(spell.get_max_uses_multiple_targets(max_used_pa), 1) # min(1, 10 // 4)

        spell.set_uses_per_turn(3) # 3 uses per target
        self.assertEqual(spell.get_max_uses_multiple_targets(max_used_pa), 2) # min(3, 10 // 4)

    def test_detailed_damages_simple(self):
        stats = Stats()
        spell = Spell()
        parameters = DamageParameters()

        spell.add_damaging_characteristic(LUCK)
        spell.set_base_damages(LUCK, {'min': 10, 'max': 20, 'crit_min': 50, 'crit_max': 70})
        spell.set_crit_chance(0.1)
        stats.set_characteristic(LUCK, 100)
        stats.set_damage(CRIT, 10)
        spell_output = spell.get_detailed_damages(stats, parameters)

        self.assertListEqual(spell_output.damages_by_characteristic, [
            {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0},
            {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0},
            {'min': 20, 'max': 40, 'crit_min': 110, 'crit_max': 150},
            {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0},
            {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0}
        ])
        self.assertDictEqual(spell_output.damages, {
            'min': 20,
            'max': 40,
            'crit_min': 110,
            'crit_max': 150
        })
        self.assertAlmostEqual(spell_output.average_damage, 30)
        self.assertAlmostEqual(spell_output.average_damage_crit, 130)

    def test_detailed_damages_multiline(self):
        stats = Stats()
        spell = Spell()
        parameters = DamageParameters()

        spell.add_damaging_characteristic(LUCK)
        spell.add_damaging_characteristic(INTELLIGENCE)
        spell.add_damaging_characteristic(STRENGTH)
        spell.set_base_damages(LUCK, {'min': 10, 'max': 20, 'crit_min': 50, 'crit_max': 70})
        spell.set_base_damages(INTELLIGENCE, {'min': 5, 'max': 10, 'crit_min': 10, 'crit_max': 20})
        spell.set_base_damages(STRENGTH, {'min': 50, 'max': 60, 'crit_min': 60, 'crit_max': 70})
        spell.set_crit_chance(0.1)
        stats.set_characteristic(LUCK, 100)
        stats.set_characteristic(INTELLIGENCE, 200)
        stats.set_damage(CRIT, 10)
        stats.set_damage(FIRE, 20)
        spell_output = spell.get_detailed_damages(stats, parameters)

        self.assertListEqual(spell_output.damages_by_characteristic, [
            {'min': 50, 'max': 60, 'crit_min': 70, 'crit_max': 80},
            {'min': 35, 'max': 50, 'crit_min': 60, 'crit_max': 90},
            {'min': 20, 'max': 40, 'crit_min': 110, 'crit_max': 150},
            {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0},
            {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0}
        ])
        self.assertDictEqual(spell_output.damages, {
            'min': 105,
            'max': 150,
            'crit_min': 240,
            'crit_max': 320
        })
        self.assertAlmostEqual(spell_output.average_damage, (105 + 150) / 2)
        self.assertAlmostEqual(spell_output.average_damage_crit, (240 + 320) / 2)

    def test_create_from_file_with_buff(self):
        filepath = 'test_files\\test_spell_with_buff.json'
        # Check if the file still exists and is accessible
        assert os.path.isfile(filepath) and os.access(filepath, os.R_OK)
        spell = Spell.from_file(filepath)

        self.assertEqual(spell.get_name(), 'test spell')
        self.assertEqual(len(spell.buffs), 1)
        self.assertSetEqual(spell.buffs[0].trigger_states, {'trigger1', 'trigger2'})
        self.assertEqual(spell.buffs[0].stats['__all__'].get_characteristic(STRENGTH), 100)
        self.assertEqual(spell.buffs[0].damage_parameters['__all__'].vulnerability, 30)


if __name__ == '__main__':
    unittest.main()
