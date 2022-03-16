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
        json_missing_characteristics_field = '{"name": "", "damages": {}}'
        json_missing_damages_field = '{"name": "", "characteristics": {}}'
        json_missing_name_field = '{"damages": {}, "characteristics": {}}'
        json_missing_characteristics = '{"damages": {}, "characteristics": {}, "name": ""}'
        # Double { and } because of .format
        json_missing_damages = '{{"name": "", "damages": {{}}, "characteristics": {0}}}'.format({characteristic.value: 0 for characteristic in Characteristics}).replace("'", '"')

        with self.assertRaises(KeyError):
            Stats.from_json_string(json_missing_both_fields)
        with self.assertRaises(KeyError):
            Stats.from_json_string(json_missing_characteristics_field)
        with self.assertRaises(KeyError):
            Stats.from_json_string(json_missing_name_field)
        with self.assertRaises(KeyError):
            Stats.from_json_string(json_missing_damages_field)
        with self.assertRaises(KeyError):
            Stats.from_json_string(json_missing_characteristics)
        with self.assertRaises(KeyError):
            Stats.from_json_string(json_missing_damages)

    def test_create_from_valid_json(self):
        valid_json_string = '{{"name": "name", "damages": {0}, "characteristics": {1}}}'.format(
            {damage.value: 0 for damage in Damages},
            {characteristic.value: 0 for characteristic in Characteristics}
        ).replace("'", '"')

        Stats.from_json_string(valid_json_string)

    def test_different_neutral_strength(self):
        json_string = '{{"name": "", "damages": {0}, "characteristics": {1}}}'.format(
            {damage.value: 0 for damage in Damages},
            {characteristic.value: (100 if characteristic == Characteristics.NEUTRAL else 0) for characteristic in Characteristics}
        ).replace("'", '"')

        with self.assertRaises(ValueError):
            Stats.from_json_string(json_string)
    
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
    
    def test_set_name(self):
        stats = Stats()

        stats.set_name("name")
        self.assertEqual(stats.get_name(), "name")

        stats.set_name(42)
        self.assertEqual(stats.get_name(), "42")


if __name__ == '__main__':
    unittest.main()
