import os
import json

SPELL_DIR = 'spells\\'

def update_stats(stats):
    chars = [0 for _ in range(5)]
    dmgs = [0 for _ in range(14)]
    for char in stats['characteristics']:
        chars[int(char)] = stats['characteristics'][char]
    for dmg in stats['damages']:
        dmgs[int(dmg)] = stats['damages'][dmg]

    stats['characteristics'] = chars
    stats['damages'] = dmgs

    return stats

spells = []
for file in os.listdir(SPELL_DIR):
    spells.append(SPELL_DIR + file)
    continue
    if 'ether' in file:
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
    for buff in spell['buffs']:
        bdmg = [0] * 5
        add_dmg_char = []
        for char in buff['base_damages']:
            if buff['base_damages'][char] > 0:
                add_dmg_char.append(int(char))
            bdmg[int(char)] = buff['base_damages'][char]
        buff['base_damages'] = bdmg
        for spellname in buff['stats']:
            buff['stats'][spellname] = update_stats(buff['stats'][spellname])
        if not 'additional_damaging_characteristics' in buff:
            buff['additional_damaging_characteristics'] = add_dmg_char
    with open(SPELL_DIR + file, 'w') as fo:
        json.dump(spell, fo)

print(str(spells).replace("'", '"'))
exit()
STATS_DIR = 'stats\\'

for file in os.listdir(STATS_DIR):
    with open(STATS_DIR + file, 'r', encoding='utf-8') as fi:
        stats = json.load(fi)
    stats = update_stats(stats)
    with open(STATS_DIR + file, 'w') as fo:
        json.dump(stats, fo)
