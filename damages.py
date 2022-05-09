from characteristics_damages import *
from damage_parameters import DamageParameters
from stats import Stats


def compute_damage(base_damages, stats: Stats, characteristic: int, parameters: DamageParameters, is_weapon, is_crit=False):
    base_damages = base_damages + parameters.get_base_damage(characteristic)

    if base_damages <= 0:
        return 0

    power = stats.get_damage(POWER)
    if is_weapon:
        power += stats.get_damage(WEAPON_POWER)

    characteristic_multiplier = 1 + (stats.get_characteristic(characteristic) + power) / 100

    # The damages associated with the characteristic is 3 more (STRENGTH is 0, EARTH is 3, ...)
    flat_damages = stats.get_damage(BASIC) + stats.get_damage(characteristic + 3)
    if is_crit:
        flat_damages += stats.get_damage(CRIT)

    final_multiplier = 1.0 + stats.get_damage(FINAL) / 100
    if is_weapon:
        final_multiplier += stats.get_damage(WEAPON) / 100
    else:
        final_multiplier += stats.get_damage(SPELL) / 100

    if parameters.distance == 'range':
        final_multiplier += stats.get_damage(RANGE) / 100
    elif parameters.distance == 'melee':
        final_multiplier += stats.get_damage(MELEE) / 100

    resistance_multiplier = max(0, 1.0 - parameters.get_resistance(characteristic) / 100) # Can't be negative damages

    vulnerability_multiplier = max(0, 1.0 + parameters.vulnerability / 100) # Can't be negative damages

    # Game rounds down the damage between each steps
    return int(int(int(int(base_damages * characteristic_multiplier + flat_damages) * final_multiplier) * vulnerability_multiplier) * resistance_multiplier)
