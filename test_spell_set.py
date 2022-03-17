import os
import shutil
import unittest

from spell import Spell
from spell_set import SpellSet


class TestStats(unittest.TestCase):

    def test_create_empty(self):
        stats = SpellSet()

        self.assertListEqual(stats.spells, [])

    def test_create_from_invalid_json(self):
        invalid_json_string = '{'

        with self.assertRaises(ValueError):
            SpellSet.from_json_string(invalid_json_string)

    def test_create_from_incomplete_json(self):
        json_missing_all_fields = '{}'
        json_missing_spells_field = '{"name": "name", "short_name": "sn"}'
        json_missing_name_field = '{"spells": [], "short_name": "sn"}'
        json_missing_short_name_field = '{"name": "name", "spells": []}'
        json_spells_field_wrong_type = '{"name": "name", "short_name": "sn", "spells": 0}'

        with self.assertRaises(KeyError):
            SpellSet.from_json_string(json_missing_all_fields)
        with self.assertRaises(KeyError):
            SpellSet.from_json_string(json_missing_spells_field)
        with self.assertRaises(KeyError):
            SpellSet.from_json_string(json_missing_name_field)
        with self.assertRaises(KeyError):
            SpellSet.from_json_string(json_missing_short_name_field)
        with self.assertRaises(TypeError):
            SpellSet.from_json_string(json_spells_field_wrong_type)

    def test_create_from_valid_json(self):
        valid_json_string = '{"name": "name", "short_name": "sn", "spells": []}'

        SpellSet.from_json_string(valid_json_string)

    def test_populate_with_spells(self):
        spell1 = Spell()
        spell1.set_name('spell1')
        spell2 = Spell()
        spell2.set_name('spell2')
        spell3 = Spell()
        spell3.set_name('spell3')
        spell4 = Spell()

        spell_set = SpellSet()
        spell_set.add_spell(spell1)
        spell_set.add_spell(spell2)
        spell_set.add_spell(spell3)

        self.assertEqual(len(spell_set), 3)
        self.assertEqual(spell_set[0], spell1)
        self.assertEqual(spell_set[1].get_name(), 'spell2')
        self.assertTrue(spell1 in spell_set)
        self.assertFalse(spell4 in spell_set)


    def test_create_from_file(self):
        filepath = 'test_files\\test_spell_set.json'
        # Check if the file still exists and is accessible
        assert os.path.isfile(filepath) and os.access(filepath, os.R_OK)
        spell_set = SpellSet.from_file(filepath)

        self.assertEqual(len(spell_set), 2)
        self.assertEqual(spell_set[0].get_name(), 'spell1')
        self.assertEqual(spell_set[1].get_name(), 'spell2')

    def test_save_to_files(self):
        dirpath = 'test_files\\spell_set2'
        shutil.rmtree(dirpath)
        os.mkdir(dirpath)

        spell_set = SpellSet()
        spell1 = Spell()
        spell1.set_name('spell1')
        spell2 = Spell()
        spell2.set_name('spell 2')

        spell_set.add_spell(spell1)
        spell_set.add_spell(spell2)

        spell_set.save_to_files('test_files\\test_spell_set_saved.json', dirpath)

        self.assertTrue(os.path.isfile(f'{dirpath}\\spell1.json'))
        self.assertTrue(os.path.isfile(f'{dirpath}\\spell_2.json'))

    def test_set_name(self):
        spell_set = SpellSet()

        spell_set.set_name("name")
        self.assertEqual(spell_set.get_name(), "name")

        spell_set.set_name(42)
        self.assertEqual(spell_set.get_name(), "42")

        with self.assertRaises(ValueError):
            spell_set.set_name('')

    def test_set_short_name(self):
        spell_set = SpellSet()

        spell_set.set_short_name("name")
        self.assertEqual(spell_set.get_short_name(), "name")

        spell_set.set_short_name(42)
        self.assertEqual(spell_set.get_short_name(), "42")

        with self.assertRaises(ValueError):
            spell_set.set_short_name('')


if __name__ == '__main__':
    unittest.main()
