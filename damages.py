from stats import Characteristics, Damages, Stats


def compute_damage(base_damage, stats: Stats, characteristic: Characteristics, is_melee, resistance: int = 0, is_crit=False):
    if base_damage == 0:
        return 0

    power = stats.get_damage(Damages.POWER)
    if is_melee:
        power += stats.get_damage(Damages.WEAPON_POWER)

    characteristic_multiplier = 1 + (stats.get_characteristic(characteristic) + power) / 100

    flat_damages = stats.get_damage(Damages.BASIC) + stats.get_damage(Damages(characteristic.value))
    if is_crit:
        flat_damages += stats.get_damage(Damages.CRIT)

    final_multiplier = 1.0 + stats.get_damage(Damages.FINAL) / 100
    if is_melee:
        final_multiplier += stats.get_damage(Damages.WEAPON) / 100
    else:
        final_multiplier += stats.get_damage(Damages.SPELL) / 100

    resistance_multiplier = max(0, 1 - resistance / 100) # Can't be negative damages

    # Game rounds down the damage
    # TODO check if rounding is done between final multiplier and resistance multiplier
    return int(int(int(base_damage * characteristic_multiplier + flat_damages) * final_multiplier) * resistance_multiplier)
