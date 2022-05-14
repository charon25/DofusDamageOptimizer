import re
from typing import Dict, List, Literal, Set, Tuple, Union

from characteristics_damages import *
from stats import Stats


class DamageParameters:

    def __init__(self) -> None:
        self.full_name: str = ''
        self.stats: List[str] = []
        self.pa: int = 1
        self.po: Tuple[int, int] = (0, 2048)
        self.type: Literal['mono', 'multi', 'versa'] = 'mono'
        self.resistances: List[int] = [0, 0, 0, 0, 0]
        self.distance: Literal['melee', 'range'] = 'range'
        self.vulnerability: int = 0
        self.base_damages: List[int] = [0, 0, 0, 0, 0]
        self.starting_states: Set[str] = set()
        # 'unspecified' indicates we do not care about the position
        self.position: Literal['unspecified', 'none', 'line', 'diag'] = 'unspecified'


    def get_min_po(self):
        return self.po[0]

    def get_max_po(self):
        return self.po[1]

    # Both functions are reordered from EARTH/FIRE/WATER/AIR/NEUTRAL to NEUTRAL/EARTH/FIRE/WATER/AIR
    def get_resistance(self, characteristic: int):
        return self.resistances[characteristic + 1 if characteristic != 4 else 0]

    def get_base_damage(self, characteristic: int):
        return self.base_damages[characteristic + 1 if characteristic != 4 else 0]

    def get_total_stats(self, stats: Dict[str, Stats]) -> Stats:
        for stats_short_name in self.stats:
            if not stats_short_name in stats:
                raise KeyError(f"Stats page '{stats_short_name}' does not exist.")

        if len(self.stats) == 0:
            return Stats()

        return sum(stats[stats_short_name] for stats_short_name in self.stats)

    def add_base_damages(self, base_damages: List[int]):
        for characteristic in range(CHARACTERISTICS_COUNT):
            self.base_damages[characteristic + 1 if characteristic != 4 else 0] += base_damages[characteristic]


    def __add__(self, other: Union['DamageParameters', int]):
        """Perform an addition of the 'addable' type : vulnerability and base damages."""

        if isinstance(other, int):  # Useful when doing stats + sum([]) - No matter the integer, return the stats
            return DamageParameters.from_existing(self)
        elif not isinstance(other, DamageParameters):
            raise TypeError(f"unsupported operand type(s) for +: 'DamageParameters' and '{type(other)}'.")

        result = DamageParameters.from_existing(self)

        result.vulnerability += other.vulnerability
        for k in range(5):
            result.base_damages[k] += other.base_damages[k]
            result.resistances[k] += other.resistances[k]

        return result


    def to_string(self):
        return f'-s {" ".join(self.stats)} -pa {self.pa} -pomin {self.get_min_po()} -pomax {self.get_max_po()} -t {self.type} -r {" ".join(map(str, self.resistances))} -d {self.distance} -v {self.vulnerability} -name {self.full_name} -bdmg {" ".join(map(str, self.base_damages))} -p {self.position}'

    def to_compact_string(self):
        return f'-r {" ".join(map(str, self.resistances))} -v {self.vulnerability} -bdmg {" ".join(map(str, self.base_damages))}'


    def _assert_correct_parameters(self):
        if self.pa < 1:
            raise ValueError(f"PA should be a positive integer ({self.pa} given instead).")
        if self.get_min_po() < 0:
            raise ValueError(f"Minimum PO should be non negative ({self.get_min_po()} given instead).")
        if self.get_min_po() > self.get_max_po():
            raise ValueError(f"Minimum PO should be less than or equal to maximum PO ({self.get_min_po()} and {self.get_max_po()} given instead).")


    def copy(self):
        return DamageParameters.from_existing(self)


    @classmethod
    def _check_parameter(cls, parameter: List[str], count: int = -1, argument_type=None, literals: List[str]=None):
        if count > 0: # If count if < 0, it means no constraints
            if len(parameter) - 1 < count:
                raise ValueError(f"Too few arguments provided to command '{parameter[0]}' ({len(parameter) - 1} given, {count} expected).")
            elif len(parameter) - 1 > count:
                raise ValueError(f"Too many arguments provided to command '{parameter[0]}' ({len(parameter) - 1} given, {count} expected).")

        if argument_type is None and literals is None: # No constraints on what the arguments can be
            return

        for k, argument in enumerate(parameter[1:]):
            if argument_type == int:
                if re.match("^[+-]?\d+$", argument) is None: # Check argument is an integer, maybe preceded by - or +
                    raise ValueError(f"Argument {k + 1} to command '{parameter[0]}' should be an integer ('{argument}' given instead).")
            elif argument_type is None:
                if not argument in literals:
                    raise ValueError(f"Argument {k + 1} to command '{parameter[0]}' should be one of {literals} ('{argument}' given instead).")

    @classmethod
    def from_string(cls, string: str, default_parameters: 'DamageParameters' = None):
        if default_parameters is None:
            default_parameters = DamageParameters()

        string = string.strip()
        string = re.sub(r'-+', '-', string) # Replace repeating substring of - into only one

        if string == '':
            # No command, so just return the default parameters
            return default_parameters.copy()

        if not string.startswith('-'):
            raise ValueError(f"Incorrect string to be parsed as parameters : does not start with a command ('{string}').")

        arguments = string.split(' ')
        parameters: List[List[str]] = list()

        for argument in arguments:
            if re.match(r'^-[^\d]', argument.lower()) is not None: # Starts with a - but is not a negative number
                parameters.append([argument.lower()])
            else:
                parameters[-1].append(argument)

        damage_parameters = default_parameters.copy()

        for parameter in parameters:
            command = parameter[0]
            if command in ('-s', '-stats'):
                damage_parameters.stats = damage_parameters.stats + [argument for argument in parameter[1:] if argument != ''] # Copy the list to avoid reference issues

            elif command == '-pa':
                cls._check_parameter(parameter, 1, argument_type=int)
                damage_parameters.pa = int(parameter[1])

            elif command == '-po':
                cls._check_parameter(parameter, 1, argument_type=int)
                po = int(parameter[1])
                damage_parameters.po = (po, po)

            elif command in ('-pomin', '-minpo'):
                cls._check_parameter(parameter, 1, argument_type=int)
                damage_parameters.po = (int(parameter[1]), damage_parameters.get_max_po())

            elif command in ('-pomax', '-maxpo'):
                cls._check_parameter(parameter, 1, argument_type=int)
                damage_parameters.po = (damage_parameters.get_min_po(), int(parameter[1]))

            elif command in ('-t', '-type'):
                cls._check_parameter(parameter, 1, literals=['mono', 'multi', 'versa'])
                damage_parameters.type = parameter[1]

            elif command in ('-r', '-res', '-resistances'):
                cls._check_parameter(parameter, 5, argument_type=int)
                damage_parameters.resistances = [int(parameter[i]) for i in range(1, 5 + 1)]
                pass

            elif command in ('-d', '-distance'):
                cls._check_parameter(parameter, 1, literals=['melee', 'range'])
                damage_parameters.distance = parameter[1]

            elif command in ('-v', '-vulne', '-vulnerability'):
                cls._check_parameter(parameter, 1, argument_type=int)
                damage_parameters.vulnerability = int(parameter[1])

            elif command in ('-bdmg', '-bdamages', '-base-damages'):
                cls._check_parameter(parameter, 5, argument_type=int)
                damage_parameters.base_damages = [int(parameter[i]) for i in range(1, 5 + 1)]

            elif command in ('-state', '-states'):
                damage_parameters.starting_states = {argument for argument in parameter[1:] if argument != ''}

            elif command in ('-name',):
                damage_parameters.full_name = ' '.join(parameter[1:])

            elif command in ('-p', '-position'):
                if len(parameter) == 2:  # This means only the string position was supplied
                    cls._check_parameter(parameter, 1, literals=['unspecified', 'none', 'line', 'diag'])
                    damage_parameters.position = parameter[1]
                else:  # This means two coordinates were supplied
                    cls._check_parameter(parameter, 2, argument_type=int)
                    x, y = map(lambda x:abs(int(x)), parameter[1:3])  # Convert both coordinates to integers and take the absolute value
                    damage_parameters.position = 'none'  # Default position if the coordinates are specified
                    if abs(x) == abs(y):
                        damage_parameters.position = 'diag'
                    elif x == 0 or y == 0:
                        damage_parameters.position = 'line'
                    damage_parameters.po = [abs(x) + abs(y), abs(x) + abs(y)]

        # If the specified PO is one, this means the enemy is in melee range
        # If the minimum PO is > 1, the enemy is not in melee range
        if max(damage_parameters.po) <= 1:
            damage_parameters.distance = 'melee'
        elif min(damage_parameters.po) > 1:
            damage_parameters.distance = 'range'

        damage_parameters._assert_correct_parameters()

        return damage_parameters

    @classmethod
    def from_existing(cls, default_parameters: 'DamageParameters'):
        # Using [::] is faster than a list comprehension
        parameters = DamageParameters()

        parameters.full_name = default_parameters.full_name
        parameters.stats = default_parameters.stats[::]
        parameters.pa = default_parameters.pa
        parameters.po = default_parameters.po[::]
        parameters.type = default_parameters.type
        parameters.resistances = default_parameters.resistances[::]
        parameters.distance = default_parameters.distance
        parameters.vulnerability = default_parameters.vulnerability
        parameters.base_damages = default_parameters.base_damages[::]

        return parameters
