import distutils.util
import json
import math
import os
import re
import sys
from typing import Any, Callable, Dict, List, Tuple

from characteristics_damages import *
from knapsack import get_best_combination
from damage_parameters import DamageParameters
from spell import Spell, SpellBuff
from spell_chain import SpellChains
from spell_set import SpellSet
from stats import Stats


class Manager:
    GENERAL_INSTRUCTIONS = ('s', 'q', 'i', 'cache')
    PARAMETERS_INSTRUCTION = ('p', 'param')
    STATS_INSTRUCTION = ('st',)
    SPELL_INSTRUCTION = ('sp',)
    SPELL_SET_INSTRUCTION = ('ss',)
    DAMAGES_INSTRUCTION = ('dmg', 'dmgs', 'dmgc')

    DIRECTORIES = ('stats', 'spells')

    def __init__(self, print_method: Callable[[int, str], Any]) -> None:
        self.print: Callable[[int, str], Any] = print_method
        self.stats: Dict[str, Stats] = dict()
        self.spells: Dict[str, Spell] = dict()
        self.spell_sets: Dict[str, SpellSet] = dict()
        self.parameters: Dict[str, DamageParameters] = dict()
        self.default_parameters: str = ''
        self.cache: Dict[int, List[Tuple[int, ...]]] = {}

        self._create_dirs()
        self._load_default()
        self._load_from_file()
        self._load_cache()

    def _create_dirs(self):
        for directory in Manager.DIRECTORIES:
            if not os.path.isdir(directory):
                os.mkdir(directory)


    def _get_default_parameters(self):
        if self.default_parameters in self.parameters:
            return self.parameters[self.default_parameters]

        return self.parameters['__default__']


    def _load_default(self):
        self.parameters['__default__'] = DamageParameters.from_string("-pa 1 -pomin 0 -pomax 2048 -t mono")
        self.default_parameters = '__default__'

    def _load_from_file(self):
        try:
            with open('manager.json', 'r', encoding='utf-8') as fi:
                json_data = json.load(fi)

            # STATS
            for stats_filepath in json_data['stats']:
                try:
                    stats = Stats.from_file(stats_filepath)
                    self.stats[stats.get_short_name()] = stats
                except (FileNotFoundError, KeyError, TypeError, ValueError):
                    self.print(1, f"Could not open or read stats page '{stats_filepath}'.")

            # SPELLS
            for spell_filepath in json_data['spells']:
                try:
                    spell = Spell.from_file(spell_filepath)
                    self.spells[spell.get_short_name()] = spell
                except (FileNotFoundError, KeyError, TypeError, ValueError):
                    self.print(1, f"Could not open or read spell '{spell_filepath}'.")

            # SPELL SETS
            for spell_set_data in json_data['spell_sets']:
                try:
                    spell_set = SpellSet()
                    for spell_short_name in spell_set_data['spells']:
                        try:
                            spell_set.add_spell(self.spells[spell_short_name])
                        except KeyError:
                            self.print(1, f"Cannot add spell '{spell_short_name}' to spell set '{spell_set_data['short_name']}': it does not exist.")

                    spell_set.set_name(spell_set_data['name'])
                    spell_set.set_short_name(spell_set_data['short_name'])
                    self.spell_sets[spell_set.get_short_name()] = spell_set
                except KeyError:
                    self.print(1, f"Could not load spell set '{spell_set_data['name']}'.")

            # DEFAULT PARAMS
            for parameters_name in json_data['parameters']:
                try:
                    self.parameters[parameters_name] = DamageParameters.from_string(json_data['parameters'][parameters_name])
                except ValueError:
                    self.print(1, f"Could not load parameters '{parameters_name}'.")

            self.default_parameters = json_data['default_parameters']

        except (FileNotFoundError, KeyError, TypeError):
            self.print(1, "'manager.json' file does not exist or is innaccessible, using default load only.")
            return


    def _load_cache(self) -> None:
        try:
            with open('cache.txt', 'r', encoding='ascii') as fi:
                for line in fi:
                    computation_hash, permutations = line.split(':')
                    permutations = [tuple(map(int, permutation.split(','))) if permutation != '' else tuple() for permutation in permutations.split(';')]
                    self.cache[computation_hash] = permutations
        except FileNotFoundError:  # File does not exist, do nothing
            pass
        except (ValueError, TypeError):  # Error while unpacking or splitting
            self.print(1, 'Could not read part or all of cache file.')


    def save(self, print_message=True, save_cache=False):
        stats_filepaths = list()
        for stats in self.stats.values():
            filepath = f'stats\\{stats.get_safe_name()}.json'
            stats.save_to_file(filepath)
            stats_filepaths.append(filepath)

        spells_filepaths = list()
        for spell in self.spells.values():
            filepath = f'spells\\{spell.get_safe_name()}.json'
            spell.save_to_file(filepath)
            spells_filepaths.append(filepath)

        spell_sets = list()
        for spell_set in self.spell_sets.values():
            spell_sets.append({
                'spells': [spell.get_short_name() for spell in spell_set],
                'name': spell_set.get_name(),
                'short_name': spell_set.get_short_name()
            })

        string_parameters = dict()
        for parameters_name in self.parameters:
            string_parameters[parameters_name] = self.parameters[parameters_name].to_string()

        json_valid_data = {
            'stats': stats_filepaths,
            'spells': spells_filepaths,
            'spell_sets': spell_sets,
            'parameters': string_parameters,
            'default_parameters': self.default_parameters
        }

        with open('manager.json', 'w', encoding='utf-8') as fo:
            json.dump(json_valid_data, fo)

        if save_cache:
            with open('cache.txt', 'w', encoding='ascii') as fo:
                for computation_hash in self.cache:
                    fo.write(f'{computation_hash}:{";".join(",".join(map(str, permutation)) for permutation in self.cache[computation_hash])}\n')

        if print_message:
            self.print(0, 'Data successfully saved!')


    def _print_infos(self):
        # TODO: redo the printing of params and infos
        self.print(0, self._get_default_parameters().to_string())


    def _print_cache(self):
        self.print(0, f'Cache entries count: {len(self.cache)}')
        try:
            total_size = f"{os.path.getsize('cache.txt') / 1024 / 1024:.2f} MB"
        except OSError:
            total_size = 'Unknown'
        self.print(0, f'Total size of cache file: {total_size}')


    def _execute_general_command(self, instr, args: List[str]):
        if instr == 's':
            self.save(save_cache=True)
        elif instr == 'i':
            self._print_infos()
        elif instr == 'cache':
            self._print_cache()


    def _execute_parameters_command(self, instr, args: List[str]):
        if len(args) == 0:
            self.print(1, 'Missing action in the command.')
            return

        command_action = args[0]

        if command_action == 'new':
            if len(args) < 2:
                self.print(1, 'Missing parameters name.')
                return

            parameters_name = args[1]

            if parameters_name in self.parameters:
                self.print(1, f"Parameters '{parameters_name}' already exist.")
                return

            self.parameters[parameters_name] = DamageParameters.from_existing(self._get_default_parameters())
            self.save(False)
            self.print(0, f"Parameters '{parameters_name}' successfully created from current ones.")

        elif command_action == 'change':
            if len(args) < 2:
                self.print(1, 'Missing parameters name.')
                return

            parameters_name = args[1]

            if not parameters_name in self.parameters:
                self.print(1, f"Parameters '{parameters_name}' do not exist.")
                return

            self.default_parameters = parameters_name
            self.save(False)
            self.print(0, f"Current parameters changed to '{parameters_name}' successfully.")

        elif command_action.startswith('-'):
            command = ' '.join(args)

            current_parameters = self._get_default_parameters()

            try:
                current_parameters = DamageParameters.from_string(command, current_parameters)
                self.parameters[self.default_parameters] = current_parameters
            except ValueError as e:
                self.print(1, f'Cannot parse parameters: {str(e)}')
                return

            self.save(False)
            self.print(0, f"Current parameters updated successfully.")

        elif command_action == 'ls':
            self.print(0, '=== Parameters set\n')
            for parameters_name, parameters in sorted(self.parameters.items(), key=lambda item: item[0]):
                self.print(0, f" - Set '{parameters.full_name}' ({parameters_name}){f' [selected]' if parameters_name == self.default_parameters else ''}")

        elif command_action == 'show':
            if len(args) < 2:
                parameters_name = self.default_parameters
            else:
                parameters_name = args[1]

                if not parameters_name in self.parameters:
                    self.print(1, f"Parameters '{parameters_name}' do not exist.")
                    return

            parameters = self.parameters[parameters_name]
            self.print(0, f"===== Page '{parameters.full_name}' ({parameters_name})")
            self.print(0, f"PA: {parameters.pa}")
            self.print(0, f"PO: {parameters.get_min_po()} - {parameters.get_max_po()}")
            self.print(0, f"Type: {parameters.type}")
            self.print(0, f"Distance: {parameters.distance}")

            self.print(0, f"\nBase damage increase:")
            for characteristic in range(CHARACTERISTICS_COUNT):
                if parameters.get_base_damage(characteristic) > 0:
                    self.print(0, f" - {CHARACTERISTICS_NAMES[characteristic]}: {parameters.get_base_damage(characteristic)}")

            self.print(0, f"\nResistances:")
            for characteristic in range(5):
                self.print(0, f" - {CHARACTERISTICS_NAMES[characteristic]}: {parameters.get_resistance(characteristic)} %")

            if len(parameters.stats) > 0:
                self.print(0, f"\nStats page{'s' if len(parameters.stats) > 1 else ''}:")
                for stats_short_name in parameters.stats:
                    if stats_short_name in self.stats:
                        self.print(0, f" - '{self.stats[stats_short_name].get_name()}' ({stats_short_name})")


        else:
            self.print(1, f"Unknown action '{command_action}' for parameters commands.")


    def _create_stats(self, stats: Stats = None, no_name: bool = False) -> Stats:
        if stats is None:
            stats = Stats()
        else:
            stats = Stats.from_existing(stats)

        if not no_name:
            name = input(f'Stats page name{f"({stats.get_name()})" if stats.get_name() != "" else ""}: ')
            if name:
                stats.set_name(name)

        self.print(0, '\n=== Characteristics\n')
        for characteristic in range(CHARACTERISTICS_COUNT):
            if characteristic == NEUTRAL:
                continue

            characteristic_value = input(f'{CHARACTERISTICS_NAMES[characteristic]} ({stats.get_characteristic(characteristic)}): ')
            if characteristic_value == '/':
                break

            if characteristic_value:
                stats.set_characteristic(characteristic, int(characteristic_value))

        self.print(0, '\n=== Damages\n')
        for damage in range(DAMAGES_COUNT):
            damage_value = input(f'{DAMAGES_NAMES[damage]} ({stats.get_damage(damage)}): ')
            if damage_value == '/':
                break

            if damage_value:
                stats.set_damage(damage, int(damage_value))

        self.print(0, '')
        bonus_crit_chance = input(f'Bonus crit chance % ({100 * stats.get_bonus_crit_chance():.1f} %): ')
        if bonus_crit_chance:
            stats.set_bonus_crit_chance(float(bonus_crit_chance) / 100.0)

        return stats

    def _execute_stats_command(self, args: List[str]):
        if len(args) == 0:
            self.print(1, 'Missing action in the command.')
            return

        command_action = args[0]

        if command_action == 'new':
            if len(args) < 2:
                self.print(1, 'Missing short name to create stats page.')
                return

            short_name = args[1]

            if short_name in self.stats:
                self.print(1, f"Stats page '{short_name}' already exists.")
                return

            try:
                stats = self._create_stats()
            except KeyboardInterrupt:
                self.print(0, '\nCancelled stats page creation.')
                return
            stats.set_short_name(short_name)

            self.stats[short_name] = stats
            self.save(False)
            self.print(0, f"Page '{short_name}' successfully created!")

        elif command_action == 'ls':
            self.print(0, '=== Stats pages\n')
            for stats in sorted(self.stats.values(), key=lambda stat: stat.get_name()):
                self.print(0, f" - Page '{stats.get_name()}' ({stats.get_short_name()})")

        elif command_action == 'show':
            if len(args) < 2:
                self.print(1, 'Missing stats page short name.')
                return

            short_name = args[1]

            if short_name in self.stats:
                stats = self.stats[short_name]
                printed_string = [f"===== Page '{stats.get_name()}' ({short_name})", '=== Characteristics\n']
                for characteristic in range(CHARACTERISTICS_COUNT):
                    if characteristic == NEUTRAL:
                        continue
                    printed_string.append(f"{CHARACTERISTICS_NAMES[characteristic]:.<15}{stats.get_characteristic(characteristic)}")

                printed_string.append('\n=== Damages\n')
                for damage in range(DAMAGES_COUNT):
                    printed_string.append(f"{DAMAGES_NAMES[damage]:.<15}{stats.get_damage(damage)}")

                printed_string.append(f'\n{"BONUS CRIT":.<15}{100 * stats.get_bonus_crit_chance():.1f} %')

                self.print(0, "\n".join(printed_string))
            else:
                self.print(1, f"Stats page '{short_name}' does not exist.")


        elif command_action == 'mod':
            if len(args) < 2:
                self.print(1, 'Missing stats page short name.')
                return

            short_name = args[1]

            if short_name in self.stats:
                try:
                    self.stats[short_name] = self._create_stats(self.stats[short_name])
                except KeyboardInterrupt:
                    self.print(0, '\nCancelled stats page modification.')
                    return

                self.save(False)
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

        elif command_action == 'addfile':
            if len(args) < 2:
                self.print(1, 'Missing stats page name.')
                return

            stats_short_name = args[1]
            if stats_short_name in self.spells:
                self.print(1, f"Stats page '{stats_short_name}' already exist.")
                return

            spell_filepath = f'stats\\{stats_short_name}.json'
            try:
                stats = Stats.from_file(spell_filepath)
                self.stats[stats.get_short_name()] = stats
            except FileNotFoundError:
                self.print(1, f"'{spell_filepath}' file does not exist.")
                return
            except (KeyError, TypeError, ValueError):
                self.print(1, f"Could not read '{spell_filepath}' file : invalid stats page.")
                return

            self.save(False)
            self.print(0, f"Stats page '{stats_short_name}' successfully added.")

        elif command_action == 'copy':
            if len(args) < 3:
                self.print(1, 'Missing current or new stats page name.')
                return

            current_stats_short_name = args[1]

            if not current_stats_short_name in self.stats:
                self.print(1, f"Stats page '{current_stats_short_name}' does not exists.")
                return

            new_stats_short_name = args[2]

            if new_stats_short_name in self.stats:
                self.print(1, f"Stats page '{new_stats_short_name}' already exists.")
                return

            new_stats = self.stats[current_stats_short_name].copy()
            new_stats.set_short_name(new_stats_short_name)
            self.stats[new_stats_short_name] = new_stats
            self.save(False)
            self.print(0, 'Stats page succesfully copied.')

        else:
            self.print(1, f"Unknown action '{command_action}' for stats commands.")


    def _create_buff(self, buff: SpellBuff = None) -> SpellBuff:
        if buff is None:
            buff = SpellBuff()

        is_huppermage_states = input(f'Is Huppermage states ({buff.is_huppermage_states}) (0/1)? ')
        if is_huppermage_states:
            try:
                buff.is_huppermage_states = distutils.util.strtobool(is_huppermage_states)
            except ValueError:  # if the value cannot be converted to a boolean, do as if nothing was input
                pass

        if buff.is_huppermage_states:
            new_output_states_txt = f' ({", ".join(sorted(buff.new_output_states))})' if buff.new_output_states else ''
            huppermage_states = input(f"\nHuppermage states without the 'h:' prefix{new_output_states_txt}: ")
            for huppermage_state in huppermage_states.split(' '):
                # If the state starts with a minus sign, it needs to be deleted
                if huppermage_state.startswith('-'):
                    buff.remove_new_output_state(f'h:{huppermage_state[1:]}')
                    continue
                # Add the prefix 'h:' is front of every state if not already there
                huppermage_state = f'h:{huppermage_state}' if not huppermage_state.startswith('h:') else huppermage_state
                if re.match(r'h:\d?[aefw]', huppermage_state):
                    buff.add_new_output_state(huppermage_state)
                else:
                    self.print(0, f"[WARNING] The state '{huppermage_state[2:]}' is not a valid Huppermage state (should be one of 'a', 'e', 'f', 'w').")

            # Huppermage states buff have no other effects
            return buff

        trigger_states_txt = f' ({", ".join(sorted(buff.trigger_states))})' if buff.trigger_states else ''
        trigger_states = input(f'\nTrigger states{trigger_states_txt}: ')
        if trigger_states:
            for state in trigger_states.split(' '):
                if state.startswith('-'):
                    buff.remove_trigger_state(state[1:])
                else:
                    buff.add_trigger_state(state)

        forbidden_states_txt = f' ({", ".join(sorted(buff.forbidden_states))})' if buff.forbidden_states else ''
        forbidden_states = input(f'Forbidden states{forbidden_states_txt}: ')
        if forbidden_states:
            for state in forbidden_states.split(' '):
                if state.startswith('-'):
                    buff.remove_forbidden_state(state[1:])
                else:
                    buff.add_forbidden_state(state)

        new_output_states_txt = f' ({", ".join(sorted(buff.new_output_states))})' if buff.new_output_states else ''
        new_output_states = input(f'New states to add if triggered{new_output_states_txt}: ')
        if new_output_states:
            for state in new_output_states.split(' '):
                if state.startswith('-'):
                    buff.remove_new_output_state(state[1:])
                else:
                    buff.add_new_output_state(state)
            buff.add_new_output_states(set(new_output_states.split(' ')))

        removed_output_states_txt = f' ({", ".join(sorted(buff.removed_output_states))})' if buff.removed_output_states else ''
        removed_output_states = input(f'States to remove if triggered{removed_output_states_txt}: ')
        if removed_output_states:
            for state in removed_output_states.split(' '):
                if state.startswith('-'):
                    buff.remove_removed_output_state(state[1:])
                else:
                    buff.add_removed_output_state(state)

        deactivate_damages = input(f'\nDoes trigger deactivates spell damages ({buff.deactivate_damages}) (0/1)? ')
        if deactivate_damages:
            try:
                buff.deactivate_damages = distutils.util.strtobool(deactivate_damages)
            except ValueError:  # if the value cannot be converted to a boolean, do as if nothing was input
                pass

        self.print(0, '\n=== Base damage increase if triggered\n')
        for characteristic in range(CHARACTERISTICS_COUNT):
            value = input(f'{CHARACTERISTICS_NAMES[characteristic]} ({buff.base_damages[characteristic]}): ')
            if value == '/':
                break

            if value:
                buff.set_base_damages(characteristic, int(value))

        self.print(0, '')
        for characteristic in range(CHARACTERISTICS_COUNT):
            default_damaging = (buff.base_damages[characteristic] > 0)
            damaging = input(f'{CHARACTERISTICS_NAMES[characteristic]} damaging ({int(default_damaging)}) (0/1)? ')

            if damaging == '/':
                break

            try:
                damaging = distutils.util.strtobool(damaging) if damaging else default_damaging
            except ValueError:  # if the valeur cannot be converted to a boolean, do as if False was input
                damaging = False

            if damaging:
                buff.add_additional_damaging_characteristic(characteristic)
            else:
                buff.remove_additional_damaging_characteristic(characteristic)

        self.print(0, '\n=== Stats pages to add to next spells when triggered')
        while True:
            if buff.has_stats:
                self.print(0, '\n=== Stats page(s) currently existing :')
                for spell in buff.stats:
                    stats_page_string = buff.stats[spell].to_compact_string(indentation='  ')
                    if stats_page_string:
                        self.print(0, ' - For all next spells' if spell == "__all__" else f" - For spell '{spell}'")
                        self.print(0, stats_page_string)

            spell = input(f"\nSpell name (or '__all__') to add another stats page to (ENTER to skip)? ")
            if spell:
                try:
                    buff.stats[spell] = self._create_stats(buff.stats.get(spell, None), no_name=True)
                except KeyboardInterrupt:
                    self.print(0, f"\n\nCancelled page creation for spell '{spell}'.")
            else:
                break

        self.print(0, '\n=== Damages parameters to add to next spells when triggered')
        while True:
            if buff.has_parameters:
                self.print(0, '\n=== Damages parameters currently existing :')
                for spell in buff.damage_parameters:
                    damage_parameters_string = buff.damage_parameters[spell].to_compact_string()
                    self.print(0, ' - For all next spells' if spell == "__all__" else f" - For spell '{spell}'")
                    self.print(0, f'  -> {damage_parameters_string}')

            spell = input(f"\nSpell name (or '__all__') to add damage parameters to (ENTER to skip)? ")
            if spell:
                try:
                    damage_parameters_command = input('Damage parameters string: ')
                    d = DamageParameters.from_string(damage_parameters_command)
                    buff.add_damage_parameters(d, spell)
                except KeyboardInterrupt:
                    self.print(0, f"\n\nCancelled damage parameters addition for spell '{spell}'.")
            else:
                break

        return buff


    def _create_spell(self, spell: Spell = None) -> Spell:
        if spell is None:
            spell = Spell()

        name = input(f'Spell name{f" ({spell.get_name()})" if spell.get_name() != "" else ""}: ')
        if name:
            spell.set_name(name)

        is_weapon = input(f'Weapon ({spell.parameters.is_weapon}) (0/1): ')
        if is_weapon:
            try:
                spell.set_weapon(distutils.util.strtobool(is_weapon))
            except ValueError:  # if the valeur cannot be converted to a boolean, do as if nothing was input
                pass

        position = input(f'Spell reach ({spell.parameters.position}) (all/line/diag)? ')
        if position:
            spell.set_position(position)

        self.print(0, '\n=== Base damages\n')
        for characteristic in range(CHARACTERISTICS_COUNT):
            unused_characteristic = False
            self.print(0, f'{CHARACTERISTICS_NAMES[characteristic]}: ')
            base_damages = spell.get_base_damages(characteristic)

            for field in ('min', 'max', 'crit_min', 'crit_max'):
                value = input(f'  - {field.replace("_", " ").capitalize()} ({base_damages[field]}): ')
                if value == '/':
                    unused_characteristic = True
                    break
                if value:
                    base_damages[field] = int(value)

            if not unused_characteristic:
                spell.set_base_damages(characteristic, base_damages)
                default_damaging = (characteristic in spell.parameters.damaging_characteristics) or any(base_damages[field] > 0 for field in base_damages)
                damaging = input(f'  - Damaging ({int(default_damaging)}) (1/0)? ')

                if damaging == '/':
                    continue

                try:
                    damaging = distutils.util.strtobool(damaging) if damaging else default_damaging
                except ValueError:  # if the valeur cannot be converted to a boolean, do as if False was input
                    damaging = False

                if damaging:
                    spell.add_damaging_characteristic(characteristic)
                else:
                    spell.remove_damaging_characteristic(characteristic)


        self.print(0, '')
        pa = input(f'PA count ({spell.get_pa()}): ')
        if pa:
            spell.set_pa(int(pa))

        self.print(0, '')
        crit_chance = input(f'Crit chance % ({100 * spell.get_crit_chance():.1f} %): ')
        if crit_chance:
            spell.set_crit_chance(float(crit_chance) / 100)

        self.print(0, '')
        uses_per_target = input(f'Uses per target ({spell.get_uses_per_target()}): ')
        if uses_per_target:
            spell.set_uses_per_target(int(uses_per_target))

        uses_per_turn = input(f'Uses per turn ({spell.get_uses_per_turn()}): ')
        if uses_per_turn:
            spell.set_uses_per_turn(int(uses_per_turn))

        self.print(0, '')
        min_po = input(f'Minimum PO ({spell.get_min_po()}): ')
        min_po = int(min_po) if min_po else None
        max_po = input(f'Maximum PO ({spell.get_max_po()}): ')
        max_po = int(max_po) if min_po else None

        spell.set_po(min_po=min_po, max_po=max_po)

        while True:
            self.print(0, '\n=== Buffs')
            buff_command_string = "\n'new' to create a buff or ENTER to skip: "
            if spell.buffs:
                buff_command_string = "\nBuff index to update, 'new' to create another one, 'del <index>' to delete an existing one (ENTER to skip): "
                self.print(0, 'Already created: ')
                for index, buff in enumerate(spell.buffs):
                    self.print(0, f' {index + 1}. {buff.to_compact_string()}')

            buff_command = input(buff_command_string).lower()
            if buff_command == 'new':
                try:
                    spell.add_buff(self._create_buff())
                except KeyboardInterrupt:
                    self.print(0, '\nCancelled buff creation.')

            elif buff_command.isnumeric():
                try:
                    index = int(buff_command) - 1
                    spell.buffs[index] = self._create_buff(spell.buffs[index])
                except KeyboardInterrupt:
                    self.print(0, '\nCancelled buff creation.')
                except (ValueError, IndexError):
                    self.print(0, '[WARNING] Wrong buff index.')

            elif re.match(r'del \d+', buff_command):
                try:
                    delete_index = int(buff_command.split(' ')[1]) - 1
                    del spell.buffs[delete_index]
                except (ValueError, IndexError):
                    self.print(0, '[WARNING] Wrong buff index.')

            elif buff_command in ('', 'q'):
                break

            else:
                self.print(0, '[WARNING] Wrong command.')

        return spell


    def _execute_spell_command(self, args: List[str]):
        if len(args) == 0:
            self.print(1, 'Missing action in the command.')
            return

        command_action = args[0]

        if command_action == 'new':
            if len(args) < 2:
                self.print(1, 'Missing short name to create spell.')
                return

            short_name = args[1]

            if short_name in self.spells:
                self.print(1, f"Spell '{short_name}' already exists.")
                return

            try:
                spell = self._create_spell()
            except KeyboardInterrupt:
                self.print(0, '\nCancelled spell creation.')
                return
            spell.set_short_name(short_name)

            self.spells[short_name] = spell
            self.save(False)
            self.print(0, f"Spell '{short_name}' successfully created!")

        elif command_action == 'ls':
            self.print(0, '=== Spells\n')
            for spell in sorted(self.spells.values(), key=lambda spell: spell.get_name()):
                self.print(0, f" - '{spell.get_name()}' ({spell.get_short_name()})")

        elif command_action == 'show':
            if len(args) < 2:
                self.print(1, 'Missing spell short name.')
                return

            short_name = args[1]

            if not short_name in self.spells:
                self.print(1, f"Spell '{short_name}' does not exist.")
                return

            spell = self.spells[short_name]
            printed_string = [f"===== Spell '{spell.get_name()}' ({short_name})", '=== Spell characteristics']

            printed_string.append(f"PA: {spell.get_pa()}")
            printed_string.append(f"PO: {spell.get_min_po()} - {spell.get_max_po()}")
            printed_string.append(f"Uses per target: {spell.get_uses_per_target() if spell.get_uses_per_target() > 0 else '∞'}")
            printed_string.append(f"Uses per turn: {spell.get_uses_per_turn() if spell.get_uses_per_turn() > 0 else '∞'}")
            printed_string.append(f'Crit chance: {100 * spell.get_crit_chance():.1f} %')
            printed_string.append(f'Weapon: {spell.parameters.is_weapon}')
            printed_string.append(f'Spell reach: {spell.parameters.position.capitalize()}')

            printed_string.append("\n=== Base damages\n")
            for characteristic in range(CHARACTERISTICS_COUNT):
                base_damages = spell.get_base_damages(characteristic)
                if all(value == 0 for value in base_damages.values()):
                    continue
                
                if spell.does_damage_in_characteristic(characteristic):
                    printed_string.append(f" {CHARACTERISTICS_NAMES[characteristic]}: {base_damages['min']} - {base_damages['max']} ({base_damages['crit_min']} - {base_damages['crit_max']})")
                else:
                    printed_string.append(f" [{CHARACTERISTICS_NAMES[characteristic]}: {base_damages['min']} - {base_damages['max']} ({base_damages['crit_min']} - {base_damages['crit_max']})]")


            if spell.buffs:
                printed_string.append("\n=== Buffs\n")
                for buff in spell.buffs:
                    printed_string.append(f' {buff.to_compact_string()}')

            self.print(0, '\n'.join(printed_string))

        elif command_action == 'buffs':
            if len(args) < 2:
                self.print(1, 'Missing spell short name.')
                return

            short_name = args[1]

            if not short_name in self.spells:
                self.print(1, f"Spell '{short_name}' does not exist.")
                return

            spell = self.spells[short_name]
            if len(spell.buffs) > 0:
                printed_string = [f"===== Buffs of spell '{spell.get_name()}' ({short_name})"]
                for index, buff in enumerate(spell.buffs):
                    printed_string.append(f'=== Buff {index + 1}')
                    if buff.is_huppermage_states:
                        printed_string.append(f'{buff.to_compact_string(only_states=True)}\n')
                        continue

                    printed_string.append(f'States: {buff.to_compact_string(only_states=True)}\n')

                    if any(value != 0 for value in buff.base_damages):
                        printed_string.append('Base damages:')
                        for characteristic in range(CHARACTERISTICS_COUNT):
                            if buff.base_damages[characteristic] > 0:
                                if buff.has_additional_damaging_characteristic(characteristic):
                                    printed_string.append(f' {CHARACTERISTICS_NAMES[characteristic]}: {buff.base_damages[characteristic]}')
                                else:
                                    printed_string.append(f' [{CHARACTERISTICS_NAMES[characteristic]}: {buff.base_damages[characteristic]}]')
                        printed_string.append('')

                    if buff.has_stats:
                        for affected_spell in buff.stats:
                            printed_string.append('Stats :')
                            stats_page_string = buff.stats[affected_spell].to_compact_string(indentation=' ')
                            if stats_page_string:
                                printed_string.append('->For all next spells' if affected_spell == "__all__" else f"->For spell '{affected_spell}'")
                                printed_string.append(stats_page_string)
                        printed_string.append('')

                    if buff.has_parameters:
                        for affected_spell in buff.damage_parameters:
                            printed_string.append('Damage parameters :')
                            damage_parameters_string = buff.damage_parameters[affected_spell].to_compact_string()
                            if damage_parameters_string:
                                printed_string.append('->For all next spells' if affected_spell == "__all__" else f"->For spell '{affected_spell}'")
                                printed_string.append(f' {damage_parameters_string}')
                        printed_string.append('')

                self.print(0, '\n'.join(printed_string))

        elif command_action == 'mod':
            if len(args) < 2:
                self.print(1, 'Missing spell short name.')
                return

            short_name = args[1]

            if short_name in self.spells:
                try:
                    self.spells[short_name] = self._create_spell(self.spells[short_name])
                except KeyboardInterrupt:
                    self.print(0, '\nCancelled spell modification.')
                    return

                self.save(False)
                self.print(0, f"Spell '{short_name}' successfully modified!")
            else:
                self.print(1, f"Spell '{short_name}' does not exist.")

        elif command_action == 'rm':
            if len(args) < 2:
                self.print(1, 'Missing spell short name.')
                return

            short_name = args[1]
            if short_name in self.spells:
                self.spells.pop(short_name)
                self.print(0, f"Spell '{short_name}' successfully deleted!")
            else:
                self.print(1, f"Spell '{short_name}' does not exist.")

        elif command_action in ('dmg', 'd'):
            if len(args) < 2:
                self.print(1, 'Missing spell name.')
                return

            spell_short_name = args[1]
            if not spell_short_name in self.spells:
                self.print(1, f"Spell '{spell_short_name}' does not exist.")
                return

            spell = self.spells[spell_short_name]

            command = ' '.join(args[2:])
            try:
                damages_parameters = DamageParameters.from_string(command, self._get_default_parameters())
            except ValueError as e:
                self.print(1, f'Cannot parse parameters: {str(e)}')
                return

            total_stats = damages_parameters.get_total_stats(self.stats)
            spell_output = spell.get_damages_and_buffs_with_states_single(total_stats, damages_parameters)

            final_crit_chance = spell.get_crit_chance() + total_stats.get_bonus_crit_chance()
            if final_crit_chance > 1.0:
                final_crit_chance = 1.0

            average_dmg_final = spell_output.average_damage * (1 - final_crit_chance) + spell_output.average_damage_crit * final_crit_chance

            self.print(0, f"Damages of the spell '{spell.get_name()}' (parameters set : '{self.default_parameters}' ; distance: {damages_parameters.distance} ; initial states: ({','.join(sorted(damages_parameters.starting_states))})):\n")
            self.print(0, 'Individual characteristics:')
            for characteristic in range(CHARACTERISTICS_COUNT):
                if sum(spell_output.damages_by_characteristic[characteristic][field] for field in ('min', 'max', 'crit_min', 'crit_max')) > 0:
                    self.print(0, f' - {CHARACTERISTICS_NAMES[characteristic]}: {spell_output.damages_by_characteristic[characteristic]["min"]} - {spell_output.damages_by_characteristic[characteristic]["max"]} ({spell_output.damages_by_characteristic[characteristic]["crit_min"]} - {spell_output.damages_by_characteristic[characteristic]["crit_max"]})')

            self.print(0, '')
            self.print(0, f'Total damages:   {spell_output.damages["min"]} - {spell_output.damages["max"]} ({spell_output.damages["crit_min"]} - {spell_output.damages["crit_max"]})')
            self.print(0, f'Average damages: {spell_output.average_damage:.0f} ({spell_output.average_damage_crit:.0f}) => {average_dmg_final:.0f} with {100 * final_crit_chance:.0f} % crit chance')

        elif command_action == 'addfile':
            if len(args) < 2:
                self.print(1, 'Missing spell name.')
                return

            spell_short_name = args[1]
            if spell_short_name in self.spells:
                self.print(1, f"Spell '{spell_short_name}' already exist.")
                return

            spell_filepath = f'spells\\{spell_short_name}.json'
            try:
                spell = Spell.from_file(spell_filepath)
                self.spells[spell.get_short_name()] = spell
            except FileNotFoundError:
                self.print(1, f"'{spell_filepath}' file does not exist.")
                return
            except (KeyError, TypeError, ValueError):
                self.print(1, f"Could not read '{spell_filepath}' file : invalid spell.")
                return

            self.save()
            self.print(0, f"Spell '{spell_short_name}' successfully added.")

        else:
            self.print(1, f"Unknown action '{command_action}' for spell commands.")

    def _execute_spell_set_command(self, args: List[str]):
        if len(args) == 0:
            self.print(1, 'Missing action in the command.')
            return

        command_action = args[0]

        if command_action == 'new':
            if len(args) < 2:
                self.print(1, 'Missing short name to create spell set.')
                return

            short_name = args[1]

            if short_name in self.spell_sets:
                self.print(1, f"Spell set '{short_name}' already exists.")
                return

            spell_set = SpellSet()
            spell_set.set_short_name(short_name)
            try:
                spell_set.set_name(input("Spell set name: ") or short_name)
            except KeyboardInterrupt:
                self.print(0, '\nCancelled spell set creation.')
                return

            self.spell_sets[short_name] = spell_set
            self.save(False)
            self.print(0, f"Spell set '{short_name}' successfully created!")

        elif command_action == 'ls':
            self.print(0, '=== Spell sets\n')
            for spell_set in sorted(self.spell_sets.values(), key=lambda spell_set: spell_set.get_name()):
                self.print(0, f" - '{spell_set.get_name()}' ({spell_set.get_short_name()}): {len(spell_set)} spell{'s' if len(spell_set) > 1 else ''}")

        elif command_action == 'show':
            if len(args) < 2:
                self.print(1, 'Missing spell set short name.')
                return

            short_name = args[1]

            if short_name in self.spell_sets:
                spell_set = self.spell_sets[short_name]
                printed_string = [f"===== Spell set '{spell_set.get_name()}' ({short_name})"]

                printed_string.append("Spells: ")

                for spell in spell_set:
                    printed_string.append(f" - {spell.get_name()} ({spell.get_short_name()})")

                self.print(0, '\n'.join(printed_string))
            else:
                self.print(1, f"Spell set '{short_name}' does not exist.")

        elif command_action == 'rm':
            if len(args) < 2:
                self.print(1, 'Missing spell set short name.')
                return

            short_name = args[1]
            if short_name in self.spell_sets:
                self.spell_sets.pop(short_name)
                self.print(0, f"Spell set '{short_name}' successfully deleted!")
            else:
                self.print(1, f"Spell set '{short_name}' does not exist.")

        elif command_action == 'add':
            if len(args) < 3:
                self.print(1, 'Missing spell set or spell short name.')
                return

            spell_set_short_name = args[1]
            for spell_short_name in args[2:]:
                if spell_set_short_name in self.spell_sets and spell_short_name in self.spells:
                    spell_set = self.spell_sets[spell_set_short_name]
                    spell = self.spells[spell_short_name]
                    if not spell in spell_set:
                        spell_set.add_spell(spell)
                        self.print(0, f"Spell '{spell_short_name}' successfully added to spell set '{spell_set_short_name}'!")
                    else:
                        self.print(1, f"Spell '{spell_short_name}' already in spell set '{spell_set_short_name}'!")
                else:
                    self.print(1, f"Spell set '{spell_set_short_name}' or spell '{spell_short_name}' do not exist.")

            self.save(False)

        elif command_action == 'del':
            if len(args) < 3:
                self.print(1, 'Missing spell set or spell short name.')
                return

            spell_set_short_name = args[1]
            spell_short_name = args[2]

            if spell_set_short_name in self.spell_sets and spell_short_name in self.spells:
                spell_set = self.spell_sets[spell_set_short_name]
                spell = self.spells[spell_short_name]
                if spell in spell_set:
                    spell_set.remove_spell(spell)
                    self.print(0, f"Spell '{spell_short_name}' successfully removed from spell set '{spell_set_short_name}'!")
                else:
                    self.print(1, f"Spell '{spell_short_name}' is not in spell set '{spell_set_short_name}'!")
            else:
                self.print(1, f"Spell set '{spell_set_short_name}' or spell '{spell_short_name}' do not exist.")

        elif command_action == 'copy':
            if len(args) < 3:
                self.print(1, 'Missing current or new spell set name.')
                return

            current_set_short_name = args[1]

            if not current_set_short_name in self.spell_sets:
                self.print(1, f"Spell set '{current_set_short_name}' does not exists.")
                return

            new_set_short_name = args[2]

            if new_set_short_name in self.spell_sets:
                self.print(1, f"Spell set '{current_set_short_name}' already exists.")
                return

            current_spell_set = self.spell_sets[current_set_short_name]
            new_spell_set = SpellSet()
            new_spell_set.short_name = new_set_short_name
            new_spell_set.spells = current_spell_set.spells[:]

            try:
                new_spell_set.set_name(input("Copied spell set name: ") or new_set_short_name)
            except KeyboardInterrupt:
                self.print(0, '\nCancelled spell set creation.')
                return

            self.spell_sets[new_set_short_name] = new_spell_set
            self.print(0, 'Spell set successfully copied.')

        else:
            self.print(1, f"Unknown action '{command_action}' for spell commands.")


    def _execute_damages_command(self, args: List[str], simple: bool = False):
        if len(args) < 1:
            self.print(1, 'Missing spell set.')
            return

        spell_set_short_name = args[0]

        if not spell_set_short_name in self.spell_sets:
            self.print(1, f"Spell set '{spell_set_short_name}' does not exist.")
            return

        spell_set = self.spell_sets[spell_set_short_name]

        command = ' '.join(args[1:])
        try:
            damages_parameters = DamageParameters.from_string(command, self._get_default_parameters())
        except ValueError as e:
            self.print(1, f'Cannot parse parameters: {str(e)}')
            return

        spell_list = list()
        if damages_parameters.type == 'mono':
            spell_list = spell_set.get_spell_list_single_target(damages_parameters)
        elif damages_parameters.type == 'multi':
            spell_list = spell_set.get_spell_list_multiple_targets(damages_parameters)
        elif damages_parameters.type == 'versa':
            spell_list = spell_set.get_spell_list_versatile(damages_parameters)

        total_stats = damages_parameters.get_total_stats(self.stats)

        if simple:
            best_spells, max_damage = get_best_combination(spell_list, total_stats, parameters=damages_parameters)

            best_spells.sort(key=lambda spell:spell.get_pa(), reverse=True)

            self.print(0, f"Maximum average damages ('{self.default_parameters}' ; PA = {damages_parameters.pa} ; PO = {damages_parameters.get_min_po()} - {damages_parameters.get_max_po()} ; type = {damages_parameters.type} ; position = {damages_parameters.position} ; distance = {damages_parameters.distance}) is: {max_damage:.0f}\n")
            self.print(0, 'Using: ')
            for spell in best_spells:
                self.print(0, f" - {spell.get_name()} ({int(spell.get_average_damages(total_stats, damages_parameters)):.0f} dmg)")
        else:
            spell_chain = SpellChains()
            for spell in spell_list:
                spell_chain.add_spell(spell)

            try:
                damages = spell_chain.get_detailed_damages(total_stats, damages_parameters, cache=self.cache)
            except KeyboardInterrupt:
                self.print(0, 'Cancelled damages computation.')
                return

            best_combination = next(iter(damages))
            average_damages, detailed_damages = damages[best_combination]
            self.print(0, f"Maximum average damages ('{self.default_parameters}' ; PA = {damages_parameters.pa} ; PO = {damages_parameters.get_min_po()} - {damages_parameters.get_max_po()} ; type = {damages_parameters.type} ; position = {damages_parameters.position} ; distance = {damages_parameters.distance}) is:\n")
            self.print(0, f" => {average_damages:.0f} dmg : {detailed_damages['min']} - {detailed_damages['max']} ({detailed_damages['crit_min']} - {detailed_damages['crit_max']})\n")
            self.print(0, 'Using, in this order: ')
            for spell_short_name in best_combination:
                spell = self.spells[spell_short_name]
                self.print(0, f" - {spell.get_name()}")

            same_damages_combinations = []
            for combination in damages:
                if combination != best_combination and math.isclose(damages[combination][0], average_damages, abs_tol=1e-4):
                    same_damages_combinations.append(combination)

            self.print(0, f"\n{len(damages)} possible combinations, {len(same_damages_combinations)} with the same damages, including: ")
            for combination in same_damages_combinations[:3]:
                self.print(0, f" - {', '.join(self.spells[spell_short_name].get_name() for spell_short_name in combination)}")


    def _execute_damages_combination_command(self, args: List[str]):
        if len(args) < 1:
            self.print(1, 'Missing spells.')
            return

        spell_list: List[Spell] = list()

        for index, spell_short_name in enumerate(args):
            if spell_short_name.startswith('-'):
                index -= 1  # Compensate for the case where the break does not occur
                break

            if not spell_short_name in self.spells:
                self.print(1, f"Spell '{spell_short_name}' does not exist.")
                return
            
            spell_list.append(self.spells[spell_short_name])

        command = ' '.join(args[index + 1:])
        try:
            damages_parameters = DamageParameters.from_string(command, self._get_default_parameters())
        except ValueError as e:
            self.print(1, f'Cannot parse parameters: {str(e)}')
            return

        total_stats = damages_parameters.get_total_stats(self.stats)

        spell_chain = SpellChains()
        for spell in spell_list:
            spell_chain.add_spell(spell)

        permutation = list(range(len(spell_list)))  # Permutation of all specified spells in the specified order
        computation_data = spell_chain._get_detailed_damages_of_permutation(permutation, total_stats, damages_parameters)

        self.print(0, f"Damages of the given combination (parameters : '{self.default_parameters}' ; total PA : {sum(spell.get_pa() for spell in spell_list)} ; initial states: ({','.join(sorted(damages_parameters.starting_states))})) is:\n")
        self.print(0, f" => {computation_data.average_damages:.0f} dmg : {computation_data.damages['min']} - {computation_data.damages['max']} ({computation_data.damages['crit_min']} - {computation_data.damages['crit_max']})")


    def execute_command(self, command: str):
        instr, *args = command.split(' ')

        if instr in Manager.GENERAL_INSTRUCTIONS:
            self._execute_general_command(instr, args)
            return

        elif instr in Manager.PARAMETERS_INSTRUCTION:
            self._execute_parameters_command(instr, args)
            return

        elif instr in Manager.STATS_INSTRUCTION:
            self._execute_stats_command(args)
            return

        elif instr in Manager.SPELL_INSTRUCTION:
            self._execute_spell_command(args)
            return

        elif instr in Manager.SPELL_SET_INSTRUCTION:
            self._execute_spell_set_command(args)
            return

        elif instr in Manager.DAMAGES_INSTRUCTION:
            if instr == 'dmgc':
                self._execute_damages_combination_command(args)
            else:
                self._execute_damages_command(args, simple=(instr=='dmgs'))
            return

        self.print(1, f"Unknown command instruction: '{instr}'.")
