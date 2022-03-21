import json
import os
from typing import Any, Callable, List

from spell import Spell
from spell_set import SpellSet
from stats import Characteristics, Damages, Stats


class Manager:
    GENERAL_INSTRUCTIONS = ('s', 'def', 'h', 'q')
    STATS_INSTRUCTION = 'sp'
    SPELL_INSTRUCTION = 'st'
    SPELL_SET_INSTRUCTION = 'ss'
    DAMAGES_INSTRUCTION = 'dmg'

    def __init__(self, filename: str, print_method: Callable[[str, str], Any]) -> None:
        self.print = print_method
        self.stats = []
        self.spells = []
        self.spell_set = []
        self.default_params = {}

        self.load_from_file(filename)


    def load_from_file(self, filename):
        pass


    def save(self):
        pass

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