# Dofus Damage Optimizer

This program is designed to help determine to best combinations of spells to use in each turn in the [Dofus MMORPG](https://www.dofus.com/en).

It can handle multiple stats pages, spells and spell sets, as well as multiple conditions for the damage computations, in order to give the most freedom possible.

It runs on a Python 3 console (developed on 3.9.10, probably work for older versions) and does not require any external package. So to run it, just use `python main.py` in the python scripts folder.

## General principle

This optimizer works by creating spells, stats page, spell sets and parameters set and then picking the desired one to determine the best possible combination of spells to maximize the damages dealt.

A spell contains informations about its damages, number of uses and AP cost, a stats page contains every useful stats needed to compute damages, a spell set is (as suggested by the name) a collection of spells and a parameters set contains informations about the computation like maximum number of AP to use, resistances of the enemy or its distance.

Every computation need to use a spell set and a parameters set (which eventually contains stats pages).

## Commands

Every `<name>` parameter in the commands below should not contains spaces and is unique for each type of commands.

### General

 - `s` : save everything (automatically done after most actions)
 - `i` : get informations on current state (TODO)
 - `h` : help
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

### Spells-related

 - `sp new <name>` : create a new spell and prompt the user for all the required informations
 - `sp rm <name> ` : delete a spell
 - `sp mod <name>` : modify a spell (prompt the user for all the changes)
 - `sp ls` : list all the currently available spells
 - `sp show <name>` : show more details on the specified spell
 - `sp buffs <name>` : show every buff of the specified spell in details
 - `sp dmg|d <spell_name> [[<parameter> <value>] ...]` : compute and show the detailed damages of a spell (the parameters are described in the "Parameters" section)

### Spell sets-related

 - `ss new <name>` : creates a new spell set
 - `ss rm <name> ` : deletes a spell set
 - `ss add <spell_set_name> <spell_name>` : add the specified spell to the spell set
 - `ss del <spell_set_name> <spell_name>` : remove the specified spell from the spell set
 - `ss ls` : lists all the currently available spell sets
 - `ss show <name>` : shows more details on the specified spell set

### Damage-related

The command to get the best combination of spells for given constraints is :
`dmg <spell_set_name> [[<param> <value>] ...]`
The parameters are described in the "Parameters" section.

## Parameters

The possible parameters for every command that requires it are :
 - `-s` (or `-stats`) followed by as many stats page short name as wanted : the stats page to use for the computations ;
 - `-pa` followed by a positive integer : the maximum number of AP (*action point*) to use ;
 - `-po` followed by a non negative integer : the exact range to the enemy ;
 - `-pomin` (or `-minpo`) followed by a non negative integer : the minimum range to the enemy ;
 - `-pomax` (or `-maxpo`) followed by a non negative integer : the maximum range to the enemy (note that maximum should be >= minimum) ;
 - `-t` (or `-type`) followed by one of `mono`, `multi`, `versa` : indicates if the computation takes into account the number of uses per target ('mono'), the number of uses per turn ('multi') or only one time each spell ('versa') ;
 - `-r` (or `-res`, `-resistances`) followed by five integers (may be negative) : indicates the resistances of the enemy to each element (in order : NEUTRAL, EARTH, FIRE, WATER, AIR) ;
 - `-d` (or `-distance`) followed by one of `melee`, `range` : indicates if the damage computations should take into account RANGE or MELEE damages ;
 - `-v` (or `-vulne`, `-vulnerability`) followed by one integer (may be negative) : indicate the bonus (or reduced) damages dealt because of vulnerability or damage reduction (independant from resistances) ;
 - `-bdmg` (or `-bdamages`, `-base-damages`) followed by five integers (may be negative) : bonus (or malus) base damages of each element (in order : NEUTRAL, EARTH, FIRE, WATER, AIR) of the spell.


## Examples of damages computation

Setting default parameters :
```
>>> def -s base -pa 11 -pomin 1 -pomax 10 -t mono
Default parameters successfully set.
```

Simple damages optimisation (`base` is the name of the spell set) :
```
>>> dmg base
Maximum average damages (PA = 11 ; PO = 1 - 10 ; type = mono) is : 1278

Using :
 - Ether (300 dmg)
 - Ether (300 dmg)
 - Morph (air) (408 dmg)
 - Ouragan (270 dmg)
```

With parameters :
```
>>> dmg base -po 8 -t multi
Maximum average damages (PA = 11 ; PO = 8 - 8 ; type = multi) is : 1287

Using :
 - Lame Astrale (439 dmg)
 - Lame Astrale (439 dmg)
 - Morph (air) (408 dmg)
```

With an additional stats page :
```
>>> dmg base -po 8 -t versa -s turquoise
Maximum average damages (PA = 11 ; PO = 8 - 8 ; type = versa) is : 1324

Using :
 - Comète (425 dmg)
 - Lame Astrale (464 dmg)
 - Morph (air) (433 dmg)
```

Calculating only one spell damages :
```
>>> sp d tison
Damages of the spell Tison:

Individual characteristics:
 - INTELLIGENCE: 102 - 115 (118 - 131)
 - AGILITY: 327 - 370 (380 - 423)

Total damages:   429 - 485 (498 - 554)
Average damages: 457 (526) => 468 with 16 % crit chance
```
