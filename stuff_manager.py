import distutils.util
import json
import math
from msilib.schema import File
import os
import re
import sys
from typing import Any, Callable, Dict, List, Tuple

from characteristics_damages import *
from item import Item
from items_manager import ItemsManager
from knapsack import get_best_combination
from damage_parameters import DamageParameters
from manager import Manager
from spell import Spell, SpellBuff
from spell_chain import SpellChains
from spell_set import SpellSet
from stats import Stats


class StuffManager:
    OPTIMIZE_STUFF_COMMAND = ('optstuff', )

    def __init__(self, print_method: Callable[[int, str], Any], manager: Manager) -> None:
        self.print: Callable[[int, str], Any] = print_method
        self.items_manager: ItemsManager = None
        self.manager: Manager = manager

        self._load_from_file()

    def _load_from_file(self):
        self.items_manager = ItemsManager('stuff_data\\all_items.json')


    def _execute_optimize_stuff_command(self, args: List[str]):
        if len(args) < 1:
            self.print(1, 'Missing spells.')
            return

        spell_list: List[Spell] = list()

        for index, spell_short_name in enumerate(args):
            if spell_short_name.startswith('-'):
                index -= 1  # Compensate for the case where the break does not occur
                break

            if not spell_short_name in self.manager.spells:
                self.print(1, f"Spell '{spell_short_name}' does not exist.")
                return

            spell_list.append(self.manager.spells[spell_short_name])

        command = ' '.join(args[index + 1:])
        try:
            damages_parameters = DamageParameters.from_string(command, self.manager._get_default_parameters())
        except ValueError as e:
            self.print(1, f'Cannot parse parameters: {str(e)}')
            return

        total_stats = damages_parameters.get_total_stats(self.manager.stats)

        spell_chain = SpellChains()
        for spell in spell_list:
            spell_chain.add_spell(spell)

        damages = self.items_manager.get_best_stuff_from_spells(spell_chain, total_stats, damages_parameters)

        self.print(0, f"Best stuff (parameters : '{self.manager.default_parameters}' ; initial states: ({','.join(sorted(damages_parameters.starting_states))})) :")
        self.print(0, '')
        for item in damages[0]:
            self.print(0, f" - {item.type.capitalize(): <7} : {item.name}")
        self.print(0, '')
        self.print(0, f" => {damages[1][0]:.0f} : {damages[1][1]['min']:.0f} - {damages[1][1]['max']:.0f} ({damages[1][1]['crit_min']:.0f} - {damages[1][1]['crit_max']:.0f})")



    def execute_command(self, command: str):
        instr, *args = command.split(' ')

        if instr in StuffManager.OPTIMIZE_STUFF_COMMAND:
            self._execute_optimize_stuff_command(args)
