import os
import shutil
import unittest

from damage_parameters import DamageParameters
from spell import Spell, SpellBuff
from spell_chain import SpellChains
from spell_set import SpellSet
from stats import Characteristics, Damages, Stats


class TestSpellChain(unittest.TestCase):

    def test_get_sub_permutation_two_spells(self):
        chain = SpellChains()

        spell1 = Spell()
        spell1.set_pa(3)
        chain.add_spell(spell1)

        spell2 = Spell()
        spell2.set_pa(2)
        chain.add_spell(spell2)

        parameters = DamageParameters(pa=6)

        permutations = chain._get_permutations(parameters)

        permutations_set = set(tuple(permutation) for permutation in permutations)

        self.assertSetEqual(permutations_set, {
            (),
            (0,),
            (1,),
            (0, 1),
            (1, 0)
        })

    def test_get_sub_permutation_one_spell_multiple_times(self):
        chain = SpellChains()

        spell1 = Spell()
        spell1.set_pa(2)
        chain.add_spell(spell1)
        chain.add_spell(spell1)
        chain.add_spell(spell1)

        parameters = DamageParameters(pa=5)

        permutations = chain._get_permutations(parameters)

        permutations_set = set(tuple(permutation) for permutation in permutations)

        self.assertSetEqual(permutations_set, {
            (),
            (0,),
            (1,),
            (2,),
            (1, 0),
            (1, 2),
            (0, 1),
            (0, 2),
            (2, 0),
            (2, 1)
        })

    def test_get_sub_permutation_one_spell_too_much_pa(self):
        chain = SpellChains()

        spell1 = Spell()
        spell1.set_pa(3)
        chain.add_spell(spell1)

        spell2 = Spell()
        spell2.set_pa(10)
        chain.add_spell(spell2)

        parameters = DamageParameters(pa=5)

        permutations = chain._get_permutations(parameters)

        permutations_set = set(tuple(permutation) for permutation in permutations)

        self.assertSetEqual(permutations_set, {
            (),
            (0,),
        })

    def test_get_sub_permutation_multiple_spells(self):
        chain = SpellChains()

        spell1 = Spell()
        spell1.set_pa(3)
        chain.add_spell(spell1)

        spell2 = Spell()
        spell2.set_pa(1)
        chain.add_spell(spell2)

        spell3 = Spell()
        spell3.set_pa(2)
        chain.add_spell(spell3)

        spell4 = Spell()
        spell4.set_pa(4)
        chain.add_spell(spell4)

        parameters = DamageParameters(pa=8)

        permutations = chain._get_permutations(parameters)
        
        self.assertEqual(len(permutations), 35)


    def test_detailed_damages_one_permutation_no_buffs_no_stats_no_parameters(self):
        chain = SpellChains()

        spell1 = Spell()
        spell1.set_base_damages(Characteristics.AGILITY, {'min': 10, 'max': 12, 'crit_min': 20, 'crit_max': 22})
        spell2 = Spell()
        spell2.set_base_damages(Characteristics.AGILITY, {'min': 5, 'max': 7, 'crit_min': 15, 'crit_max': 17})

        stats = Stats()
        parameters = DamageParameters()

        chain.add_spell(spell1)
        chain.add_spell(spell2)

        damages, average_damages = chain._get_detailed_damages_of_permutation([0, 1], stats, parameters)

        self.assertDictEqual(damages, {'min': 10 + 5, 'max': 12 + 7, 'crit_min': 20 + 15, 'crit_max': 22 + 17})
        self.assertAlmostEqual(average_damages, 17)

    def test_detailed_damages_one_permutation_no_buffs_with_stats_no_parameters(self):
        chain = SpellChains()

        spell1 = Spell()
        spell1.set_base_damages(Characteristics.AGILITY, {'min': 10, 'max': 12, 'crit_min': 20, 'crit_max': 22})
        spell2 = Spell()
        spell2.set_base_damages(Characteristics.STRENGTH, {'min': 5, 'max': 7, 'crit_min': 15, 'crit_max': 17})

        stats = Stats()
        stats.set_characteristic(Characteristics.AGILITY, 100)
        stats.set_damage(Damages.BASIC, 10)
        stats.set_damage(Damages.CRIT, 2)
        parameters = DamageParameters()

        chain.add_spell(spell1)
        chain.add_spell(spell2)

        damages, _ = chain._get_detailed_damages_of_permutation([0, 1], stats, parameters)

        self.assertDictEqual(damages, {'min': 45, 'max': 51, 'crit_min': 79, 'crit_max': 85})

    def test_detailed_damages_one_permutation_no_buffs_with_stats_with_parameters(self):
        chain = SpellChains()

        spell1 = Spell()
        spell1.set_base_damages(Characteristics.AGILITY, {'min': 10, 'max': 12, 'crit_min': 20, 'crit_max': 22})
        spell2 = Spell()
        spell2.set_base_damages(Characteristics.STRENGTH, {'min': 5, 'max': 7, 'crit_min': 15, 'crit_max': 17})

        stats = Stats()
        stats.set_characteristic(Characteristics.AGILITY, 100)
        stats.set_damage(Damages.BASIC, 10)
        stats.set_damage(Damages.CRIT, 2)
        parameters = DamageParameters.from_string('-r 0 -100 0 0 0')

        chain.add_spell(spell1)
        chain.add_spell(spell2)

        damages, _ = chain._get_detailed_damages_of_permutation([0, 1], stats, parameters)

        self.assertDictEqual(damages, {'min': 60, 'max': 68, 'crit_min': 106, 'crit_max': 114})

    def test_detailed_damages_one_permutation_with_buffs_no_stats_no_parameters__stats(self):
        chain = SpellChains()

        spell1 = Spell()
        spell1.set_base_damages(Characteristics.AGILITY, {'min': 10, 'max': 12, 'crit_min': 20, 'crit_max': 22})

        buff = SpellBuff()
        buff_stats = Stats()
        buff_stats.set_characteristic(Characteristics.AGILITY, 100)
        buff.add_stats(buff_stats)
        spell1.add_buff(buff)

        spell2 = Spell()
        spell2.set_base_damages(Characteristics.AGILITY, {'min': 5, 'max': 7, 'crit_min': 15, 'crit_max': 17})

        stats = Stats()
        parameters = DamageParameters()

        chain.add_spell(spell1)
        chain.add_spell(spell2)

        damages, _ = chain._get_detailed_damages_of_permutation([0, 1], stats, parameters)

        self.assertDictEqual(damages, {'min': 20, 'max': 26, 'crit_min': 50, 'crit_max': 56})

    def test_detailed_damages_one_permutation_with_buffs_no_stats_no_parameters__states(self):
        chain = SpellChains()

        spell1 = Spell()
        spell1.set_base_damages(Characteristics.AGILITY, {'min': 1, 'max': 2, 'crit_min': 3, 'crit_max': 4})

        buff_spell1 = SpellBuff()
        buff_spell1.add_new_output_state('fire')
        buff_spell1.add_new_output_state('water')
        spell1.add_buff(buff_spell1)

        spell2 = Spell()
        spell2.set_base_damages(Characteristics.AGILITY, {'min': 10, 'max': 20, 'crit_min': 30, 'crit_max': 40})

        buff_spell2 = SpellBuff()
        buff_spell2.add_trigger_state('fire')
        buff_spell2.add_trigger_state('water')
        buff_spell2.add_removed_output_state('fire')
        buff_spell2.set_base_damages(Characteristics.AGILITY, 1000)
        spell2.add_buff(buff_spell2)

        spell3 = Spell()
        spell3.set_base_damages(Characteristics.AGILITY, {'min': 100, 'max': 200, 'crit_min': 300, 'crit_max': 400})

        buff_spell3 = SpellBuff()
        buff_spell3.add_trigger_state('fire')
        buff_spell3.add_removed_output_state('fire')
        buff_spell3.set_base_damages(Characteristics.AGILITY, 1000)
        spell3.add_buff(buff_spell3)

        stats = Stats()
        parameters = DamageParameters()

        chain.add_spell(spell1)
        chain.add_spell(spell2)
        chain.add_spell(spell3)

        damages, _ = chain._get_detailed_damages_of_permutation([0, 1, 2], stats, parameters)

        self.assertDictEqual(damages, {'min': 1111, 'max': 1222, 'crit_min': 1333, 'crit_max': 1444})

    def test_detailed_damages_two_permutations_with_buffs_no_stats_no_parameters__states(self):
        chain = SpellChains()

        spell1 = Spell()
        spell1.set_base_damages(Characteristics.AGILITY, {'min': 1, 'max': 2, 'crit_min': 3, 'crit_max': 4})

        buff_spell1 = SpellBuff()
        buff_spell1.add_new_output_state('fire')
        buff_spell1.add_new_output_state('water')
        spell1.add_buff(buff_spell1)

        spell2 = Spell()
        spell2.set_base_damages(Characteristics.AGILITY, {'min': 10, 'max': 20, 'crit_min': 30, 'crit_max': 40})

        buff_spell2 = SpellBuff()
        buff_spell2.add_trigger_state('fire')
        buff_spell2.add_trigger_state('water')
        buff_spell2.add_removed_output_state('fire')
        buff_spell2.set_base_damages(Characteristics.AGILITY, 1000)
        spell2.add_buff(buff_spell2)

        spell3 = Spell()
        spell3.set_base_damages(Characteristics.AGILITY, {'min': 100, 'max': 200, 'crit_min': 300, 'crit_max': 400})

        buff_spell3 = SpellBuff()
        buff_spell3.add_trigger_state('fire')
        buff_spell3.add_removed_output_state('fire')
        buff_spell3.set_base_damages(Characteristics.AGILITY, 1000)
        spell3.add_buff(buff_spell3)

        stats = Stats()
        parameters = DamageParameters()

        chain.add_spell(spell1)
        chain.add_spell(spell2)
        chain.add_spell(spell3)

        damages1, _ = chain._get_detailed_damages_of_permutation([0, 1, 2], stats, parameters)
        damages2, _ = chain._get_detailed_damages_of_permutation([1, 2, 0], stats, parameters)

        self.assertDictEqual(damages1, {'min': 1111, 'max': 1222, 'crit_min': 1333, 'crit_max': 1444})
        self.assertDictEqual(damages2, {'min': 111, 'max': 222, 'crit_min': 333, 'crit_max': 444})

    def test_detailed_damages_one_permutation_with_buffs_with_stats_with_parameters(self):
        chain = SpellChains()

        spell1 = Spell()
        spell1.set_base_damages(Characteristics.AGILITY, {'min': 1, 'max': 2, 'crit_min': 3, 'crit_max': 4})

        buff_spell1 = SpellBuff()
        buff_spell1.add_new_output_state('fire')
        buff_spell1_stats = Stats()
        buff_spell1_stats.set_characteristic(Characteristics.INTELLIGENCE, 100)
        buff_spell1.add_stats(buff_spell1_stats)
        buff_spell1_parameters = DamageParameters(vulnerability=100)
        buff_spell1.add_damage_parameters(buff_spell1_parameters)
        spell1.add_buff(buff_spell1)

        spell2 = Spell()

        buff_spell2 = SpellBuff()
        buff_spell2.add_trigger_state('fire')
        buff_spell2.add_removed_output_state('fire')
        buff_spell2.set_base_damages(Characteristics.INTELLIGENCE, 10)
        spell2.add_buff(buff_spell2)

        stats = Stats()
        stats.set_damage(Damages.AIR, 10)
        stats.set_characteristic(Characteristics.INTELLIGENCE, 100)
        parameters = DamageParameters.from_string('-r 0 0 0 0 -100')

        chain.add_spell(spell1)
        chain.add_spell(spell2)

        damages, _ = chain._get_detailed_damages_of_permutation([0, 1], stats, parameters)

        self.assertDictEqual(damages, {'min': 2 * (1 + 10) + 2 * (3 * 10), 'max':  2 * (2 + 10) + 2 * (3 * 10), 'crit_min':  2 * (3 + 10) + 2 * (3 * 10), 'crit_max':  2 * (4 + 10) + 2 * (3 * 10)})


    def test_detailed_damages_all_permutations_with_buffs_no_stats_no_parameters__states(self):
        chain = SpellChains()

        spell1 = Spell()
        spell1.set_base_damages(Characteristics.AGILITY, {'min': 1, 'max': 2, 'crit_min': 3, 'crit_max': 4})
        spell1.set_pa(2)
        spell1.set_short_name('s1')

        buff_spell1 = SpellBuff()
        buff_spell1.add_new_output_state('fire')
        buff_spell1.add_new_output_state('water')
        spell1.add_buff(buff_spell1)

        spell2 = Spell()
        spell2.set_base_damages(Characteristics.AGILITY, {'min': 10, 'max': 20, 'crit_min': 30, 'crit_max': 40})
        spell2.set_pa(2)
        spell2.set_short_name('s2')

        buff_spell2 = SpellBuff()
        buff_spell2.add_trigger_state('fire')
        buff_spell2.add_trigger_state('water')
        buff_spell2.add_removed_output_state('fire')
        buff_spell2.set_base_damages(Characteristics.AGILITY, 1000)
        spell2.add_buff(buff_spell2)

        spell3 = Spell()
        spell3.set_base_damages(Characteristics.AGILITY, {'min': 100, 'max': 200, 'crit_min': 300, 'crit_max': 400})
        spell3.set_pa(2)
        spell3.set_short_name('s3')

        buff_spell3 = SpellBuff()
        buff_spell3.add_trigger_state('fire')
        buff_spell3.add_removed_output_state('fire')
        buff_spell3.set_base_damages(Characteristics.AGILITY, 1000)
        spell3.add_buff(buff_spell3)

        stats = Stats()
        parameters = DamageParameters()
        parameters.pa = 6

        chain.add_spell(spell1)
        chain.add_spell(spell2)
        chain.add_spell(spell3)

        damages = chain.get_detailed_damages(stats, parameters)
        
        self.assertAlmostEqual(list(damages.values())[0][0], (1111 + 1222) / 2)
        self.assertTupleEqual(list(damages.keys())[0], ('s3', 's1', 's2'))

    def test_huppermage_states_simple(self):
        chain = SpellChains()

        spell1 = Spell()
        spell1.set_base_damages(Characteristics.AGILITY, {'min': 1, 'max': 2, 'crit_min': 3, 'crit_max': 4})
        buff_spell1 = SpellBuff()
        buff_spell1.is_huppermage_states = True
        buff_spell1.add_new_output_state('h:w')
        spell1.add_buff(buff_spell1)

        spell2 = Spell()
        spell2.set_base_damages(Characteristics.AGILITY, {'min': 10, 'max': 20, 'crit_min': 30, 'crit_max': 40})
        buff_spell2 = SpellBuff()
        buff_spell2.is_huppermage_states = True
        buff_spell2.add_new_output_state('h:a')
        spell2.add_buff(buff_spell2)

        spell3 = Spell()
        spell3.set_base_damages(Characteristics.AGILITY, {'min': 100, 'max': 200, 'crit_min': 300, 'crit_max': 400})

        stats = Stats()
        parameters = DamageParameters()

        chain.add_spell(spell1)
        chain.add_spell(spell2)
        chain.add_spell(spell3)

        damages, _ = chain._get_detailed_damages_of_permutation([0, 1, 2], stats, parameters)

        self.assertDictEqual(damages, {'min': 161, 'max': 322, 'crit_min': 483, 'crit_max': 644})
        chain = SpellChains()

        spell1 = Spell()
        spell1.set_base_damages(Characteristics.AGILITY, {'min': 1, 'max': 2, 'crit_min': 3, 'crit_max': 4})
        spell1.set_pa(2)
        spell1.set_short_name('s1')

        buff_spell1 = SpellBuff()
        buff_spell1.add_new_output_state('fire')
        buff_spell1.add_new_output_state('water')
        spell1.add_buff(buff_spell1)

        spell2 = Spell()
        spell2.set_base_damages(Characteristics.AGILITY, {'min': 10, 'max': 20, 'crit_min': 30, 'crit_max': 40})
        spell2.set_pa(2)
        spell2.set_short_name('s2')

        buff_spell2 = SpellBuff()
        buff_spell2.add_trigger_state('fire')
        buff_spell2.add_trigger_state('water')
        buff_spell2.add_removed_output_state('fire')
        buff_spell2.set_base_damages(Characteristics.AGILITY, 1000)
        spell2.add_buff(buff_spell2)

        spell3 = Spell()
        spell3.set_base_damages(Characteristics.AGILITY, {'min': 100, 'max': 200, 'crit_min': 300, 'crit_max': 400})
        spell3.set_pa(2)
        spell3.set_short_name('s3')

        buff_spell3 = SpellBuff()
        buff_spell3.add_trigger_state('fire')
        buff_spell3.add_removed_output_state('fire')
        buff_spell3.set_base_damages(Characteristics.AGILITY, 1000)
        spell3.add_buff(buff_spell3)

        stats = Stats()
        parameters = DamageParameters()
        parameters.pa = 6

        chain.add_spell(spell1)
        chain.add_spell(spell2)
        chain.add_spell(spell3)

        damages = chain.get_detailed_damages(stats, parameters)
        
        self.assertAlmostEqual(list(damages.values())[0][0], (1111 + 1222) / 2)
        self.assertTupleEqual(list(damages.keys())[0], ('s3', 's1', 's2'))

    def test_huppermage_states_same_state(self):
        chain = SpellChains()

        spell1 = Spell()
        spell1.set_base_damages(Characteristics.AGILITY, {'min': 1, 'max': 2, 'crit_min': 3, 'crit_max': 4})
        buff_spell1 = SpellBuff()
        buff_spell1.is_huppermage_states = True
        buff_spell1.add_new_output_state('h:w')
        spell1.add_buff(buff_spell1)

        spell2 = Spell()
        spell2.set_base_damages(Characteristics.AGILITY, {'min': 10, 'max': 20, 'crit_min': 30, 'crit_max': 40})
        buff_spell2 = SpellBuff()
        buff_spell2.is_huppermage_states = True
        buff_spell2.add_new_output_state('h:w')
        spell2.add_buff(buff_spell2)

        spell3 = Spell()
        spell3.set_base_damages(Characteristics.AGILITY, {'min': 100, 'max': 200, 'crit_min': 300, 'crit_max': 400})

        stats = Stats()
        parameters = DamageParameters()

        chain.add_spell(spell1)
        chain.add_spell(spell2)
        chain.add_spell(spell3)

        damages, _ = chain._get_detailed_damages_of_permutation([0, 1, 2], stats, parameters)

        self.assertDictEqual(damages, {'min': 111, 'max': 222, 'crit_min': 333, 'crit_max': 444})

    def test_huppermage_states_earth_fire(self):
        chain = SpellChains()

        spell1 = Spell()
        spell1.set_base_damages(Characteristics.AGILITY, {'min': 1, 'max': 2, 'crit_min': 3, 'crit_max': 4})
        buff_spell1 = SpellBuff()
        buff_spell1.is_huppermage_states = True
        buff_spell1.add_new_output_state('h:e')
        spell1.add_buff(buff_spell1)

        spell2 = Spell()
        spell2.set_base_damages(Characteristics.AGILITY, {'min': 10, 'max': 20, 'crit_min': 30, 'crit_max': 40})
        buff_spell2 = SpellBuff()
        buff_spell2.is_huppermage_states = True
        buff_spell2.add_new_output_state('h:f')
        spell2.add_buff(buff_spell2)

        spell3 = Spell()
        spell3.set_base_damages(Characteristics.AGILITY, {'min': 100, 'max': 200, 'crit_min': 300, 'crit_max': 400})

        stats = Stats()
        parameters = DamageParameters()

        chain.add_spell(spell1)
        chain.add_spell(spell2)
        chain.add_spell(spell3)

        damages, _ = chain._get_detailed_damages_of_permutation([0, 1, 2], stats, parameters)

        self.assertDictEqual(damages, {'min': int(11 + 150 * 1.15), 'max': int(22 + 300 * 1.15), 'crit_min': int(33 + 450 * 1.15), 'crit_max': int(44 + 600 * 1.15)})

    def test_huppermage_states_earth_fire_reversed_order(self):
        chain = SpellChains()

        spell1 = Spell()
        spell1.set_base_damages(Characteristics.AGILITY, {'min': 1, 'max': 2, 'crit_min': 3, 'crit_max': 4})
        buff_spell1 = SpellBuff()
        buff_spell1.is_huppermage_states = True
        buff_spell1.add_new_output_state('h:f')
        spell1.add_buff(buff_spell1)

        spell2 = Spell()
        spell2.set_base_damages(Characteristics.AGILITY, {'min': 10, 'max': 20, 'crit_min': 30, 'crit_max': 40})
        buff_spell2 = SpellBuff()
        buff_spell2.is_huppermage_states = True
        buff_spell2.add_new_output_state('h:e')
        spell2.add_buff(buff_spell2)

        spell3 = Spell()
        spell3.set_base_damages(Characteristics.AGILITY, {'min': 100, 'max': 200, 'crit_min': 300, 'crit_max': 400})

        stats = Stats()
        parameters = DamageParameters()

        chain.add_spell(spell1)
        chain.add_spell(spell2)
        chain.add_spell(spell3)

        damages, _ = chain._get_detailed_damages_of_permutation([0, 1, 2], stats, parameters)

        self.assertDictEqual(damages, {'min': int(11 + 150 * 1.15), 'max': int(22 + 300 * 1.15), 'crit_min': int(33 + 450 * 1.15), 'crit_max': int(44 + 600 * 1.15)})

    def test_huppermage_states_same_combination_twice(self):
        chain = SpellChains()

        spell1 = Spell()
        spell1.set_base_damages(Characteristics.AGILITY, {'min': 1, 'max': 2, 'crit_min': 3, 'crit_max': 4})
        buff_spell1 = SpellBuff()
        buff_spell1.is_huppermage_states = True
        buff_spell1.add_new_output_state('h:a')
        spell1.add_buff(buff_spell1)

        spell2 = Spell()
        spell2.set_base_damages(Characteristics.AGILITY, {'min': 10, 'max': 20, 'crit_min': 30, 'crit_max': 40})
        buff_spell2 = SpellBuff()
        buff_spell2.is_huppermage_states = True
        buff_spell2.add_new_output_state('h:f')
        spell2.add_buff(buff_spell2)

        spell3 = Spell()
        spell3.set_base_damages(Characteristics.AGILITY, {'min': 100, 'max': 200, 'crit_min': 300, 'crit_max': 400})
        buff_spell3 = SpellBuff()
        buff_spell3.is_huppermage_states = True
        buff_spell3.add_new_output_state('h:f')
        spell3.add_buff(buff_spell1)

        spell4 = Spell()
        spell4.set_base_damages(Characteristics.AGILITY, {'min': 1000, 'max': 2000, 'crit_min': 3000, 'crit_max': 4000})
        buff_spell4 = SpellBuff()
        buff_spell4.is_huppermage_states = True
        buff_spell4.add_new_output_state('h:a')
        spell4.add_buff(buff_spell4)

        spell5 = Spell()
        spell5.set_base_damages(Characteristics.AGILITY, {'min': 10000, 'max': 20000, 'crit_min': 30000, 'crit_max': 40000})

        stats = Stats()
        parameters = DamageParameters()

        chain.add_spell(spell1)
        chain.add_spell(spell2)
        chain.add_spell(spell3)
        chain.add_spell(spell4)
        chain.add_spell(spell5)

        damages, _ = chain._get_detailed_damages_of_permutation([0, 1, 2, 3, 4], stats, parameters)

        self.assertDictEqual(damages, {'min': 16661, 'max': 33322, 'crit_min': 49983, 'crit_max': 66644})

    def test_huppermage_states_one_spell_two_states(self):
        chain = SpellChains()

        spell1 = Spell()
        spell1.set_base_damages(Characteristics.AGILITY, {'min': 1, 'max': 2, 'crit_min': 3, 'crit_max': 4})
        buff_spell1 = SpellBuff()
        buff_spell1.is_huppermage_states = True
        buff_spell1.add_new_output_state('h:1w')
        buff_spell1.add_new_output_state('h:2e')
        spell1.add_buff(buff_spell1)

        spell2 = Spell()
        spell2.set_base_damages(Characteristics.AGILITY, {'min': 10, 'max': 20, 'crit_min': 30, 'crit_max': 40})

        stats = Stats()
        parameters = DamageParameters()

        chain.add_spell(spell1)
        chain.add_spell(spell2)

        damages, _ = chain._get_detailed_damages_of_permutation([0, 1], stats, parameters)

        self.assertDictEqual(damages, {'min': 16, 'max': 32, 'crit_min': 48, 'crit_max': 64})

    def test_huppermage_states_one_spell_two_states_earth_fire(self):
        chain = SpellChains()

        spell1 = Spell()
        spell1.set_base_damages(Characteristics.AGILITY, {'min': 1, 'max': 2, 'crit_min': 3, 'crit_max': 4})
        buff_spell1 = SpellBuff()
        buff_spell1.is_huppermage_states = True
        buff_spell1.add_new_output_state('h:e')
        spell1.add_buff(buff_spell1)

        spell2 = Spell()
        spell2.set_base_damages(Characteristics.AGILITY, {'min': 10, 'max': 20, 'crit_min': 30, 'crit_max': 40})
        buff_spell2 = SpellBuff()
        buff_spell2.is_huppermage_states = True
        buff_spell2.add_new_output_state('h:1f')
        buff_spell2.add_new_output_state('h:2a')
        spell2.add_buff(buff_spell2)

        spell3 = Spell()
        spell3.set_base_damages(Characteristics.AGILITY, {'min': 100, 'max': 200, 'crit_min': 300, 'crit_max': 400})

        stats = Stats()
        parameters = DamageParameters()

        chain.add_spell(spell1)
        chain.add_spell(spell2)
        chain.add_spell(spell3)

        damages, _ = chain._get_detailed_damages_of_permutation([0, 1, 2], stats, parameters)

        self.assertDictEqual(damages, {'min': int(11 + 150 * 1.15), 'max': int(22 + 300 * 1.15), 'crit_min': int(33 + 450 * 1.15), 'crit_max': int(44 + 600 * 1.15)})

    def test_huppermage_states_one_spell_two_states_earth_fire_in_wrong_order(self):
        chain = SpellChains()

        spell1 = Spell()
        spell1.set_base_damages(Characteristics.AGILITY, {'min': 1, 'max': 2, 'crit_min': 3, 'crit_max': 4})
        buff_spell1 = SpellBuff()
        buff_spell1.is_huppermage_states = True
        buff_spell1.add_new_output_state('h:e')
        spell1.add_buff(buff_spell1)

        spell2 = Spell()
        spell2.set_base_damages(Characteristics.AGILITY, {'min': 10, 'max': 20, 'crit_min': 30, 'crit_max': 40})
        buff_spell2 = SpellBuff()
        buff_spell2.is_huppermage_states = True
        buff_spell2.add_new_output_state('h:1a')
        buff_spell2.add_new_output_state('h:2f')
        spell2.add_buff(buff_spell2)

        spell3 = Spell()
        spell3.set_base_damages(Characteristics.AGILITY, {'min': 100, 'max': 200, 'crit_min': 300, 'crit_max': 400})

        stats = Stats()
        parameters = DamageParameters()

        chain.add_spell(spell1)
        chain.add_spell(spell2)
        chain.add_spell(spell3)

        damages, _ = chain._get_detailed_damages_of_permutation([0, 1, 2], stats, parameters)

        self.assertDictEqual(damages, {'min': 161, 'max': 322, 'crit_min': 483, 'crit_max': 644})

    def test_huppermage_states_best_combination(self):
        chain = SpellChains()

        spell1 = Spell()
        spell1.set_base_damages(Characteristics.AGILITY, {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0})
        buff_spell1 = SpellBuff()
        buff_spell1.is_huppermage_states = True
        buff_spell1.add_new_output_state('h:e')
        spell1.add_buff(buff_spell1)
        spell1.set_pa(1)
        spell1.set_short_name('s1')

        spell2 = Spell()
        spell2.set_base_damages(Characteristics.AGILITY, {'min': 0, 'max': 0, 'crit_min': 0, 'crit_max': 0})
        buff_spell2 = SpellBuff()
        buff_spell2.is_huppermage_states = True
        buff_spell2.add_new_output_state('h:f')
        spell2.add_buff(buff_spell2)
        spell2.set_pa(1)
        spell2.set_short_name('s2')

        spell3 = Spell()
        spell3.set_base_damages(Characteristics.AGILITY, {'min': 40, 'max': 40, 'crit_min': 40, 'crit_max': 40})
        spell3.set_pa(1)
        spell3.set_short_name('s3')

        stats = Stats()
        parameters = DamageParameters.from_string('-pa 3')

        chain.add_spell(spell1)
        chain.add_spell(spell2)
        chain.add_spell(spell3)

        damages = chain.get_detailed_damages(stats, parameters)

        self.assertAlmostEqual(list(damages.values())[0][0], 69.0)
        self.assertTupleEqual(list(damages.keys())[0], ('s2', 's1', 's3'))

if __name__ == '__main__':
    unittest.main()
