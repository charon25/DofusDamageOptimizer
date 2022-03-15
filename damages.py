from stats import Characteristics, Damages, Stats


def compute_damage(base_damages, stats: Stats, characteristic: Characteristics, is_melee, is_crit=False):
    if is_crit:
        base = (base_damages['crit_min'] + base_damages['crit_max']) / 2
    else:
        base = (base_damages['min'] + base_damages['max']) / 2

    power = stats.get_damage(Damages.POWER)
    if is_melee:
        power += stats.get_damage(Damages.WEAPON)

    caracteristic_multiplier = 1 + (stats.get_characteristic[characteristic] + power) / 100

    spell_multiplier = 1.0
    if not is_melee:
        spell_multiplier += stats.get_damage(Damages.SPELLS) / 100

    flat_damages = stats.get_damage(Damages.BASIC) + stats.get_damage(Damages(characteristic.value))
    if is_crit:
        flat_damages += stats.get_damage(Damages.CRIT)

    return base * caracteristic_multiplier * spell_multiplier + flat_damages
