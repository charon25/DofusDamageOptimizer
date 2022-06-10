# Characteristics
CHARACTERISTICS_COUNT = 5

STRENGTH = 0
INTELLIGENCE = 1
LUCK = 2
AGILITY = 3
NEUTRAL = 4

CHARACTERISTICS_NAMES = [
    "STRENGTH",
    "INTELLIGENCE",
    "LUCK",
    "AGILITY",
    "NEUTRAL"
]

CHARACTERISTICS_ID = {
    'strength': 0,
    'str': 0,
    'intelligence': 1,
    'int': 1,
    'luck': 2,
    'agility': 3,
    'agi': 3,
    'neutral': 4
}

# Damages
DAMAGES_COUNT = 14

POWER = 0
BASIC = 1
CRIT = 2
EARTH = 3
FIRE = 4
WATER = 5
AIR = 6
D_NEUTRAL = 7
SPELL = 8
WEAPON = 9
WEAPON_POWER = 10
RANGE = 11
MELEE = 12
FINAL = 13

DAMAGES_NAMES = [
    "POWER",
    "BASIC",
    "CRIT",
    "EARTH",
    "FIRE",
    "WATER",
    "AIR",
    "NEUTRAL",
    "SPELL",
    "WEAPON",
    "WEAPON_POWER",
    "RANGE",
    "MELEE",
    "FINAL"
]

DAMAGES_ID = {
    'power': 0,
    'basic': 1,
    'critdmg': 2,
    'earthdmg': 3,
    'strdmg': 3,
    'firedmg': 4,
    'intdmg': 4,
    'waterdmg': 5,
    'luckdmg': 5,
    'airdmg': 6,
    'agidmg': 6,
    'neutraldmg': 7,
    'spelldmg': 8,
    'weapondmg': 9,
    'weaponpower': 10,
    'rangedmg': 11,
    'meleedmg': 12,
    'finaldmg': 13
}


# Other
OTHER_STATS_COUNT = 28

OTHER_STATS_NAME = [
    'air res',
    'ap',
    'ap parry',
    'ap reduction',
    'crit res',
    'dodge',
    'earth res',
    'fire res',
    'heal',
    'health',
    'init',
    'lock',
    'melee res',
    'mp',
    'mp parry',
    'mp reduction',
    'neutral res',
    'pods',
    'prospec',
    'pushback dmg',
    'pushback res',
    'range',
    'range res',
    'reflect',
    'summon',
    'trap dmg',
    'water res',
    'wisdom',
]


ALL_STATS_NAME = [
    'strength',
    'intelligence',
    'luck',
    'agility',
] + [
    'power',
    'basic',
    'critdmg',
    'earthdmg',
    'firedmg',
    'waterdmg',
    'airdmg',
    'neutraldmg',
    'spelldmg',
    'weapondmg',
    'weaponpower',
    'rangedmg',
    'meleedmg',
    'finaldmg'
] + OTHER_STATS_NAME
