import unittest

from damages import compute_damage
from stats import Damages, Characteristics, Stats


class TestDamages(unittest.TestCase):

    def test_no_stats(self):
        stats = Stats()

        damage_spell_no_crit = compute_damage(10, stats, Characteristics.AGILITY, is_weapon=False, is_crit=False)
        damage_weapon_no_crit = compute_damage(10, stats, Characteristics.AGILITY, is_weapon=True, is_crit=False)
        damage_spell_crit = compute_damage(10, stats, Characteristics.AGILITY, is_weapon=False, is_crit=True)
        damage_weapon_crit = compute_damage(10, stats, Characteristics.AGILITY, is_weapon=True, is_crit=True)

        self.assertEqual(damage_spell_no_crit, 10)
        self.assertEqual(damage_weapon_no_crit, 10)
        self.assertEqual(damage_spell_crit, 10)
        self.assertEqual(damage_weapon_crit, 10)

    def test_resistance(self):
        stats = Stats()

        damage_spell_50_res = compute_damage(10, stats, Characteristics.AGILITY, is_weapon=False, resistance=50, is_crit=False)
        damage_spell_150_res = compute_damage(10, stats, Characteristics.AGILITY, is_weapon=False, resistance=200, is_crit=False)
        damage_spell_minus_200_res = compute_damage(10, stats, Characteristics.AGILITY, is_weapon=False, resistance=-200, is_crit=False)

        self.assertEqual(damage_spell_50_res, 5)
        self.assertEqual(damage_spell_150_res, 0)
        self.assertEqual(damage_spell_minus_200_res, 30)

    def test_only_characteristic_multiplier(self):
        stats = Stats()

        stats.set_characteristic(Characteristics.AGILITY, 100)
        damage = compute_damage(10, stats, Characteristics.AGILITY, is_weapon=False) # 10 * (1 + 100 / 100)

        stats.set_damage(Damages.POWER, 50)
        damage2 = compute_damage(10, stats, Characteristics.AGILITY, is_weapon=False) # 10 * (1 + (100 + 50) / 100)

        damage3 = compute_damage(10, stats, Characteristics.INTELLIGENCE, is_weapon=False) # 10 * (1 + 50 / 100)

        self.assertEqual(damage, 20)
        self.assertEqual(damage2, 25)
        self.assertEqual(damage3, 15)

    def test_flat_damages(self):
        stats = Stats()

        stats.set_damage(Damages.BASIC, 12)
        damage = compute_damage(10, stats, Characteristics.STRENGTH, is_weapon=False) # 10 + 12

        stats.set_damage(Damages.EARTH, 7)
        damage2 = compute_damage(10, stats, Characteristics.STRENGTH, is_weapon=False) # 10 + 12 + 7

        damage3 = compute_damage(10, stats, Characteristics.INTELLIGENCE, is_weapon=False) # 10 + 12

        self.assertEqual(damage, 22)
        self.assertEqual(damage2, 29)
        self.assertEqual(damage3, 22)

    def test_characteristic_and_flat_damages(self):
        stats = Stats()

        stats.set_characteristic(Characteristics.LUCK, 200)
        stats.set_damage(Damages.BASIC, 23)

        damage = compute_damage(10, stats, Characteristics.LUCK, is_weapon=False) # 10 * (1 + 200 / 100) + 23

        self.assertEqual(damage, 53)

    def test_crit_damage(self):
        stats = Stats()

        stats.set_damage(Damages.CRIT, 30)

        damage_no_crit = compute_damage(10, stats, Characteristics.LUCK, is_weapon=False, is_crit=False) # 10
        damage_crit = compute_damage(10, stats, Characteristics.LUCK, is_weapon=False, is_crit=True) # 10 + 30

        self.assertEqual(damage_no_crit, 10)
        self.assertEqual(damage_crit, 40)

    def test_weapon_power(self):
        stats = Stats()

        stats.set_damage(Damages.WEAPON_POWER, 300)
        damage_spell = compute_damage(10, stats, Characteristics.STRENGTH, is_weapon=False) # 10
        damage_weapon = compute_damage(10, stats, Characteristics.STRENGTH, is_weapon=True) # 10 * (1 + 300 / 100)

        stats.set_characteristic(Characteristics.STRENGTH, 50)
        damage_spell_with_characteristic = compute_damage(10, stats, Characteristics.STRENGTH, is_weapon=False) # 10 * (1 + 50 / 100)
        damage_weapon_with_characteristic = compute_damage(10, stats, Characteristics.STRENGTH, is_weapon=True) # 10 * (1 + (50 + 300) / 100)

        self.assertEqual(damage_spell, 10)
        self.assertEqual(damage_weapon, 40)
        self.assertEqual(damage_spell_with_characteristic, 15)
        self.assertEqual(damage_weapon_with_characteristic, 45)

    def test_final_damages(self):
        stats = Stats()

        stats.set_damage(Damages.SPELL, 10)
        stats.set_damage(Damages.WEAPON, 30)
        damage_spell = compute_damage(10, stats, Characteristics.INTELLIGENCE, is_weapon=False) # 10 * (1 + 10 / 100)
        damage_weapon = compute_damage(10, stats, Characteristics.INTELLIGENCE, is_weapon=True) # 10 * (1 + 30 / 100)

        stats.set_damage(Damages.FINAL, 14)
        damage_spell_with_final = compute_damage(10, stats, Characteristics.INTELLIGENCE, is_weapon=False) # 10 * (1 + (10 + 14) / 100)
        damage_weapon_with_final = compute_damage(10, stats, Characteristics.INTELLIGENCE, is_weapon=True) # 10 * (1 + (30 + 14) / 100)

        self.assertEqual(damage_spell_with_final, 12)
        self.assertEqual(damage_weapon_with_final, 14)

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

        damage_spell_no_crit = compute_damage(20, stats, Characteristics.AGILITY, is_weapon=False, is_crit=False)
        damage_weapon_no_crit = compute_damage(20, stats, Characteristics.AGILITY, is_weapon=True, is_crit=False)
        damage_spell_crit = compute_damage(20, stats, Characteristics.AGILITY, is_weapon=False, is_crit=True)
        damage_weapon_crit = compute_damage(20, stats, Characteristics.AGILITY, is_weapon=True, is_crit=True)

        self.assertEqual(damage_spell_no_crit, 198)
        self.assertEqual(damage_weapon_no_crit, 255)
        self.assertEqual(damage_spell_crit, 213)
        self.assertEqual(damage_weapon_crit, 272)

    def get_real_stats(self):
        stats = Stats()

        stats.set_characteristic(Characteristics.AGILITY, 779)
        stats.set_characteristic(Characteristics.LUCK, 86)
        stats.set_characteristic(Characteristics.STRENGTH, 101)
        stats.set_characteristic(Characteristics.INTELLIGENCE, 81)

        stats.set_damage(Damages.POWER, 121)
        stats.set_damage(Damages.BASIC, 17)
        stats.set_damage(Damages.NEUTRAL, 29)
        stats.set_damage(Damages.EARTH, 31)
        stats.set_damage(Damages.FIRE, 7)
        stats.set_damage(Damages.WATER, 7)
        stats.set_damage(Damages.AIR, 49)
        stats.set_damage(Damages.SPELL, 7)

        return stats

    # Done with the real game
    def test_real_values_spell1(self):
        stats = self.get_real_stats()

        base_damages = [20, 22, 23, 25]
        is_crit = [False, False, True, True]

        damages = [compute_damage(base_damages[i], stats, Characteristics.AGILITY, is_weapon=False, is_crit=is_crit[i]) for i in range(4)]

        self.assertListEqual(damages, [284, 306, 316, 338])

    def test_real_values_spell2(self):
        stats = self.get_real_stats()

        base_damages = [32, 35, 36, 39]
        is_crit = [False, False, True, True]

        damages = [compute_damage(base_damages[i], stats, Characteristics.AGILITY, is_weapon=False, is_crit=is_crit[i]) for i in range(4)]

        self.assertListEqual(damages, [413, 445, 455, 487])

    def test_real_values_spell3(self):
        stats = self.get_real_stats()

        base_damages_air = [24, 28, 29, 33]
        base_damages_fire = [24, 28, 29, 33]
        is_crit = [False, False, True, True]

        damages = [
            compute_damage(base_damages_air[i], stats, Characteristics.AGILITY, is_weapon=False, is_crit=is_crit[i])
            + compute_damage(base_damages_fire[i], stats, Characteristics.INTELLIGENCE, is_weapon=False, is_crit=is_crit[i])
            for i in range(4)
        ]

        self.assertListEqual(damages, [429, 485, 498, 554])

    def test_real_value_weapon(self):
        stats = self.get_real_stats()

        base_damages = [7, 13, 12, 18]
        is_crit = [False, False, True, True]

        damages = [
            compute_damage(base_damages[i], stats, Characteristics.AGILITY, is_weapon=True, is_crit=is_crit[i])
            + compute_damage(base_damages[i], stats, Characteristics.INTELLIGENCE, is_weapon=True, is_crit=is_crit[i])
            + compute_damage(base_damages[i], stats, Characteristics.LUCK, is_weapon=True, is_crit=is_crit[i])
            + compute_damage(base_damages[i], stats, Characteristics.NEUTRAL, is_weapon=True, is_crit=is_crit[i])
            for i in range(4)
        ]

        self.assertListEqual(damages, [294, 409, 390, 506])

    def test_real_value_spell3(self):
        stats = self.get_real_stats()

        base_damages = [38, 47, 49, 49]
        is_crit = [False, False, True, True]

        stats.set_damage(Damages.SPELL, 0)
        damages_no_bonus_spell_damages = [compute_damage(base_damages[i], stats, Characteristics.AGILITY, is_weapon=False, is_crit=is_crit[i]) for i in range(4)]

        stats.set_damage(Damages.SPELL, 7)
        damages_bonus_spell_damages = [compute_damage(base_damages[i], stats, Characteristics.AGILITY, is_weapon=False, is_crit=is_crit[i]) for i in range(4)]

        self.assertListEqual(damages_no_bonus_spell_damages, [446, 536, 556, 556])
        self.assertListEqual(damages_bonus_spell_damages, [477, 573, 594, 594])


if __name__ == '__main__':
    unittest.main()
