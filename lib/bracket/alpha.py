#!/usr/bin/env python
import os, toml
from .round import Rounds
from .team import Team

class Alpha:
    '''
    Stores the alpha values for each round in memory.
    '''
    def __init__(self, path):
        '''
        Constructs an Alpha object to look up alpha values by round.

        Parameters
        ----------
        path (str) : a file path pointing to the correct alpha.toml file.
        '''
        t = toml.load(path)
        self.default_alphas = { int(rnd) : float(alpha) for rnd, alpha in t['default_alpha'].items() }
        self.r1_alphas = { int(lower_seed) : float(alpha) for lower_seed, alpha in t['r1_alpha'].items() }
    
    def get_alpha(self, rnd: Rounds, s1: int=None, s2: int=None) -> float:
        '''
        Returns the default alpha value for a particular round.
        Raises a KeyError if an invalid rnd argument is provided.

        Parameters
        ----------
        rnd (Rounds) : the round enum value.
        s1 (int) : the seed of t1 in a match pairing.
        s2 (int) : the seed of t2 in a match pairing.
        '''
        if rnd == Rounds.ROUND_OF_64:
            return self.r1_alphas[min(s1, s2)]
        else:
            return self.default_alphas[rnd.value]