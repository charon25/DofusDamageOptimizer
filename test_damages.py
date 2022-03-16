import unittest

from damages import compute_damage
from spell import Spell
from stats import Damages, Characteristics, Stats


class TestDamages(unittest.TestCase):
    
    def test_no_stats(self):
        stats = Stats()

        damage_spell_no_crit = compute_damage(10, stats, Characteristics.AGILITY, is_melee=False, is_crit=False)
        damage_melee_no_crit = compute_damage(10, stats, Characteristics.AGILITY, is_melee=True, is_crit=False)
        damage_spell_crit = compute_damage(10, stats, Characteristics.AGILITY, is_melee=False, is_crit=True)
        damage_melee_crit = compute_damage(10, stats, Characteristics.AGILITY, is_melee=True, is_crit=True)

        self.assertEqual(damage_spell_no_crit, 10)
        self.assertEqual(damage_melee_no_crit, 10)
        self.assertEqual(damage_spell_crit, 10)
        self.assertEqual(damage_melee_crit, 10)
    
    def test_only_caracteristic_multiplier(self):
        stats = Stats()

        stats.set_characteristic(Characteristics.AGILITY, 100)
        damage = compute_damage(10, stats, Characteristics.AGILITY, is_melee=False) # 10 * (1 + 100 / 100)

        stats.set_damage(Damages.POWER, 50)
        damage2 = compute_damage(10, stats, Characteristics.AGILITY, is_melee=False) # 10 * (1 + (100 + 50) / 100)

        damage3 = compute_damage(10, stats, Characteristics.INTELLIGENCE, is_melee=False) # 10 * (1 + 50 / 100)

        self.assertEqual(damage, 20)
        self.assertEqual(damage2, 25)
        self.assertEqual(damage3, 15)
    
    def test_flat_damages(self):
        stats = Stats()

        stats.set_damage(Damages.BASIC, 12)
        damage = compute_damage(10, stats, Characteristics.STRENGTH, is_melee=False) # 10 + 12

        stats.set_damage(Damages.EARTH, 7)
        damage2 = compute_damage(10, stats, Characteristics.STRENGTH, is_melee=False) # 10 + 12 + 7

        damage3 = compute_damage(10, stats, Characteristics.INTELLIGENCE, is_melee=False) # 10 + 12

        self.assertEqual(damage, 22)
        self.assertEqual(damage2, 29)
        self.assertEqual(damage3, 22)

    def test_caracteristic_and_flat_damages(self):
        stats = Stats()

        stats.set_characteristic(Characteristics.LUCK, 200)
        stats.set_damage(Damages.BASIC, 23)

        damage = compute_damage(10, stats, Characteristics.LUCK, is_melee=False) # 10 * (1 + 200 / 100) + 23

        self.assertEqual(damage, 53)

    def test_crit_damage(self):
        stats = Stats()

        stats.set_damage(Damages.CRIT, 30)

        damage_no_crit = compute_damage(10, stats, Characteristics.LUCK, is_melee=False, is_crit=False) # 10
        damage_crit = compute_damage(10, stats, Characteristics.LUCK, is_melee=False, is_crit=True) # 10 + 30

        self.assertEqual(damage_no_crit, 10)
        self.assertEqual(damage_crit, 40)

    def test_weapon_power(self):
        stats = Stats()

        stats.set_damage(Damages.WEAPON_POWER, 300)
        damage_spell = compute_damage(10, stats, Characteristics.STRENGTH, is_melee=False) # 10
        damage_melee = compute_damage(10, stats, Characteristics.STRENGTH, is_melee=True) # 10 * (1 + 300 / 100)

        stats.set_characteristic(Characteristics.STRENGTH, 50)
        damage_spell_with_caracteristic = compute_damage(10, stats, Characteristics.STRENGTH, is_melee=False) # 10 * (1 + 50 / 100)
        damage_melee_with_caracteristic = compute_damage(10, stats, Characteristics.STRENGTH, is_melee=True) # 10 * (1 + (50 + 300) / 100)

        self.assertEqual(damage_spell, 10)
        self.assertEqual(damage_melee, 40)
        self.assertEqual(damage_spell_with_caracteristic, 15)
        self.assertEqual(damage_melee_with_caracteristic, 45)

    def test_final_damages(self):
        stats = Stats()

        stats.set_damage(Damages.SPELL, 10)
        stats.set_damage(Damages.WEAPON, 30)
        damage_spell = compute_damage(10, stats, Characteristics.INTELLIGENCE, is_melee=False) # 10 * (1 + 10 / 100)
        damage_melee = compute_damage(10, stats, Characteristics.INTELLIGENCE, is_melee=True) # 10 * (1 + 30 / 100)

        stats.set_damage(Damages.FINAL, 14)
        damage_spell_with_final = compute_damage(10, stats, Characteristics.INTELLIGENCE, is_melee=False) # 10 * (1 + (10 + 14) / 100)
        damage_melee_with_final = compute_damage(10, stats, Characteristics.INTELLIGENCE, is_melee=True) # 10 * (1 + (30 + 14) / 100)

        self.assertEqual(damage_spell_with_final, 12)
        self.assertEqual(damage_melee_with_final, 14)

    def test_complete(self):
        stats = Stats()

        stats.set_characteristic(Characteristics.AGILITY, 233)
        stats.set_damage(Damages.POWER, 78)
        stats.set_damage(Damages.BASIC, 12)
        stats.set_damage(Damages.AIR, 34)
        stats.set_damage(Damages.FIRE, 8)
        stats.set_damage(Damages.SPELL, 10)
        stats.set_damage(Damages.WEAPON_POWER, 149)
        stats.set_damage(Damages.WEAPON, 17)
        stats.set_damage(Damages.CRIT, 10)
        stats.set_damage(Damages.FINAL, 45)

        damage_spell_no_crit = compute_damage(20, stats, Characteristics.AGILITY, is_melee=False, is_crit=False)
        damage_melee_no_crit = compute_damage(20, stats, Characteristics.AGILITY, is_melee=True, is_crit=False)
        damage_spell_crit = compute_damage(20, stats, Characteristics.AGILITY, is_melee=False, is_crit=True)
        damage_melee_crit = compute_damage(20, stats, Characteristics.AGILITY, is_melee=True, is_crit=True)

        self.assertEqual(damage_spell_no_crit, 198)
        self.assertEqual(damage_melee_no_crit, 255)
        self.assertEqual(damage_spell_crit, 214)
        self.assertEqual(damage_melee_crit, 272)


if __name__ == '__main__':
    unittest.main()
