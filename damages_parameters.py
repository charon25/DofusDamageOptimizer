from dataclasses import dataclass, field, replace
import re
from typing import List, Literal, Tuple

from stats import Stats



@dataclass
class DamageParameters:
    stats: List[str] = field(default_factory=lambda: [])
    pa: int = 1
    po: List[int] = field(default_factory=lambda: [0, 2048])
    type: Literal['mono', 'multi', 'versa'] = 'mono'
    resistances: List[int] = field(default_factory=lambda: [0, 0, 0, 0, 0])
    distance: Literal['melee', 'range'] = 'range'
    vulnerability: int = 0


    def to_string(self):
        return f'-s {" ".join(self.stats)} -pa {self.pa} -pomin {self.po[0]} -pomax {self.po[1]} -t {self.type} -r {" ".join(map(str, self.resistances))} -d {self.distance} -v {self.vulnerability}'


    def _assert_correct_parameters(self):
        if self.pa < 1:
            raise ValueError(f"PA should be a positive integer ({self.pa} given instead).")
        if self.po[0] < 0:
            raise ValueError(f"Minimum PO should be non negative ({self.po[0]} given instead).")
        if self.po[0] > self.po[1]:
            raise ValueError(f"Minimum PO should be less than or equal to maximum PO ({self.po[0]} and {self.po[1]} given instead).")

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
                if re.match("[+-]?\d", argument) is None:
                    raise ValueError(f"Argument {k + 1} to command '{parameter[0]}' should be an integer ('{argument}' given instead.).")
            elif argument_type is None:
                if not argument in literals:
                    raise ValueError(f"Argument {k + 1} to command '{parameter[0]}' should be one of {literals} ('{argument}' given instead.).")

    @classmethod
    def from_string(cls, string: str, default_parameters: 'DamageParameters' = None):
        if default_parameters is None:
            default_parameters = DamageParameters()

        string = string.strip().lower()
        string = re.sub(r'-+', '-', string) # Replace repeating substring of - into only one

        if not string.startswith('-'):
            raise ValueError(f"Incorrect string to be parsed as parameters : does not start with a command ('{string}').")

        arguments = string.split(' ')
        parameters: List[List[str]] = list()

        for argument in arguments:
            if argument.startswith('-'):
                parameters.append([argument])
            else:
                parameters[-1].append(argument)

        damage_parameters = replace(default_parameters)

        for parameter in parameters:
            command = parameter[0]
            if command in ('-s', '-stats'):
                damage_parameters.stats = [argument for argument in parameter[1:]] # Copy the list to avoid reference issues

            elif command == '-pa':
                cls._check_parameter(parameter, 1, argument_type=int)
                damage_parameters.pa = int(parameter[1])

            elif command == '-po':
                cls._check_parameter(parameter, 1, argument_type=int)
                po = int(parameter[1])
                damage_parameters.po = [po, po]

            elif command in ('-pomin', '-minpo'):
                cls._check_parameter(parameter, 1, argument_type=int)
                damage_parameters.po[0] = int(parameter[1])

            elif command in ('-pomax', '-maxpo'):
                cls._check_parameter(parameter, 1, argument_type=int)
                damage_parameters.po[1] = int(parameter[1])

            elif command in ('-t', '-type'):
                cls._check_parameter(parameter, 1, literals=['mono', 'multi', 'versa'])
                damage_parameters.type = parameter[1]

            elif command in ('-r', '-res'):
                cls._check_parameter(parameter, 5, argument_type=int)
                damage_parameters.resistances = [int(parameter[i]) for i in range(1, 5 + 1)]
                pass

            elif command in ('-d', '-distance'):
                cls._check_parameter(parameter, 1, literals=['melee', 'range'])
                damage_parameters.distance = parameter[1]

            elif command in ('-v', '-vulne'):
                cls._check_parameter(parameter, 1, argument_type=int)
                damage_parameters.vulnerability = int(parameter[1])

        damage_parameters._assert_correct_parameters()

        return damage_parameters
