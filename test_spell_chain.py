import os
import shutil
import unittest

from damages_parameters import DamageParameters
from spell import Spell
from spell_chain import SpellChain
from spell_set import SpellSet


class TestStats(unittest.TestCase):

    def test_get_sub_permutation_two_spells(self):
        chain = SpellChain()

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
        chain = SpellChain()

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
        chain = SpellChain()

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
        chain = SpellChain()

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


if __name__ == '__main__':
    unittest.main()
