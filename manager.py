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

    def __init__(self, filename: str, print_method: Callable[[str], Any]) -> None:
        self.print = print_method
        self.stats = []
        self.spells = []
        self.spell_set = []

        self.load_from_file(filename)


    def load_from_file(self, filename):
        pass


    def execute_general_command(self, instr, args: List[str]):
        pass

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

        if instr == Manager.STATS_INSTRUCTION:
            self.execute_stats_command(args)

        if instr == Manager.SPELL_INSTRUCTION:
            self.execute_spell_command(args)

        if instr == Manager.SPELL_SET_INSTRUCTION:
            self.execute_spell_set_command(args)

        if instr == Manager.DAMAGES_INSTRUCTION:
            self.execute_damages_command(args)

        self.print(f"Unknown command instruction : '{instr}'.")