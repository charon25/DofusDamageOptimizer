import os
import json

SPELL_DIR = 'spells\\'

for file in os.listdir(SPELL_DIR):
    if file != 'deflag.json':
        continue
    with open(SPELL_DIR + file, 'r', encoding='utf-8') as fi:
        spell = json.load(fi)
    
    spell['position'] = 'all'
    base_damages = [None for _ in range(5)]
    dmg_char = []
    for char in spell['base_damages']:
        if any(spell['base_damages'][char][field] > 0 for field in spell['base_damages'][char]):
            dmg_char.append(int(char))
        base_damages[int(char)] = spell['base_damages'][char]
    spell['base_damages'] = base_damages
    spell['damaging_characteristics'] = dmg_char
    if not 'buffs' in spell:
        spell['buffs'] = []
    with open(SPELL_DIR + file, 'w') as fo:
        json.dump(spell, fo)

STATS_DIR = 'stats\\'

for file in os.listdir(STATS_DIR):
    if file != 'test.json':
        continue
    with open(STATS_DIR + file, 'r', encoding='utf-8') as fi:
        stats = json.load(fi)
    
    chars = [0 for _ in range(5)]
    dmgs = [0 for _ in range(14)]
    for char in stats['characteristics']:
        chars[int(char)] = stats['characteristics'][char]
    for dmg in stats['damages']:
        dmgs[int(dmg)] = stats['damages'][dmg]

    stats['characteristics'] = chars
    stats['damages'] = dmgs
    with open(STATS_DIR + file, 'w') as fo:
        json.dump(stats, fo)
