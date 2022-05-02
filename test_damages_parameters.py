import unittest

from damages_parameters import DamageParameters
from stats import Characteristics


class TestDamagesParameters(unittest.TestCase):

    def test_check_parameters_count(self):
        DamageParameters._check_parameter(['-a', '1'], count=1)
        DamageParameters._check_parameter(['-a'], count=0)

        with self.assertRaises(ValueError):
            DamageParameters._check_parameter(['-a', '1', '2', '3'], count=1)
        with self.assertRaises(ValueError):
            DamageParameters._check_parameter(['-a', '1'], count=2)

    def test_check_parameters_int(self):
        DamageParameters._check_parameter(['-a', '1', '213', '-5'], argument_type=int)

        with self.assertRaises(ValueError):
            DamageParameters._check_parameter(['-a', 'c'], argument_type=int)
        with self.assertRaises(ValueError):
            DamageParameters._check_parameter(['-a', '0', '1', 'c'], argument_type=int)
        with self.assertRaises(ValueError):
            DamageParameters._check_parameter(['-a', '0.1'], argument_type=int)

    def test_check_parameters_literals(self):
        DamageParameters._check_parameter(['-a', 'lit1', 'lit2'], literals=['lit1', 'lit2', 'lit3'])

        with self.assertRaises(ValueError):
            DamageParameters._check_parameter(['-a', 'c'], literals=['lit1'])
        with self.assertRaises(ValueError):
            DamageParameters._check_parameter(['-a', 'lit1', 'lit2', 'lit3', 'lit4'], literals=['lit1', 'lit2', 'lit3'])

    def test_assert_correct_parameters(self):
        damage_parameters = DamageParameters()

        with self.assertRaises(ValueError):
            damage_parameters.pa = -5
            damage_parameters._assert_correct_parameters()
        damage_parameters.pa = 1

        with self.assertRaises(ValueError):
            damage_parameters.po = [-1, 5]
            damage_parameters._assert_correct_parameters()

        with self.assertRaises(ValueError):
            damage_parameters.po = [4, 3]
            damage_parameters._assert_correct_parameters()

    def test_from_string_simple(self):
        string = '-pa 1 -po 3'

        damage_parameters = DamageParameters.from_string(string)

        self.assertEqual(damage_parameters.pa, 1)
        self.assertListEqual(damage_parameters.po, [3, 3])

    def test_from_string_with_default(self):
        default_string = '-pa 1 -po 3'
        string = '-pomax 8'

        default_parameters = DamageParameters.from_string(default_string)

        damage_parameters = DamageParameters.from_string(string, default_parameters)

        self.assertEqual(damage_parameters.pa, 1)
        self.assertListEqual(damage_parameters.po, [3, 8])

    def test_from_string_all_parameters(self):
        string = '-s a b c -pa 3 -pomin 1 -maxpo 6 -t multi -r 1 2 3 4 5 -d melee -v 15 -bdmg 8'

        damage_parameters = DamageParameters.from_string(string)

        self.assertListEqual(damage_parameters.stats, ['a', 'b', 'c'])
        self.assertEqual(damage_parameters.pa, 3)
        self.assertListEqual(damage_parameters.po, [1, 6])
        self.assertEqual(damage_parameters.type, 'multi')
        self.assertListEqual(damage_parameters.resistances, [1, 2, 3, 4, 5])
        self.assertEqual(damage_parameters.distance, 'melee')
        self.assertEqual(damage_parameters.vulnerability, 15)

    def test_to_string(self):
        string = '-s a b c -pa 3 -pomin 1 -pomax 6 -t multi -r 1 2 3 4 5 -d melee -v 15 -bdmg 8'

        damage_parameters = DamageParameters.from_string(string)

        self.assertEqual(damage_parameters.to_string(), string)

    def test_get_resistances_dict(self):
        string = '-r -10 0 10 20 30'

        damage_parameters = DamageParameters.from_string(string)

        self.assertDictEqual(damage_parameters.get_resistances_dict(), {
            Characteristics.NEUTRAL: -10,
            Characteristics.STRENGTH: 0,
            Characteristics.INTELLIGENCE: 10,
            Characteristics.LUCK: 20,
            Characteristics.AGILITY: 30
        })

    def test_addition_other(self):
        string1 = '-v 15 -bdmg 8'
        string2 = '-v 30 -bdmg 4'

        damage_parameters1 = DamageParameters.from_string(string1)
        damage_parameters2 = DamageParameters.from_string(string2)

        damage_parameters3 = damage_parameters1 + damage_parameters2

        self.assertEqual(damage_parameters3.vulnerability, 15 + 30)
        self.assertEqual(damage_parameters3.base_damages, 8 + 4)

    def test_addition_int(self):
        string1 = '-v 15 -bdmg 8'

        damage_parameters1 = DamageParameters.from_string(string1)

        damage_parameters3 = damage_parameters1 + 10

        self.assertEqual(damage_parameters3.vulnerability, 15)
        self.assertEqual(damage_parameters3.base_damages, 8)

if __name__ == '__main__':
    unittest.main()
