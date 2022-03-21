from typing import List

from spell import Spell
from stats import Stats

def _dp_knapsack(weights: List[int], values: List[int], W):
    N = len(weights)
    weights.insert(0, -1)
    values.insert(0, -1)

    T = [[0 for _ in range(W + 1)] for _ in range(N + 1)]

    for i in range(1, N + 1):
        for c in range(1, W + 1):
            if c >= weights[i]:
                T[i][c] = max(T[i - 1][c], T[i - 1][c - weights[i]] + values[i])
            else:
                T[i][c] = T[i - 1][c]

    i, c = N, W
    indexes = []
    while T[i][c] != 0:
        if T[i-1][c] < T[i][c]:
            indexes.append(i - 1)
            c -= weights[i]
        i -= 1
    
    indexes.sort()
    return (indexes, T[N][W])


def get_best_combination(spell_list: List[Spell], stats: Stats, max_used_pa):
    weights = [spell.get_pa() for spell in spell_list]
    values = [spell.get_average_damages(stats) for spell in spell_list]

    indexes, max_damages = _dp_knapsack(weights, values, max_used_pa)

    return ((spell_list[index] for index in indexes), max_damages)
