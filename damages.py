from damages_parameters import DamageParameters
from stats import Characteristics, Damages, Stats


def compute_damage(base_damages, stats: Stats, characteristic: Characteristics, parameters: DamageParameters, is_weapon, is_crit=False):
    # If base_damages is already 0, it means the spell does not use this characteristics, so the damages are 0
    # Same thing if the parameters base_damages are very negative and cancel the base damages
    parameters_base_damages = parameters.get_base_damages_dict()[characteristic]
    if base_damages <= 0 or base_damages + parameters_base_damages <= 0:
        return 0

    base_damages = base_damages + parameters_base_damages

    power = stats.get_damage(Damages.POWER)
    if is_weapon:
        power += stats.get_damage(Damages.WEAPON_POWER)

    characteristic_multiplier = 1 + (stats.get_characteristic(characteristic) + power) / 100

    flat_damages = stats.get_damage(Damages.BASIC) + stats.get_damage(Damages(characteristic.value))
    if is_crit:
        flat_damages += stats.get_damage(Damages.CRIT)

    final_multiplier = 1.0 + stats.get_damage(Damages.FINAL) / 100
    if is_weapon:
        final_multiplier += stats.get_damage(Damages.WEAPON) / 100
    else:
        final_multiplier += stats.get_damage(Damages.SPELL) / 100

    if parameters.distance == 'range':
        final_multiplier += stats.get_damage(Damages.RANGE) / 100
    elif parameters.distance == 'melee':
        final_multiplier += stats.get_damage(Damages.MELEE) / 100

    resistance_multiplier = max(0, 1.0 - parameters.get_resistances_dict()[characteristic] / 100) # Can't be negative damages

    vulnerability_multiplier = max(0, 1.0 + parameters.vulnerability / 100) # Can't be negative damages

    # Game rounds down the damage between each steps
    return int(int(int(int(base_damages * characteristic_multiplier + flat_damages) * final_multiplier) * vulnerability_multiplier) * resistance_multiplier)
