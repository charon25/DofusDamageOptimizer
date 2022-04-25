from dataclasses import dataclass, field, replace
import re
from typing import Dict, List, Literal

from stats import Stats, Characteristics

@dataclass
class DamageParameters:
    stats: List[str] = field(default_factory=lambda: [])
    pa: int = 1
    po: List[int] = field(default_factory=lambda: [0, 2048])
    type: Literal['mono', 'multi', 'versa'] = 'mono'
    resistances: List[int] = field(default_factory=lambda: [0, 0, 0, 0, 0])
    distance: Literal['melee', 'range'] = 'range'
    vulnerability: int = 0
    base_damages: int = 0


    def get_min_po(self):
        return self.po[0]

    def get_max_po(self):
        return self.po[1]

    def get_resistances_dict(self):
        # Reorder from STRENGTH/INTELLIGENCE/LUCK/AGILITY/NEUTRAL to NEUTRAL/STRENGTH/INTELLIGENCE/LUCK/AGILITY
        return {Characteristics(str(k - 1) if k > 0 else '4'): self.resistances[k] for k in range(5)}

    def get_total_stats(self, stats: Dict[str, Stats]):
        for stats_short_name in self.stats:
            if not stats_short_name in self.stats:
                raise KeyError(f"Stats page '{stats_short_name}' does not exist.")

        return sum(stats[stats_short_name] for stats_short_name in stats)


    def to_string(self):
        return f'-s {" ".join(self.stats)} -pa {self.pa} -pomin {self.get_min_po()} -pomax {self.get_max_po()} -t {self.type} -r {" ".join(map(str, self.resistances))} -d {self.distance} -v {self.vulnerability} -bdmg {self.base_damages}'


    def _assert_correct_parameters(self):
        if self.pa < 1:
            raise ValueError(f"PA should be a positive integer ({self.pa} given instead).")
        if self.get_min_po() < 0:
            raise ValueError(f"Minimum PO should be non negative ({self.get_min_po()} given instead).")
        if self.get_min_po() > self.get_max_po():
            raise ValueError(f"Minimum PO should be less than or equal to maximum PO ({self.get_min_po()} and {self.get_max_po()} given instead).")

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

        string = string.strip().lower()
        string = re.sub(r'-+', '-', string) # Replace repeating substring of - into only one

        if string == '':
            # No command, so just return the default parameters
            return replace(default_parameters)

        if not string.startswith('-'):
            raise ValueError(f"Incorrect string to be parsed as parameters : does not start with a command ('{string}').")

        arguments = string.split(' ')
        parameters: List[List[str]] = list()

        for argument in arguments:
            if re.match(r'^-[^\d]', argument) is not None: # Starts with a - but is not a negative number
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
                damage_parameters.po = [int(parameter[1]), damage_parameters.get_max_po()]

            elif command in ('-pomax', '-maxpo'):
                cls._check_parameter(parameter, 1, argument_type=int)
                damage_parameters.po = [damage_parameters.get_min_po(), int(parameter[1])]

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
                cls._check_parameter(parameter, 1, argument_type=int)
                damage_parameters.base_damages = int(parameter[1])

        damage_parameters._assert_correct_parameters()

        return damage_parameters

    @classmethod
    def from_other(cls, default_parameters: 'DamageParameters'):
        return replace(default_parameters)
