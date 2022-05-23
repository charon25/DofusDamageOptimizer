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


class StuffManager:

    def __init__(self, print_method: Callable[[int, str], Any]) -> None:
        self.print: Callable[[int, str], Any] = print_method


    def execute_command(self, command: str):
        instr, *args = command.split(' ')
