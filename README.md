# Dofus Damage Optimizer

This program is designed to help determine to best combinations of spells to use in each turn in the [Dofus MMORPG](https://www.dofus.com/en).

It can handle multiple stats pages, spells and spell sets, as well as multiple conditions for the damage computations, in order to give the most freedom possible.

It runs on a Python 3 console (developed on 3.9.10, probably work for older versions) and does not require any external package. So to run it, just use `python main.py` in the python scripts folder.

## Commands

Every `<name>` parameter in the commands below should not contains spaces and is unique for each type of commands.

### General

 - `s` : save everything (automatically done after most actions)
 - `i` : get informations on current state (TODO)
 - `def <param> <value>` : define default options for the damage computation, where `param` and `value` should respect :
   - `param = pa` and `value > 0`
   - `param = pomin` and `pomax >= value >= 0`
   - `param = pomax` and `value >= pomin >= 0`
   - `param = t` and `value = mono|multi|versa`
 - `h` : help
 - `q` : quit

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
 - `sp dmg|d <spell_name> <stats_page_name> [[<param> <value>] ...]` : compute and show the detailed damages of a spell with the specified stats page (the params are the `r` and `s` parameters defined in the Damage-related part)

### Spell sets-related

 - `ss new <name>` : creates a new spell set
 - `ss rm <name> ` : deletes a spell set
 - `ss add <spell_set_name> <spell_name>` : add the specified spell to the spell set
 - `ss del <spell_set_name> <spell_name>` : remove the specified spell from the spell set
 - `ss ls` : lists all the currently available spell sets
 - `ss show <name>` : shows more details on the specified spell set

### Damage-related

The command to get the best combination of spells for given constraints is : 
`dmg <spell_set_name> <stats_page_name> [[<param> <value>] ...]`
where the params can be : 
 - Those presented in the "General" section
 - `po <value>` which sets both minimum and maximum PO to the value
 - `r|res <neutral_res> <earth_res> <fire_res> <water_res> <air_res>` which sets ennemy resistances for damages computation
 - `s <add_stats_page1> <add_stats_page2>...` which adds additional stats page to the damages computation (simple addition between the same stats). Must be the **LAST** parameter, as everything following it will be considered as a stats page

## Examples of damages computation

```
>>> dmg base base
Maximum average damages (PA = 11 ; PO = 1 - 10 ; type = mono) is : 1278

Using :
 - Ether (300 dmg)
 - Ether (300 dmg)
 - Morph (air) (408 dmg)
 - Ouragan (270 dmg)
```
Here, there are both a spell set named `base` and a stats page named `base`.

With parameters :
```
>>> dmg base base po 8 t multi
Maximum average damages (PA = 11 ; PO = 8 - 8 ; type = multi) is : 1287

Using :
 - Lame Astrale (439 dmg)
 - Lame Astrale (439 dmg)
 - Morph (air) (408 dmg)
```

With an additional stats page :
```
>>> dmg base base po 8 t versa s turquoise
Maximum average damages (PA = 11 ; PO = 8 - 8 ; type = versa) is : 1324

Using :
 - Comète (425 dmg)
 - Lame Astrale (464 dmg)
 - Morph (air) (433 dmg)
```

Calculating only one spell damages :
```
>>> sp d tison base
Damages of the spell Tison:

Individual characteristics:
 - INTELLIGENCE: 102 - 115 (118 - 131)
 - AGILITY: 327 - 370 (380 - 423)

Total damages:   429 - 485 (498 - 554)
Average damages: 457 (526) => 468 with 16 % crit chance
```
