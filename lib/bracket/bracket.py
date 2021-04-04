#!/usr/bin/env python
from .sample import Sample
from enum import Enum
import json, os, random, toml
from .alpha import Alpha
from .match import Match
from .team import Team
from .region import Region
from .round import Rounds
from .utils import matchorder, pairwise, men_path, women_path

class BracketType(Enum):
    '''
    Enum to select the men's or women's bracket.
    '''
    MEN = 'men'
    WOMEN = 'women'

class Bracket:
    '''
    Defines a tournament bracket.
    '''
    def __init__(self, bracket_type: BracketType, sampling_fn: Sample=None):
        '''
        Constructs a Bracket object.

        Parameters
        ----------
        bracket_type (BracketType) : a BracketType enum value that selects the men's or women's bracket.
        sampling_fn (Sample) : a Sample object (i.e. F4_A or E_8).
        '''
        self.bracket_type = bracket_type
        data_path = men_path if bracket_type == BracketType.MEN else women_path
        self.alpha = Alpha(data_path + 'alpha.toml')
        self.sfn = sampling_fn.name if sampling_fn else None
        self.sample = sampling_fn() if sampling_fn else None
        self.regions = []
        t = toml.load(data_path + 'regions.toml')
        # iterate through all 4 regions
        for i in range(4):
            rnd = sampling_fn.rnd if self.sample else None
            seeds = self.sample[i] if self.sample else None
            region_teams = {int(seed) : name for seed, name in t[str(i)].items() }
            self.regions.append(Region(t['regions'][i], region_teams, self.alpha, seeds, rnd))
        self.rounds = { Rounds.FINAL_4: [], Rounds.CHAMPIONSHIP: [] }
        # self.match_list = self.matches()

    @classmethod
    def from_bitstring(cls, bracket_type: BracketType, bitstring: str):
        bracket = cls(bracket_type)
        it = iter(bitstring)
        for region in bracket.regions:
            for s1, s2 in pairwise(matchorder):
                w = region.teams[s2] if int(next(it)) else region.teams[s1]
                region.rounds[Rounds.ROUND_OF_64].append(Match(region.teams[s1], region.teams[s2],
                    Rounds.ROUND_OF_64, winner=w))
        for rnd_num in range(2, 5):
            rnd = Rounds(rnd_num)
            for region in bracket.regions:
                for m1, m2 in pairwise(region.rounds[Rounds(rnd_num - 1)]):
                    w = m2.winner if int(next(it)) else m1.winner
                    region.rounds[rnd].append(Match(m1.winner, m2.winner, rnd, winner=w))
        for r1, r2 in pairwise(bracket.regions):
            t1 = r1.rounds[Rounds.ELITE_8][0].winner
            t2 = r2.rounds[Rounds.ELITE_8][0].winner
            w = t2 if int(next(it)) else t1
            bracket.rounds[Rounds.FINAL_4].append(Match(t1, t2, Rounds.FINAL_4, winner=w))
        
        t1 = bracket.rounds[Rounds.FINAL_4][0].winner
        t2 = bracket.rounds[Rounds.FINAL_4][1].winner
        w = t2 if int(next(it)) else t1
        bracket.rounds[Rounds.CHAMPIONSHIP].append(Match(t1, t2, Rounds.CHAMPIONSHIP, winner=w))
        return bracket
        
    def run(self) -> Team:
        '''
        Runs the entire bracket to calculate a winner. Returns the winning Team.
        '''
        for region in self.regions:
            region.run()
        # Rounds 1 - 4 handled in each region.
        # Round 5 (Final 4)
        for r1, r2 in pairwise(self.regions):
            self.rounds[Rounds.FINAL_4].append(Match(r1.rounds[Rounds.ELITE_8][0].winner, r2.rounds[Rounds.ELITE_8][0].winner, 
                Rounds.FINAL_4, self.alpha.get_alpha(Rounds.FINAL_4)))
        # Round 6 (Championship)
        self.rounds[Rounds.CHAMPIONSHIP].append(
            Match(self.rounds[Rounds.FINAL_4][0].winner, self.rounds[Rounds.FINAL_4][1].winner,
                Rounds.CHAMPIONSHIP, self.alpha.get_alpha(Rounds.CHAMPIONSHIP)))
    
    def bits(self) -> str:
        '''
        Return a bitstring representing the bracket.
        '''
        out = ['0'] * 64
        m = self.matches()
        for i in range(len(m)):
            out[i] = str(m[i].bits())
        return ''.join(out)

    def matches(self) -> list:
        '''
        Return an ordered list of all matches played in a bracket.
        '''
        # The first four rounds handled inside each region.
        regional_rounds = range(1, 5)
        # The last two rounds played across regions.
        final_rounds = range(5, 7)
        out = []
        for rnd_num in regional_rounds:
            for region in self.regions:
                for match in region.rounds[Rounds(rnd_num)]:
                    out.append(match)
        for rnd in final_rounds:
            for match in self.rounds[Rounds(rnd)]:
                out.append(match)
        return out

    def to_json(self):
        '''
        Returns a json serializeable dict representation of a Bracket.
        '''
        d = {
            'type': self.bracket_type.value,
            'bitstring': self.bits(),
            'matches' : [match.to_json() for match in self.matches()],
            'sampled_seeds': self.sample,
            'winner': self.rounds[Rounds.CHAMPIONSHIP][0].winner.to_json() \
                if self.rounds[Rounds.CHAMPIONSHIP] else None,
            'sfn': self.sfn,
            'regions': [region.name for region in self.regions]
        }
        return d