import json
import os
from typing import Any, Callable, Dict, List

from spell import Spell
from spell_set import SpellSet
from stats import Characteristics, Damages, Stats


class Manager:
    GENERAL_INSTRUCTIONS = ('s', 'def', 'h', 'q')
    STATS_INSTRUCTION = 'sp'
    SPELL_INSTRUCTION = 'st'
    SPELL_SET_INSTRUCTION = 'ss'
    DAMAGES_INSTRUCTION = 'dmg'

    DIRECTORIES = ('stats', 'spells')

    def __init__(self, print_method: Callable[[str, str], Any]) -> None:
        self.print = print_method
        self.stats: Dict[str, Stats] = {}
        self.spells: Dict[str, Spell] = {}
        self.spell_sets: Dict[str, SpellSet] = {}
        self.default_params = {}

        self.create_dirs()
        self.load_from_file()

    def create_dirs(self):
        for directory in Manager.DIRECTORIES:
            if not os.path.isdir(directory):
                os.mkdir(directory)

    def load_default(self):
        self.default_params = {
            'pa': 1,
            'pomin': 0,
            'pomax': 2048,
            't': 'mono'
        }

    def load_from_file(self):
        try:
            with open('manager.json', 'r', encoding='utf-8') as fi:
                json_data = json.load(fi)

            # STATS
            for stats_filepath in json_data['stats']:
                try:
                    stats = Stats.from_file(stats_filepath)
                    self.stats[stats.get_short_name()] = stats
                except Exception:
                    self.print('warning', f"Could not open or read stats page '{stats_filepath}'.")

            # SPELLS
            for spells_filepath in json_data['spells']:
                try:
                    spell = Spell.from_file(spells_filepath)
                    self.spells[spell.get_short_name()] = spell
                except Exception:
                    self.print('warning', f"Could not open or read spell '{spells_filepath}'.")

            # SPELL SETS
            for spell_set_data in json_data['spell_sets']:
                try:
                    spell_set = SpellSet()
                    try:
                        for spell_short_name in spell_set_data['spells']:
                            spell_set.add_spell(self.spells[spell_short_name])
                    except KeyError:
                        self.print('warning', f"Cannot add spell '{spell_short_name}' to spell set '{spell_set_data['short_name']}' : it does not exist.")

                    spell_set.set_name(spell_set_data['name'])
                    spell_set.set_short_name(spell_set_data['short_name'])
                    self.spell_sets[spell_set.get_short_name()] = spell_set
                except Exception:
                    self.print('warning', f"Could not load spell set '{spell_set_data['name']}'.")

            # DEFAULT PARAMS
            self.default_params = json_data['default_params']
        except Exception:
            self.print('error', "'manager.json' file does not exist or is innaccessible, using default load.")
            self.load_default()
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

    def set_default_param(self, args: List[str]):
        if len(args) < 2:
            self.print('error', f'Invalid syntax : missing argument{"s" if len(args) < 1 else ""}.')
            return

        param, value = args[:2]
        if not param in self.default_params:
            self.print('error', f"Unknown parameter : '{param}'.")
            return

        if param == 'pa':
            try:
                value = int(value)
            except:
                self.print('error', 'Default value for PA should be an int.')
                return
            if value <= 0:
                self.print('error', 'Default value for PA should be positive.')
                return
            self.default_params[param] = value

        elif param == 'pomin':
            try:
                value = int(value)
            except:
                self.print('error', 'Default value for minimum PO should be an int.')
                return
            if value < 0 or value > self.default_params['pomax']:
                self.print('error', 'Default value for minimum PO should be non-negative and smaller or equal to maximum PO.')
                return
            self.default_params[param] = value

        elif param == 'pomax':
            try:
                value = int(value)
            except:
                self.print('error', 'Default value for maximum PO should be an int.')
                return
            if value < 0 or value < self.default_params['pomin']:
                self.print('error', 'Default value for maximum PO should be non-negative and greater or equal to minimum PO.')
                return
            self.default_params[param] = value
        
        elif param == 't':
            if not value in ('mono', 'multi', 'versa'):
                self.print('error', "Type should be one of 'mono', 'multi', 'versa'.")
                return
            self.default_params[param] = value

    def print_help(self):
        pass

    def execute_general_command(self, instr, args: List[str]):
        if instr == 's':
            self.save()
        elif instr == 'def':
            self.set_default_param(args)
        elif instr == 'h':
            self.print_help()



    def execute_stats_command(self, args: List[str]):
        pass

    def execute_spell_command(self, args: List[str]):
        pass

    def execute_spell_set_command(self, args: List[str]):
        pass

    def execute_damages_command(self, args: List[str]):
        pass

    def execute_command(self, command: str):
        if command == '':
            raise ValueError('Command should be non empty.')

        instr, *args = command.split(' ')

        if instr in Manager.GENERAL_INSTRUCTIONS:
            self.execute_general_command(instr, args)

        elif instr == Manager.STATS_INSTRUCTION:
            self.execute_stats_command(args)

        elif instr == Manager.SPELL_INSTRUCTION:
            self.execute_spell_command(args)

        elif instr == Manager.SPELL_SET_INSTRUCTION:
            self.execute_spell_set_command(args)

        elif instr == Manager.DAMAGES_INSTRUCTION:
            self.execute_damages_command(args)

        self.print('warning', f"Unknown command instruction : '{instr}'.")