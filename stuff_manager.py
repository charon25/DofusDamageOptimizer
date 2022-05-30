import distutils.util
import json
import math
from msilib.schema import File
import os
import re
import sys
from typing import Any, Callable, Dict, List, Tuple

from characteristics_damages import *
from item import Equipment, Item
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
    OPTIMIZE_STATS_COMMAND = ('optstats', )
    EQUIPMENT_COMMAND = ('equip', 'equipment')
    SEARCH_COMMAND = ('search', )
    ITEM_command = ('item', )


    def __init__(self, print_method: Callable[[int, str], Any], manager: Manager) -> None:
        self.print: Callable[[int, str], Any] = print_method
        self.items_manager: ItemsManager = None
        self.manager: Manager = manager

        self._load_from_files()

    def _load_from_files(self):
        self.items_manager = ItemsManager({'items': 'stuff_data\\all_items.json', 'item_sets': 'stuff_data\\all_item_sets.json', 'item_sets_combinations': 'stuff_data\\item_sets_combinations.json'})


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
        if damages_parameters.equipment:
            damages_parameters.update_stuff_with_equipment(self.manager.equipments)
            # total_stats += damages_parameters.get_equipment_stats(self.items_manager.items, self.manager.equipments)

        spell_chain = SpellChains()
        for spell in spell_list:
            spell_chain.add_spell(spell)

        damages = self.items_manager.get_best_stuff_from_spells(spell_chain, total_stats, damages_parameters, self.manager.equipments)

        self.print(0, f"Best stuff (parameters : '{self.manager.default_parameters}' ; initial states: ({','.join(sorted(damages_parameters.starting_states))}) ; equipment: '{damages_parameters.equipment}') :")
        self.print(0, '')
        for item in damages[0]:
            self.print(0, f" - {item.type.capitalize(): <7} : {item.name} ({item.id})")
        self.print(0, '')
        self.print(0, f" => {damages[1][0]:.0f} : {damages[1][1]['min']:.0f} - {damages[1][1]['max']:.0f} ({damages[1][1]['crit_min']:.0f} - {damages[1][1]['crit_max']:.0f})")


    def _execute_equipment_command(self, args: List[str]):
        if len(args) == 0:
            self.print(1, 'Missing action in the command.')
            return

        command_action = args[0]

        if command_action == 'new':
            if len(args) < 2:
                self.print(1, 'Missing equipment name.')
                return

            equip_name = args[1]

            if equip_name in self.manager.equipments:
                self.print(1, 'Equipment already exist.')
                return

            equipment = Equipment()
            equipment.name = equip_name
            self.manager.equipments[equip_name] = equipment

            self.manager.save(False)
            self.print(0, f"Equipment '{equip_name}' successfully created.")

        elif command_action == 'rm':
            if len(args) < 2:
                self.print(1, 'Missing equipment name.')
                return

            equip_name = args[1]

            if not equip_name in self.manager.equipments:
                self.print(1, 'Equipment does not exist.')
                return

            self.manager.equipments.pop(equip_name)

        elif command_action == 'ls':
            self.print(0, '=== Equipments\n')
            for equipment in sorted(self.manager.equipments.values(), key=lambda equipment: equipment.name):
                self.print(0, f" - '{equipment.name}': {len(equipment)} item{'s' if len(equipment) > 1 else ''}")

        elif command_action == 'show':
            if len(args) < 2:
                self.print(1, 'Missing equipment name.')
                return

            equip_name = args[1]

            if not equip_name in self.manager.equipments:
                self.print(1, 'Equipment does not exist.')
                return

            equipment = self.manager.equipments[equip_name]
            printed_string = [f"===== Equipment '{equip_name}'", '']

            for item_type in Item.TYPES:
                if item_type in equipment:
                    printed_string.append(f" - {item_type.capitalize(): <7} : {self.items_manager.items[equipment.items[item_type]].name}")

            self.print(0, '\n'.join(printed_string))

        elif command_action == 'add':
            if len(args) < 3:
                self.print(1, 'Missing equipment name or items to add.')
                return

            equip_name = args[1]

            if not equip_name in self.manager.equipments:
                self.print(1, 'Equipment does not exist.')
                return

            equipment = self.manager.equipments[equip_name]
            added_count = 0
            for item_id in args[2:]:
                if item_id.isnumeric() and int(item_id) in self.items_manager.items:
                    item_id = int(item_id)
                    equipment.add_item(self.items_manager.items[item_id].type, item_id)
                    added_count += 1
                else:
                    self.print(0, f"[WARNING] Item '{item_id}' is invalid or does not exist.")

            self.manager.save(False)
            self.print(0, f"{added_count} item{'s' if added_count > 1 else ''} added to '{equip_name}' successfully.")

        elif command_action == 'del':
            if len(args) < 3:
                self.print(1, 'Missing equipment name or items to add.')
                return

            equip_name = args[1]

            if not equip_name in self.manager.equipments:
                self.print(1, 'Equipment does not exist.')
                return

            equipment = self.manager.equipments[equip_name]
            removed_count = 0
            for item_id in args[2:]:
                could_be_removed = False
                if item_id.isnumeric():
                    could_be_removed = equipment.remove_item(int(item_id))
                    removed_count += int(could_be_removed)
                
                if not item_id.isnumeric() or not could_be_removed:
                    self.print(0, f"[WARNING] Item '{item_id}' is invalid or does not belong to equipment '{equip_name}'.")
                

            self.print(0, f"{removed_count} item{'s' if removed_count > 1 else ''} removed from '{equip_name}' successfully.")

        elif command_action == 'copy':
            if len(args) < 3:
                self.print(1, 'Missing current or new equipment.')
                return

            current_equip_name = args[1]

            if not current_equip_name in self.manager.equipments:
                self.print(1, f"Equipment '{current_equip_name}' does not exist.")
                return

            new_equip_name = args[2]

            if new_equip_name in self.manager.equipments:
                self.print(1, f"Equipment '{new_equip_name}' already exist.")

            self.manager.equipments[new_equip_name] = self.manager.equipments[current_equip_name].copy(new_equip_name)

            self.manager.save(False)
            self.print(0, f"Equipment '{new_equip_name}' succesfully created from '{current_equip_name}'.")


    def _execute_search_command(self, args: List[str]):
        if len(args) < 1:
            self.print(1, 'Missing item name.')
            return

        search_phrase = ' '.join(args)
        search_result = self.items_manager.search(search_phrase)

        self.print(0, '=== Search results\n')
        for item in search_result[:25]:
            self.print(0, f" - {item.name} ({item.type}): {item.id}")


    def _execute_item_command(self, args: List[str]):
        if len(args) < 1:
            self.print(1, 'Missing item id.')
            return

        if not args[0].isnumeric() or not int(args[0]) in self.items_manager.items:
            self.print(1, f"'{args[0]}' is not a valid item.")

        item = self.items_manager.items[int(args[0])]

        mode = 'max'
        if len(args) >= 2 and args[1] in ('min', 'max', 'ave'):
            mode = args[1]

        self.print(0, f"=== Item '{item.name}' ({item.id})\n")
        self.print(0, item.stats[mode].to_compact_string())


    def _execute_optimize_stats_command(self, args: List[str]):
        if len(args) < 1:
            self.print(1, 'Missing stats.')
            return

        optimized_stats = []

        for index, arg in enumerate(args):
            if arg.startswith('-'):
                index -= 1  # Compensate for the case where the break does not occur
                break

            optimized_stats.append(arg.lower())

        command = ' '.join(args[index + 1:])
        try:
            damages_parameters = DamageParameters.from_string(command, self.manager._get_default_parameters())
        except ValueError as e:
            self.print(1, f'Cannot parse parameters: {str(e)}')
            return

        if damages_parameters.equipment:
            damages_parameters.update_stuff_with_equipment(self.manager.equipments)

        items, value = self.items_manager.get_best_stuff_from_stats(' '.join(optimized_stats), damages_parameters, self.manager.equipments)

        self.print(0, f"Best stuff to maximise '{' '.join(optimized_stats)} (parameters : '{self.manager.default_parameters}' - equipment: '{damages_parameters.equipment}') :")
        self.print(0, '')
        for item in items:
            self.print(0, f" - {item.type.capitalize(): <7} : {item.name} ({item.id})")
        self.print(0, '')
        self.print(0, f" => {int(value):.0f} {' '.join(optimized_stats).capitalize()}")


    def execute_command(self, command: str):
        instr, *args = command.split(' ')

        if instr in StuffManager.OPTIMIZE_STUFF_COMMAND:
            self._execute_optimize_stuff_command(args)
        elif instr in StuffManager.OPTIMIZE_STATS_COMMAND:
            self._execute_optimize_stats_command(args)
        elif instr in StuffManager.EQUIPMENT_COMMAND:
            self._execute_equipment_command(args)
        elif instr in StuffManager.SEARCH_COMMAND:
            self._execute_search_command(args)
        elif instr in StuffManager.ITEM_command:
            self._execute_item_command(args)
