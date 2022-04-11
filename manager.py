import distutils.util
import json
import os
from typing import Any, Callable, Dict, List

from knapsack import get_best_combination
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
        self.stats: Dict[str, Stats] = dict()
        self.spells: Dict[str, Spell] = dict()
        self.spell_sets: Dict[str, SpellSet] = dict()
        self.default_params = dict()

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
                except (FileNotFoundError, KeyError, TypeError, ValueError):
                    self.print(1, f"Could not open or read stats page '{stats_filepath}'.")

            # SPELLS
            for spells_filepath in json_data['spells']:
                try:
                    spell = Spell.from_file(spells_filepath)
                    self.spells[spell.get_short_name()] = spell
                except (FileNotFoundError, KeyError, TypeError, ValueError):
                    self.print(1, f"Could not open or read spell '{spells_filepath}'.")

            # SPELL SETS
            for spell_set_data in json_data['spell_sets']:
                try:
                    spell_set = SpellSet()
                    for spell_short_name in spell_set_data['spells']:
                        try:
                            spell_set.add_spell(self.spells[spell_short_name])
                        except KeyError:
                            self.print(1, f"Cannot add spell '{spell_short_name}' to spell set '{spell_set_data['short_name']}' : it does not exist.")

                    spell_set.set_name(spell_set_data['name'])
                    spell_set.set_short_name(spell_set_data['short_name'])
                    self.spell_sets[spell_set.get_short_name()] = spell_set
                except KeyError:
                    self.print(1, f"Could not load spell set '{spell_set_data['name']}'.")

            # DEFAULT PARAMS
            self.default_params = json_data['default_params']
            self.default_params['pa'] = int(self.default_params['pa'])
            self.default_params['pomin'] = int(self.default_params['pomin'])
            self.default_params['pomax'] = int(self.default_params['pomax'])
            if not self.default_params['t'] in ('mono', 'multi', 'versa'):
                raise TypeError

        except (FileNotFoundError, KeyError, TypeError):
            self.print(1, "'manager.json' file does not exist or is innaccessible, using default load.")
            self._load_default()
            return


    def save(self, print_message=True):
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

        json_valid_data = {
            'stats': stats_filepaths,
            'spells': spells_filepaths,
            'spell_sets': spell_sets,
            'default_params': self.default_params
        }

        with open('manager.json', 'w', encoding='utf-8') as fo:
            json.dump(json_valid_data, fo)

        if print_message:
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
            except ValueError:
                self.print(1, 'Default value for PA should be an int.')
                return
            if value <= 0:
                self.print(1, 'Default value for PA should be positive.')
                return
            self.default_params[param] = value
            self.print(0, f"Default PA count successfully set to '{value}'.")

        elif param in ('pomin', 'po_min', 'minpo', 'min_po'):
            try:
                value = int(value)
            except ValueError:
                self.print(1, 'Default value for minimum PO should be an int.')
                return
            if value < 0 or value > self.default_params['pomax']:
                self.print(1, 'Default value for minimum PO should be non-negative and smaller or equal to maximum PO.')
                return
            self.default_params[param] = value
            self.print(0, f"Default minimum PO successfully set to '{value}'.")

        elif param in ('pomax', 'po_max', 'maxpo', 'max_po'):
            try:
                value = int(value)
            except ValueError:
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


    def _create_stats(self, stats: Stats = None) -> Stats:
        if stats is None:
            stats = Stats()

        name = input(f'Stats page name {f"({stats.get_name()}) " if stats.get_name() != "" else ""}: ')
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
                self.print(0, f"Page '{stats.get_name()}' ({stats.get_short_name()})")

        elif command_action == 'show':
            if len(args) < 2:
                self.print(1, 'Missing stats page short name.')
                return

            short_name = args[1]

            if short_name in self.stats:
                stats = self.stats[short_name]
                printed_string = [f"===== Page '{stats.get_name()}' ({short_name})", '=== Characteristics\n']
                for characteristic in Characteristics:
                    if characteristic == Characteristics.NEUTRAL:
                        continue
                    printed_string.append(f"{characteristic.name:.<15}{stats.get_characteristic(characteristic)}")

                printed_string.append('\n=== Damages\n')
                for damage in Damages:
                    printed_string.append(f"{damage.name:.<15}{stats.get_damage(damage)}")

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
        else:
            self.print(1, f"Unknown action '{command_action}' for stats commands.")

    def _create_spell(self, spell: Spell = None) -> Spell:
        if spell is None:
            spell = Spell()

        name = input(f'Spell name {f"({spell.get_name()}) " if spell.get_name() != "" else ""}: ')
        if name:
            spell.set_name(name)

        is_melee = input(f'Melee ({spell.is_melee}) (0/1) : ')
        if is_melee:
            spell.set_melee(distutils.util.strtobool(is_melee))

        self.print(0, '\n=== Base damages\n')
        for characteristic in Characteristics:
            unused_characteristic = False
            self.print(0, f'{characteristic.name} : ')
            base_damages = spell.get_base_damages(characteristic)

            for field in ('min', 'max', 'crit_min', 'crit_max'):
                value = input(f'  - {field.replace("_", " ").capitalize()} ({base_damages[field]}) : ')
                if value == '/':
                    unused_characteristic = True
                    break
                if value:
                    base_damages[field] = int(value)

            if not unused_characteristic:
                spell.set_base_damages(characteristic, base_damages)

        self.print(0, '')
        pa = input(f'PA count ({spell.get_pa()}) : ')
        if pa:
            spell.set_pa(int(pa))

        self.print(0, '')
        crit_chance = input(f'Crit chance % ({100 * spell.get_crit_chance():.1f} %) : ')
        if crit_chance:
            spell.set_crit_chance(float(crit_chance) / 100)

        self.print(0, '')
        uses_per_target = input(f'Uses per target ({spell.get_uses_per_target()}) : ')
        if uses_per_target:
            spell.set_uses_per_target(int(uses_per_target))

        uses_per_turn = input(f'Uses per turn ({spell.get_uses_per_turn()}) : ')
        if uses_per_turn:
            spell.set_uses_per_turn(int(uses_per_turn))

        self.print(0, '')
        min_po = input(f'Minimum PO ({spell.get_min_po()}) : ')
        min_po = int(min_po) if min_po else None
        max_po = input(f'Maximum PO ({spell.get_max_po()}) : ')
        max_po = int(max_po) if min_po else None

        spell.set_po(min_po=min_po, max_po=max_po)

        return spell


    def _execute_spell_command(self, args: List[str]):
        if len(args) == 0:
            self.print(1, 'Action missing in the command.')
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

            if short_name in self.spells:
                spell = self.spells[short_name]
                printed_string = [f"===== Spell '{spell.get_name()}' ({short_name})", '=== Spell characteristics']

                printed_string.append(f"PA : {spell.get_pa()}")
                printed_string.append(f"PO : {spell.get_min_po()} - {spell.get_max_po()}")
                printed_string.append(f"Uses per target : {spell.get_uses_per_target() if spell.get_uses_per_target() > 0 else '∞'}")
                printed_string.append(f"Uses per turn : {spell.get_uses_per_turn() if spell.get_uses_per_turn() > 0 else '∞'}")
                printed_string.append(f'Crit chance : {100 * spell.get_crit_chance():.1f} %')

                printed_string.append("\n=== Base damages\n")
                for characteristic in Characteristics:
                    base_damages = spell.get_base_damages(characteristic)
                    if all(value == 0 for value in base_damages.values()):
                        continue

                    printed_string.append(f" {characteristic.name} : {base_damages['min']} - {base_damages['max']} ({base_damages['crit_min']} - {base_damages['crit_max']})")

                self.print(0, '\n'.join(printed_string))
            else:
                self.print(1, f"Spell '{short_name}' does not exist.")


        elif command_action == 'mod':
            if len(args) < 2:
                self.print(1, 'Missing spell short name.')
                return

            short_name = args[1]

            if short_name in self.spells:
                try:
                    self.spells[short_name] = self._create_spell(self.spells[short_name])
                except:
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
        else:
            self.print(1, f"Unknown action '{command_action}' for spell commands.")

    def _execute_spell_set_command(self, args: List[str]):
        if len(args) == 0:
            self.print(1, 'Action missing in the command.')
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
                spell_set.set_name(input("Spell set name : ") or short_name)
            except KeyboardInterrupt:
                self.print(0, '\nCancelled spell set creation.')
                return

            self.spell_sets[short_name] = spell_set
            self.save(False)
            self.print(0, f"Spell set '{short_name}' successfully created!")

        elif command_action == 'ls':
            self.print(0, '=== Spell sets\n')
            for spell_set in sorted(self.spell_sets.values(), key=lambda spell_set: spell_set.get_name()):
                self.print(0, f" - '{spell_set.get_name()}' ({spell_set.get_short_name()}) : {len(spell_set)} spell{'s' if len(spell_set) > 1 else ''}")

        elif command_action == 'show':
            if len(args) < 2:
                self.print(1, 'Missing spell set short name.')
                return

            short_name = args[1]

            if short_name in self.spell_sets:
                spell_set = self.spell_sets[short_name]
                printed_string = [f"===== Spell set '{spell_set.get_name()}' ({short_name})"]

                printed_string.append("Spells : ")

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
            spell_short_name = args[2]

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

        else:
            self.print(1, f"Unknown action '{command_action}' for spell commands.")


    def _execute_damages_command(self, args: List[str]):
        if len(args) < 2:
            self.print(1, 'Missing spell set or stats page.')
            return

        spell_set_short_name = args[0]
        stats_short_name = args[1]

        if not spell_set_short_name in self.spell_sets or not stats_short_name in self.stats:
            self.print(1, f"Spell set '{spell_set_short_name}' or stats page '{stats_short_name}' do not exist.")
            return

        spell_set = self.spell_sets[spell_set_short_name]
        stats = self.stats[stats_short_name]

        pa = self.default_params['pa']
        min_po = self.default_params['pomin']
        max_po = self.default_params['pomax']
        po = None
        resistances = {characteristic: 0 for characteristic in Characteristics}
        list_type = self.default_params['t']
        additional_stats = list()

        try:
            index = 2
            while index < len(args):
                param = args[index]
                if param == 'pa':
                    value = int(args[index + 1])
                    index += 2
                    if value <= 0:
                        raise ValueError
                    pa = value
                elif param in ('pomin', 'po_min', 'minpo', 'min_po'):
                    value = int(args[index + 1])
                    index += 2
                    if value < 0:
                        raise ValueError
                    min_po = value
                elif param in ('pomax', 'po_max', 'maxpo', 'max_po'):
                    value = int(args[index + 1])
                    index += 2
                    if value < 0:
                        raise ValueError
                    max_po = value
                elif param == 'po':
                    value = int(args[index + 1])
                    index += 2
                    if value < 0:
                        raise ValueError
                    po = value
                elif param == 't':
                    value = args[index + 1]
                    index += 2
                    if not value in ('mono', 'multi', 'versa'):
                        raise ValueError
                    list_type = value
                elif param in ('r', 'res'):
                    values = args[index + 1:index + 6] # 5 values
                    if len(values) < 5:
                        raise ValueError
                    index += 6
                    for k, value in enumerate(values):
                        # Reorder from STRENGTH/INTELLIGENCE/LUCK/AGILITY/NEUTRAL to NEUTRAL/STRENGTH/INTELLIGENCE/LUCK/AGILITY
                        characteristic_key = str(k - 1) if k > 0 else '4' 
                        resistances[Characteristics(characteristic_key)] = int(value)
                elif param in ('s', 'st', 'stats'):
                    values = args[index + 1:]
                    for value in values:
                        if not value in self.stats:
                            self.print(0, f"[WARNING] Unknown additional stats page : '{value}'.")
                        else:
                            additional_stats.append(self.stats[value])
                    break # Must be the last argument
                else:
                    self.print(0, f"[WARNING] Unknown parameter : '{param}'.")
                    index += 1
        except ValueError:
            self.print(1, "Error while parsing damage command.")
            return
        if po is not None:
            min_po = po
            max_po = po

        if min_po > max_po:
            self.print(1, "Error while parsing damage command.")
            return

        spell_list = list()
        if list_type == 'mono':
            spell_list = spell_set.get_spell_list_single_target(max_used_pa=pa, min_po=min_po, max_po=max_po)
        elif list_type == 'multi':
            spell_list = spell_set.get_spell_list_multiple_targets(max_used_pa=pa, min_po=min_po, max_po=max_po)
        elif list_type == 'versa':
            spell_list = spell_set.get_spell_list_versatile(max_used_pa=pa, min_po=min_po, max_po=max_po)

        stats = sum([stats] + additional_stats)

        best_spells, max_damage = get_best_combination(spell_list, stats, pa, resistances)

        best_spells.sort(key=lambda spell:spell.get_pa(), reverse=True)

        self.print(0, f"Maximum average damages (PA = {pa} ; PO = {min_po} - {max_po} ; type = {list_type}) is : {int(max_damage):.0f}\n")
        self.print(0, 'Using : ')
        for spell in best_spells:
            self.print(0, f" - {spell.get_name()} ({int(spell.get_average_damages(stats, resistances)):.0f} dmg)")


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
