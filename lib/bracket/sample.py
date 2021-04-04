#!/usr/bin/env python
import random
import numpy as np
from .round import Rounds
from .utils import sample_path, top, bottom
import toml
from math import ceil, log

class Sample:
    '''
    Initializes a callable Sample. Calling the sample yields a list of seeds that
    must win (and survive up to) the Sample round.

    Attributes
    ----------
    rnd (Rounds) : the round enum valyue for which the sampling function is used.
    pmf (int) : the Probability Mass Function for each seed reaching a given round.
    rng (np.random.Generator) : a random number generator.
    adjustments (dict) : a map of adjusted seeds onto a tuple with adjusted number of ocurrences and adjusted probability.
    '''
    def __init__(self, rnd: Rounds, adjustments: dict=None, seed: int=None):
        '''
        Constructs a Sample for a given round.

        Parameters
        ----------
        rnd (Rounds) : the round for which the Sample is used.
        '''
        self.rnd = rnd
        if seed:
            self.rng = np.random.default_rng(seed)
        else:
            self.rng = np.random.default_rng()
        self.adjustments = adjustments
        self.observed_counts = self.get_observed_counts()
        self.adjust_counts(self.adjustments)

    def __call__(self) -> list:
        '''
        Returns a list of 4 lists representing the sampled seeds for each region.
        '''
        pass

    def get_observed_counts(self) -> list:
        '''
        Reads in pmf data and returns a list with a pmf for a specific round.
        '''
        # extract all teams from the data file.
        t = toml.load(sample_path)

        # observed counts of appearances in the sample round for each seed.
        return { int(seed) : count for seed, count in t[str(self.rnd.value)].items() }

    def adjust_counts(self, adjustments: dict) -> None:
        '''
        Adjusts the expected counts.

        Parameters
        ----------
        adjustments (dict) : a map of seeds to adjust onto the new count.
        '''
        for seed, (new_count, _) in adjustments.items():
            self.observed_counts[seed] = new_count

    def get_psum(self, qhat: float) -> float:
        return (1 - (1 - qhat)**(len(self.observed_counts)))

    def sample_seed(self, qhat: float, max_val: int, fixed: int=None, support: list=list(range(1, 17))):
        # stage 1: adjustment sample
        if fixed:
            if random.random() < self.adjustments[fixed][1]:
                return fixed

        # stage 2: truncated geometric sampling.
        psum = self.get_psum(qhat)
        
        u = random.random() * psum
        sampled = int(ceil(log(u) / log(1 - qhat)))
        if max_val:
            return support[min(max_val, sampled) - 1]
        return support[sampled - 1]

class F4_A(Sample):
    '''
    Defines an F4_A sampling function. 

    Attributes
    ----------
    Sample
    '''
    def __init__(self, rng_seed: int=None):
        '''
        Constructs an F4_A Sample.

        Parameters
        ----------
        rng_seed (int) : a seed to use for the random number generator.
        '''
        self.name = 'f4a'
        t = toml.load(sample_path)
        adjustments = { int(seed) : (int(new_count), float(prob)) for seed, [new_count, prob] in t['F4_A'].items() }
        Sample.__init__(self, Rounds.FINAL_4, adjustments, rng_seed)

    def __call__(self):
        '''
        Returns a list of 4 sample seed lists (with one seed) for the Final Four.
        '''
        qhat = self.get_qhat()
        return [[self.sample_seed(qhat, 16, 11)] for _ in range(4)]

    def get_qhat(self) -> float:
        '''
        Calculates the qhat value for the F4_A function.
        '''
        q = 0
        for seed, count in self.observed_counts.items():
            q += (count * seed)
        q /= sum(self.observed_counts.values())
        return 1 / q

class E_8(Sample):
    '''
    Defines an E_8 sampling function.

    Attributes
    ----------  
    Sample
    '''
    def __init__(self, seed=None):
        '''
        Constructs an E_8 Sample.
        '''
        self.name = 'e8'
        t = toml.load(sample_path)
        adjustments = { int(seed) : (int(new_count), float(prob)) for seed, [new_count, prob] in t['E_8'].items() }
        Sample.__init__(self, Rounds.ELITE_8, adjustments, seed)

    def __call__(self):
        '''
        Returns 8 seeds for the Elite 8.
        '''
        out = []
        for _ in range(4):
            q1 = self.get_qhat(top)
            q2 = self.get_qhat(bottom)
            fixed_seed = 1 # 0 is the index of 1 in TOP_SEEDS_SORTED; must add 1 to account for subtraction by 1
            s1 = self.sample_seed(q1, 8, fixed_seed, top)
            fixed_seed = 11 # 5 is the index of 11 in BOTTOM_SEEDS_SORTED; must add 1 to account for subtraction by 1
            s2 = self.sample_seed(q2, 8, fixed_seed, bottom)
            out.append([s1, s2])
        return out

    def get_qhat(self, support: list): 
        # get the observed counts in the support.
        support_counts = {}
        for seed in support:
            support_counts[seed] = self.observed_counts[seed]
        q = 0
        for i in range(len(support)):
            q += (support_counts[support[i]] * (i + 1))
        q /= sum(support_counts.values())
        return 1 / q