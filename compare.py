#!/usr/bin/env python
from lib.bracket import Bracket, BracketType
import toml

# The paths to the perfect bitstring configuration files for men and women.
men_path = 'lib/data/men/results.toml'
women_path = 'lib/data/women/results.toml'

def compareBrackets(bitstring: str, bracket_type: BracketType) -> (int, list):
    # Compares a bitstring for a generated bracket to a perfect bitstring
    # The perfect bitstring is stored in men_path or women_path
    # Returns a tuple (score, numCorrectByRound), where score is the bracket score
    # and numCorrectByRound is the number of games that were correct in the bitstring for each round.
    t = toml.load(men_path if bracket_type == BracketType.MEN else women_path)
    perfect_bitstring = t['bitstring']
    current_round = t['round']
    current_idx = 0
    # The score value of a correct game in each round
    # Doubles for each sequential round
    value = 10
    totalScore = 0
    gamesCorrectList = [0] * 6

    for rnd in range(current_round):
        # Calculates the number of games in the round
        for _ in range(2**(5 - rnd)):
            if bitstring[current_idx] == perfect_bitstring[current_idx]:
                gamesCorrectList[rnd] += 1
                totalScore += value
            current_idx += 1
        value *= 2

    return totalScore, gamesCorrectList