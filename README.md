# Dofus Damage Optimizer

This program is designed to help determine to best combinations of spells to use in each turn in the [Dofus MMORPG](https://www.dofus.com/en).

It can handle multiple stats pages, spells and spell sets, as well as multiple conditions for the damage computations, in order to give the most freedom possible.

It runs on a Python 3 console (developed on 3.9.10, probably work for older versions) and does not require any external package. However, if the [tqdm](https://pypi.org/project/tqdm/) package is installed, it will be used for some progress bars. To run it, just use `python main.py` in the folder containing the python files.

## "Stuff" TODO

- commande pour optimiser les sorts avec un équipement donné
- commande pour maximiser une caractéristique donnée (stuff entier ou un seul équipement)
- correction bug si on a déjà un equipement complet
- ajouter commande pour calculer dégats equipement
- afficher les stats après optimisation stuff

possibilité d'ajouter des stats de départ à chaque fois

## General principle

This optimizer works by creating spells, stats page, spell sets and parameters set and then picking the desired one to determine the best possible combination of spells to maximize the damages dealt.

A spell contains informations about its damages, number of uses and AP cost, a stats page contains every useful stats needed to compute damages, a spell set is (as suggested by the name) a collection of spells and a parameters set contains informations about the computation like maximum number of AP to use, resistances of the enemy or its distance.

A spell also contains "buffs", which are events triggered in certain conditions that can affect the spells coming next in the computation. They are used when spells interact each other, or when one increase damages of the following.

Every computation need to use a spell set and a parameters set (which eventually contains stats pages).

## Commands

Every `<name>` parameter in the commands below should not contains spaces and is unique for each type of commands.

## Spell section

### General

 - `s` : save everything (automatically done after most actions)
 - `i` : get informations on current state (TODO)
 - `cache` : get informations on the cache
 - `q` : quit

### Parameters-related

Every `param` can be replaced with only `p`.

 - `param new <name>` : create a new parameters set, based on the current one
 - `param change <name>` : change the current parameters set to the specified one
 - `param [[<parameter> <value>] ...]` : update the current parameters set with the specified parameters (the parameters are described in the "Parameters" section)
 - `param ls` : list all the currently available parameters set
 - `param show [name]` : show more details on the specified parameters set (if none is supplied, use the currently selected one)

### Stats-related

 - `st new <name>` : create a new stats page and prompt the user for all the required informations
 - `st rm <name> ` : delete a stats page
 - `st mod <name>` : modify a stats page (prompt the user for all the changes)
 - `st ls` : list all the currently available stats pages
 - `st show <name>` : show more details on the specified stats pages
 - `st addfile <name>` : create a stats page from a file whose path is `stats\\{name}.json`
 - `st copy <source_name> <target_name>` : copy the source stats page into a new page

### Spells-related

 - `sp new <name>` : create a new spell and prompt the user for all the required informations
 - `sp rm <name>` : delete a spell
 - `sp mod <name>` : modify a spell (prompt the user for all the changes)
 - `sp ls` : list all the currently available spells
 - `sp show <name>` : show more details on the specified spell
 - `sp buffs <name>` : show every buff of the specified spell in details
 - `sp dmg|d <spell_name> [[<parameter> <value>] ...]` : compute and show the detailed damages of a spell (the parameters are described in the "Parameters" section)
 - `sp addfile <name>` : create a spell from a file whose path is `spells\\{name}.json`

### Spell sets-related

 - `ss new <name>` : create a new spell set
 - `ss rm <name> ` : delete a spell set
 - `ss add <spell_set_name> <spell_name> [<spell_name> ...]` : add the specified spell(s) to the spell set
 - `ss del <spell_set_name> <spell_name>` : remove the specified spell from the spell set
 - `ss ls` : lists all the currently available spell sets
 - `ss show <name>` : shows more details on the specified spell set
 - `ss copy <source_name> <target_name>` : copy the source spell set with the new specified name

### Damage-related

 - `dmg <spell_set_name> [[<param> <value>] ...]` : return the best combination of spells for the given constraints (the parameters are described in the "Parameters" section) ;
 - `dmgs <spell_set_name> [[<param> <value>] ...]` : return the best combination of spells using the simple method which does not use the interactions between spells ;
 - `dmgc <spell1> <spell2> ... [[<param> <value>] ...]` : return the damages of the specified combination of spells in the specified order.

## Stuff section

### Equipment-related

 - `equip new <name>` : create a new equipment
 - `equip rm <name> ` : delete a equipment
 - `equip add <equipment_name> <item_id> [<item_id> ...]` : add the specified item(s) to the equipment
 - `equip del <equipment_name> <item_id> [<item_id> ...]` : remove the specified item(s) from the equipment
 - `equip ls` : lists all the currently available equipments
 - `equip show <name>` : shows more details on the specified equipment
 - `equip copy <source_name> <target_name>` : copy the source equipment with the new specified name

### Item-related

 - `search <search_phrase>` : print the type and id of items whose name contains the search phrase
 - `item <item_id> [mode]` : print the stats of the given item id, with the mode being 'max', 'min' or 'ave' (default: 'max')

### Equipment type

All equipments have a unique type in the list :
 - `hat`: for hats
 - `amulet`: for amulets
 - `cloak`: for cloaks
 - `ring`: for rings (two will be chosen when optimized)
 - `weapon`: for every kind of weapon
 - `shield`: for shields
 - `belt`: for belts
 - `boots`: for boots
 - `pet`: for pets, petsmounts and mounts
 - `dofus`: for dofus and trophies (6 will be chosen when optimized)

## Parameters

The possible parameters for every command that requires it are :
 - `-s` (or `-stats`) followed by as many stats page short name as wanted : the stats page to use for the computations (if one starts with a `!`, it will remove this page) ;
 - `-pa` followed by a positive integer : the maximum number of AP (*action point*) to use ;
 - `-po` followed by a non negative integer : the exact range to the enemy ;
 - `-pomin` (or `-minpo`) followed by a non negative integer : the minimum range to the enemy ;
 - `-pomax` (or `-maxpo`) followed by a non negative integer : the maximum range to the enemy (note that maximum should be >= minimum) ;
 - `-t` (or `-type`) followed by one of `mono`, `multi`, `versa` : indicates if the computation takes into account the number of uses per target ('mono'), the number of uses per turn ('multi') or only one time each spell ('versa') ;
 - `-r` (or `-res`, `-resistances`) followed by five integers (may be negative) : indicates the resistances of the enemy to each element (in order : NEUTRAL, EARTH, FIRE, WATER, AIR) ;
 - `-d` (or `-distance`) followed by one of `melee`, `range` : indicates if the damage computations should take into account RANGE or MELEE damages ;
 - `-v` (or `-vulne`, `-vulnerability`) followed by one integer (may be negative) : indicate the bonus (or reduced) damages dealt because of vulnerability or damage reduction (independant from resistances) ;
 - `-bdmg` (or `-bdamages`, `-base-damages`) followed by five integers (may be negative) : bonus (or malus) base damages of each element (in order : NEUTRAL, EARTH, FIRE, WATER, AIR) of the spell ;
 - `-states` (or `-state`) followed by as many states as wanted : the starting states used for the computations (only used in a damage command) ;
 - `-critres` (or `-rc`) followed by an integer (may be negative) : the critical resistance of the target.

The following additional parameters are only used for the stuff section :
 - `-lvl` (or `-level`) followed by an integer between 1 and 200 : the exact level of items ;
 - `-lvlmin` (or `-levelmin`, `-minlvl`, `-minlevel`) followed by an integer between 1 and 200 : the minimum level of items ;
 - `-lvlmax` (or `-levelmax`, `-maxlvl`, `-maxlevel`) followed by an integer between 1 and 200 : the maximum level of items ;
 - `-stuff` followed by one or more of the stuff types (or 'all') : indicate what equipment to optimize (if one starts with a `!`, it means to not chose this type) ;
 - `-stuffmode` (or `-mode`) followed by one of `min`, `max`, `ave` : what type of stats to consider on every item (respectively the maximum possible, the minimum possible or the average of the two) ;
 - `-e` (or `-equip`) followed by one equipment name : the equipment already chosen before the optimization.

## Examples of damages computation

Setting default parameters:
```
>>> param -s base -pa 11 -pomin 1 -pomax 10 -t mono
Default parameters successfully set.
```

Simple damages optimisation (`all` is the name of the spell set):
```
>>> dmg all
Maximum average damages ('base' ; PA = 11 ; PO = 1 - 10 ; type = mono ; position = unspecified ; distance = range) is:

 => 1697 dmg : 1577 - 1714 (1768 - 1906)

Using, in this order:
 - Ouragan
 - Drain Elémentaire
 - Ether
 - Lame Astrale

189924 possible combinations, 1 with the same damages, including:
 - Ouragan, Drain Elémentaire, Lame Astrale, Ether
```

With parameters:
```
>>> dmg all -po 8 -t multi
Maximum average damages ('base' ; PA = 11 ; PO = 8 - 8 ; type = multi ; position = unspecified ; distance = range) is:

 => 1275 dmg : 1189 - 1278 (1327 - 1416)

Using, in this order:
 - Lame Astrale
 - Orage
 - Lame Astrale

2720 possible combinations, 1 with the same damages, including:
 - Orage, Lame Astrale, Lame Astrale
```

With an additional stats page:
```
>>> dmg all -po 8 -t versa -s turquoise
Maximum average damages ('base' ; PA = 11 ; PO = 8 - 8 ; type = versa ; position = unspecified ; distance = range) is:

 => 1292 dmg : 1184 - 1286 (1325 - 1429)

Using, in this order:
 - Comète
 - Orage
 - Lame Astrale

700 possible combinations, 1 with the same damages, including:
 - Orage, Comète, Lame Astrale
```

Calculating only one spell damages:
```
>>> sp d tison
Damages of the spell 'Tison' (parameters set : 'base' ; distance: range ; initial states: ()):

Individual characteristics:
 - INTELLIGENCE: 144 - 160 (171 - 185)
 - AGILITY: 384 - 430 (449 - 495)

Total damages:   528 - 590 (620 - 680)
Average damages: 559 (650) => 575 with 18 % crit chance
```

Calculating damages of a specific combination of spells (with starting states):
```
>>> dmgc tribut ether -states h:w
Damages of the given combination (parameters : 'base' ; total PA : 4 ; initial states: (h:w)) is:

 => 393 dmg : 371 - 397 (418 - 445)
```

## TODO

 - Spell buffs can increase damage field by field ('min', 'max', 'crit_min', 'crit_max') instead of one flat value
 - `i` command
