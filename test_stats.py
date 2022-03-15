from operator import inv
import unittest

from stats import Damages, Elements, Stats


class TestStats(unittest.TestCase):

    def test_create_empty(self):
        empty_damages = {damage: 0 for damage in Damages}
        empty_elements = {element: 0 for element in Elements}

        stats = Stats()

        self.assertDictEqual(stats.elements, empty_elements)
        self.assertDictEqual(stats.damages, empty_damages)

    def test_create_from_invalid_json(self):
        invalid_json_string = '{'

        with self.assertRaises(ValueError):
            Stats.from_json_string(invalid_json_string)
    
    def test_create_from_incomplete_json(self):
        json_missing_both_fields = '{}'
        json_missing_elements_field = '{"damages": {}}'
        json_missing_damages_field = '{"elements": {}}'
        json_missing_elements = '{"damages": {}, "elements": {}}'
        json_missing_damages = '{{"damages": {{}}, "elements": {0}}}'.format({element.value: 0 for element in Elements})

        with self.assertRaises(ValueError):
            Stats.from_json_string(json_missing_both_fields)
        with self.assertRaises(ValueError):
            Stats.from_json_string(json_missing_elements_field)
        with self.assertRaises(ValueError):
            Stats.from_json_string(json_missing_damages_field)
        with self.assertRaises(ValueError):
            Stats.from_json_string(json_missing_elements)
        with self.assertRaises(ValueError):
            Stats.from_json_string(json_missing_damages)
    
    def test_create_from_valid_json(self):
        valid_json_string = '{{"damages": {0}, "elements": {1}}}'.format(
            {damage.value: 0 for damage in Damages},
            {element.value: 0 for element in Elements}
        ).replace("'", '"')

        stats = Stats.from_json_string(valid_json_string)


if __name__ == '__main__':
    unittest.main()
