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
        json_missing_characteristics_field = '{"damages": {}}'
        json_missing_damages_field = '{"characteristics": {}}'
        json_missing_characteristics = '{"damages": {}, "characteristics": {}}'
        json_missing_damages = '{{"damages": {{}}, "characteristics": {0}}}'.format({characteristic.value: 0 for characteristic in Characteristics})

        with self.assertRaises(ValueError):
            Stats.from_json_string(json_missing_both_fields)
        with self.assertRaises(ValueError):
            Stats.from_json_string(json_missing_characteristics_field)
        with self.assertRaises(ValueError):
            Stats.from_json_string(json_missing_damages_field)
        with self.assertRaises(ValueError):
            Stats.from_json_string(json_missing_characteristics)
        with self.assertRaises(ValueError):
            Stats.from_json_string(json_missing_damages)
    
    def test_create_from_valid_json(self):
        valid_json_string = '{{"damages": {0}, "characteristics": {1}}}'.format(
            {damage.value: 0 for damage in Damages},
            {characteristic.value: 0 for characteristic in Characteristics}
        ).replace("'", '"')

        Stats.from_json_string(valid_json_string)
    
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


if __name__ == '__main__':
    unittest.main()
