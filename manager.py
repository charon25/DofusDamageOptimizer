import json
import os
from typing import Any, Callable, Dict, List

from spell import Spell
from spell_set import SpellSet
from stats import Characteristics, Damages, Stats


class Manager:
    GENERAL_INSTRUCTIONS = ('s', 'def', 'h', 'q', 'i')
    STATS_INSTRUCTION = 'st'
    SPELL_INSTRUCTION = 'sp'
    SPELL_SET_INSTRUCTION = 'ss'
    DAMAGES_INSTRUCTION = 'dmg'

    DIRECTORIES = ('stats', 'spells')

    def __init__(self, print_method: Callable[[int, str], Any]) -> None:
        self.print = print_method
        self.stats: Dict[str, Stats] = {}
        self.spells: Dict[str, Spell] = {}
        self.spell_sets: Dict[str, SpellSet] = {}
        self.default_params = {}

        self._create_dirs()
        self._load_from_file()

    def _create_dirs(self):
        for directory in Manager.DIRECTORIES:
            if not os.path.isdir(directory):
                os.mkdir(directory)

    def _load_default(self):
        self.default_params = {
            'pa': 1,
            'pomin': 0,
            'pomax': 2048,
            't': 'mono'
        }

    def _load_from_file(self):
        try:
            with open('manager.json', 'r', encoding='utf-8') as fi:
                json_data = json.load(fi)

            # STATS
            for stats_filepath in json_data['stats']:
                try:
                    stats = Stats.from_file(stats_filepath)
                    self.stats[stats.get_short_name()] = stats
                except Exception:
                    self.print(1, f"Could not open or read stats page '{stats_filepath}'.")

            # SPELLS
            for spells_filepath in json_data['spells']:
                try:
                    spell = Spell.from_file(spells_filepath)
                    self.spells[spell.get_short_name()] = spell
                except Exception:
                    self.print(1, f"Could not open or read spell '{spells_filepath}'.")

            # SPELL SETS
            for spell_set_data in json_data['spell_sets']:
                try:
                    spell_set = SpellSet()
                    try:
                        for spell_short_name in spell_set_data['spells']:
                            spell_set.add_spell(self.spells[spell_short_name])
                    except KeyError:
                        self.print(1, f"Cannot add spell '{spell_short_name}' to spell set '{spell_set_data['short_name']}' : it does not exist.")

                    spell_set.set_name(spell_set_data['name'])
                    spell_set.set_short_name(spell_set_data['short_name'])
                    self.spell_sets[spell_set.get_short_name()] = spell_set
                except Exception:
                    self.print(1, f"Could not load spell set '{spell_set_data['name']}'.")

            # DEFAULT PARAMS
            self.default_params = json_data['default_params']
        except Exception:
            self.print(1, "'manager.json' file does not exist or is innaccessible, using default load.")
            self._load_default()
            return


    def save(self):
        stats_filepaths = []
        for stats in self.stats.values():
            filepath = f'stats\\{stats.get_safe_name()}.json'
            stats.save_to_file(filepath)
            stats_filepaths.append(filepath)

        spells_filepaths = []
        for spell in self.spells.values():
            filepath = f'spells\\{spell.get_safe_name()}.json'
            spell.save_to_file(filepath)
            spells_filepaths.append(filepath)

        spell_sets = []
        for spell_set in self.spell_sets.values():
            spell_sets.append({
                'spells': [spell.get_short_name() for spell in spell_set.spells],
                'name': spell_set.get_name(),
                'short_name': spell_set.get_short_name()
            })

        json_valid_data = {
            'stats': stats_filepaths,
            'spells': spells_filepaths,
            'spell_sets': spell_sets,
            'default_params': self.default_params
        }

        with open('manager.json', 'w', encoding='utf-8') as fo:
            json.dump(json_valid_data, fo)

        self.print(0, 'Data successfully saved!')

    def _set_default_param(self, args: List[str]):
        if len(args) < 2:
            self.print(1, f'Invalid syntax : missing argument{"s" if len(args) < 1 else ""}.')
            return

        param, value = args[:2]
        if not param in self.default_params:
            self.print(1, f"Unknown parameter : '{param}'.")
            return

        if param == 'pa':
            try:
                value = int(value)
            except:
                self.print(1, 'Default value for PA should be an int.')
                return
            if value <= 0:
                self.print(1, 'Default value for PA should be positive.')
                return
            self.default_params[param] = value
            self.print(0, f"Default PA count successfully set to '{value}'.")

        elif param == 'pomin':
            try:
                value = int(value)
            except:
                self.print(1, 'Default value for minimum PO should be an int.')
                return
            if value < 0 or value > self.default_params['pomax']:
                self.print(1, 'Default value for minimum PO should be non-negative and smaller or equal to maximum PO.')
                return
            self.default_params[param] = value
            self.print(0, f"Default minimum PO successfully set to '{value}'.")

        elif param == 'pomax':
            try:
                value = int(value)
            except:
                self.print(1, 'Default value for maximum PO should be an int.')
                return
            if value < 0 or value < self.default_params['pomin']:
                self.print(1, 'Default value for maximum PO should be non-negative and greater or equal to minimum PO.')
                return
            self.default_params[param] = value
            self.print(0, f"Default maximum PO successfully set to '{value}'.")
        
        elif param == 't':
            if not value in ('mono', 'multi', 'versa'):
                self.print(1, "Type should be one of 'mono', 'multi', 'versa'.")
                return
            self.default_params[param] = value
            self.print(0, f"Default type successfully set to '{value}'.")

    def _print_help(self):
        pass

    def _print_infos(self):
        pass

    def _execute_general_command(self, instr, args: List[str]):
        if instr == 's':
            self.save()
        elif instr == 'def':
            self._set_default_param(args)
        elif instr == 'h':
            self._print_help()
        elif instr == 'i':
            self._print_infos()


    def _create_stats(self, stats: Stats = Stats()) -> Stats:
        name = input(f'Stats page name {f"({stats.get_name()})" if stats.get_name() != "" else ""} : ')
        if name:
            stats.set_name(name)

        self.print(0, '\n=== Characteristics\n')
        for characteristic in Characteristics:
            if characteristic == Characteristics.NEUTRAL:
                continue

            characteristic_value = input(f'{characteristic.name} ({stats.get_characteristic(characteristic)}) : ')
            if characteristic_value:
                stats.set_characteristic(characteristic, int(characteristic_value))

        self.print(0, '\n=== Damages\n')
        for damage in Damages:
            damage_value = input(f'{damage.name} ({stats.get_damage(damage)}) : ')
            if damage_value:
                stats.set_damage(damage, int(damage_value))

        self.print(0, '')
        bonus_crit_chance = input(f'Bonus crit chance % ({100 * stats.get_bonus_crit_chance():.1f} %) : ')
        if bonus_crit_chance:
            stats.set_bonus_crit_chance(float(bonus_crit_chance) / 100.0)

        return stats

    def _execute_stats_command(self, args: List[str]):
        if len(args) == 0:
            self.print(1, 'Action missing in the command.')
            return

        command_action = args[0]
        if command_action == 'new':
            if len(args) < 2:
                self.print(1, 'Missing short name to create stats page.')
                return

            short_name = args[1]

            stats = self._create_stats()
            stats.set_short_name(short_name)

            self.stats[short_name] = stats
            self.print(0, f"Page '{short_name}' successfully created!")
        elif command_action == 'list':
            for stats in sorted(self.stats.values(), key=lambda stat: stat.get_name()):
                self.print(0)
        elif command_action == 'show':
            pass
        elif command_action == 'mod':
            if len(args) < 2:
                self.print(1, 'Missing stats page short name.')
                return

            short_name = args[1]

            if short_name in self.stats:
                self.stats[short_name] = self._create_stats(self.stats[short_name])
                self.print(0, f"Page '{short_name}' successfully modified!")
            else:
                self.print(1, f"Stats page '{short_name}' does not exist.")
        elif command_action == 'rm':
            if len(args) < 2:
                self.print(1, 'Missing stats page short name.')
                return
                
            short_name = args[1]
            if short_name in self.stats:
                self.stats.pop(short_name)
                self.print(0, f"Page '{short_name}' successfully deleted!")
            else:
                self.print(1, f"Stats page '{short_name}' does not exist.")
        else:
            self.print(1, f"Unknown action '{command_action}' for stats commands.")

    def _execute_spell_command(self, args: List[str]):
        pass

    def _execute_spell_set_command(self, args: List[str]):
        pass

    def _execute_damages_command(self, args: List[str]):
        pass

    def execute_command(self, command: str):
        if command == '':
            raise ValueError('Command should be non empty.')

        instr, *args = command.split(' ')

        if instr in Manager.GENERAL_INSTRUCTIONS:
            self._execute_general_command(instr, args)
            return

        elif instr == Manager.STATS_INSTRUCTION:
            self._execute_stats_command(args)
            return

        elif instr == Manager.SPELL_INSTRUCTION:
            self._execute_spell_command(args)
            return

        elif instr == Manager.SPELL_SET_INSTRUCTION:
            self._execute_spell_set_command(args)
            return

        elif instr == Manager.DAMAGES_INSTRUCTION:
            self._execute_damages_command(args)
            return

        self.print(1, f"Unknown command instruction : '{instr}'.")
