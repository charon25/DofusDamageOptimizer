from typing import Callable, Tuple
from characteristics_damages import *
from damage_parameters import DamageParameters
from stats import Stats


def compute_one_damage(base_damages, stats: Stats, characteristic: int, parameters: DamageParameters, is_weapon, is_crit=False):
    base_damages = base_damages + parameters.base_damages[characteristic + 1 if characteristic != 4 else 0]

    if base_damages <= 0:
        return 0

    power = stats.damages[POWER]
    if is_weapon:
        power += stats.damages[WEAPON_POWER]

    characteristic_multiplier = 1 + (stats.characteristics[characteristic] + power) / 100

    # The damages associated with the characteristic is 3 more (STRENGTH is 0, EARTH is 3, ...)
    flat_damages = stats.damages[BASIC] + stats.damages[characteristic + 3]
    if is_crit:
        flat_damages += stats.damages[CRIT]

    final_multiplier = 1.0 + stats.damages[FINAL] / 100
    if is_weapon:
        final_multiplier += stats.damages[WEAPON] / 100
    else:
        final_multiplier += stats.damages[SPELL] / 100

    if parameters.distance == 'range':
        final_multiplier += stats.damages[RANGE] / 100
    elif parameters.distance == 'melee':
        final_multiplier += stats.damages[MELEE] / 100

    resistance_multiplier = max(0, 1.0 - parameters.resistances[characteristic + 1 if characteristic != 4 else 0] / 100) # Can't be negative damages

    vulnerability_multiplier = max(0, 1.0 + parameters.vulnerability / 100) # Can't be negative damages

    # Game rounds down the damage between each steps
    return int(int(int(int(base_damages * characteristic_multiplier + flat_damages) * final_multiplier) * vulnerability_multiplier) * resistance_multiplier)


def compute_damages(base_damages, stats: Stats, characteristic: int, parameters: DamageParameters, is_weapon):
    additional_base_damages = parameters.base_damages[characteristic + 1 if characteristic != 4 else 0]

    power = stats.damages[POWER]
    if is_weapon:
        power += stats.damages[WEAPON_POWER]

    characteristic_multiplier = 1 + (stats.characteristics[characteristic] + power) / 100

    # The damages associated with the characteristic is 3 more (STRENGTH is 0, EARTH is 3, ...)
    flat_damages = stats.damages[BASIC] + stats.damages[characteristic + 3]

    final_multiplier = 1.0 + stats.damages[FINAL] / 100
    if is_weapon:
        final_multiplier += stats.damages[WEAPON] / 100
    else:
        final_multiplier += stats.damages[SPELL] / 100

    if parameters.distance == 'range':
        final_multiplier += stats.damages[RANGE] / 100
    elif parameters.distance == 'melee':
        final_multiplier += stats.damages[MELEE] / 100

    resistance_multiplier = max(0, 1.0 - parameters.resistances[characteristic + 1 if characteristic != 4 else 0] / 100) # Can't be negative damages

    vulnerability_multiplier = max(0, 1.0 + parameters.vulnerability / 100) # Can't be negative damages

    # Game rounds down the damage between each steps
    return (
        int(int(int(int((base_damages['min'] + additional_base_damages) * characteristic_multiplier + flat_damages) * final_multiplier) * vulnerability_multiplier) * resistance_multiplier) if (base_damages['min'] + additional_base_damages) > 0 else 0,
        int(int(int(int((base_damages['max'] + additional_base_damages) * characteristic_multiplier + flat_damages) * final_multiplier) * vulnerability_multiplier) * resistance_multiplier) if (base_damages['max'] + additional_base_damages) > 0 else 0,
        int(int(int(int((base_damages['crit_min'] + additional_base_damages) * characteristic_multiplier + flat_damages + stats.damages[CRIT]) * final_multiplier) * vulnerability_multiplier) * resistance_multiplier) if (base_damages['crit_min'] + additional_base_damages) > 0 else 0,
        int(int(int(int((base_damages['crit_max'] + additional_base_damages) * characteristic_multiplier + flat_damages + stats.damages[CRIT]) * final_multiplier) * vulnerability_multiplier) * resistance_multiplier) if (base_damages['crit_max'] + additional_base_damages) > 0 else 0,
    )
