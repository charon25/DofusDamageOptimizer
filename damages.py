from stats import Characteristics, Damages, Stats


def compute_damage(base_damage, stats: Stats, characteristic: Characteristics, is_melee, is_crit=False):
    power = stats.get_damage(Damages.POWER)
    if is_melee:
        power += stats.get_damage(Damages.WEAPON)

    caracteristic_multiplier = 1 + (stats.get_characteristic[characteristic] + power) / 100

    final_multiplier = 1.0 + stats.get_damage(Damages.FINAL) / 100
    if is_melee:
        final_multiplier += stats.get_damage(Damages.WEAPON) / 100
    else:
        final_multiplier += stats.get_damage(Damages.SPELL) / 100

    flat_damages = stats.get_damage(Damages.BASIC) + stats.get_damage(Damages(characteristic.value))
    if is_crit:
        flat_damages += stats.get_damage(Damages.CRIT)

    return (base_damage * caracteristic_multiplier + flat_damages ) * final_multiplier
