import json
import os
import re
from typing import List

from spell import Spell


class SpellSet:
    def __init__(self):
        self.spells: List[Spell] = []
        self.name = ''
        self.short_name = ''

    def add_spell(self, spell: Spell):
        self.spells.append(spell)

    def add_spell_from_file(self, spell_file):
        self.add_spell(Spell.from_file(spell_file))


    def get_spell_list_single_target(self, max_used_pa):
        spell_list: List[Spell] = []

        for spell in self.spells:
            uses = spell.get_max_uses_single_target(max_used_pa)
            spell_list.extend([self for _ in range(uses)])
        
        return spell_list

    def get_spell_list_multiple_target(self, max_used_pa):
        spell_list: List[Spell] = []

        for spell in self.spells:
            uses = spell.get_max_uses_multiple_targets(max_used_pa)
            spell_list.extend([self for _ in range(uses)])
        
        return spell_list

    def get_spell_list_versatile(self, max_used_pa):
        if not isinstance(max_used_pa, int):
            raise TypeError(f"Max used pa is not an int ('{max_used_pa}' of type '{type(max_used_pa)}' given instead).")
        
        if max_used_pa < 0:
            raise ValueError(f"Max used pa should be non negative ('{max_used_pa}' given instead).")

        return [spell for spell in self.spells if spell.get_pa() <= max_used_pa]


    def save_only_set_file(self, filepath, spell_filepaths):
        json_valid_data = {
            'spells': spell_filepaths,
            'name': self.name,
            'short_name': self.short_name
        }

        with open(filepath, 'w', encoding='utf-8') as fo:
            json.dump(json_valid_data, fo)

    def save_to_files(self, filepath, spell_dir: str=None):
        if spell_dir is None:
            spell_dir = os.path.dirname(filepath)

        if not spell_dir.endswith('\\'):
            spell_dir += '\\'

        spell_filepaths = []
        for spell in self.spells:
            spell_safe_filename = spell.get_safe_name() # replaces all non alphanumeric chars by an underscore
            spell_filepath = f'{spell_dir}{spell_safe_filename}.json'

            spell.save_to_file(spell_filepath)
            spell_filepaths.append(spell_filepath)

        self.save_only_set_file(filepath, spell_filepaths)


    def __len__(self):
        return len(self.spells)

    def __getitem__(self, indices):
        return self.spells[indices]

    def __iter__(self, indices):
        return iter(self.spells)

    def __contains__(self, spell):
        return spell in self.spells


    def get_name(self):
        return self.name

    def get_safe_name(self):
        return re.sub(r'\W', '_', self.name)

    def set_name(self, name):
        if len(str(name)) == 0:
            raise ValueError('Name cannnot be an empty string.')

        self.name = str(name)


    def get_short_name(self):
        return self.short_name

    def set_short_name(self, short_name):
        if len(str(short_name)) == 0:
            raise ValueError('Short name cannnot be an empty string.')

        self.short_name = str(short_name)


    @classmethod
    def check_json_validity(cls, json_data):
        for key in ('spells', 'name', 'short_name'):
            if not key in json_data:
                raise KeyError(f"JSON string does not contain a '{key}' key.")

        if not isinstance(json_data['spells'], list):
            raise TypeError(f"json_data['spells'] is not a list.")

    @classmethod
    def from_json_string(cls, json_string):
        json_data = json.loads(json_string)
        SpellSet.check_json_validity(json_data)

        spell_set = SpellSet()
        for spell_file in json_data['spells']:
            spell_set.add_spell_from_file(spell_file)

        spell_set.set_name(json_data['name'])
        spell_set.set_short_name(json_data['name'])

        return spell_set

    @classmethod
    def from_file(cls, filepath):
        if not (os.path.isfile(filepath) and os.access(filepath, os.R_OK)):
            raise FileNotFoundError(f"Cannot create spell set from file {filepath} : file not found or innaccessible.")

        with open(filepath, 'r', encoding='utf-8') as fi:
            json_string = fi.read()

        return SpellSet.from_json_string(json_string)
