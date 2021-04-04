#!/usr/bin/env python
from .alpha import Alpha
from .match import Match
from .round import Rounds
from .team import Team
from .utils import matchorder, pairwise


class Region:
    '''
    Defines a region with 16 teams in the tournament.

    Attributes
    ----------
    teams (dict) : a dict with seed number -> Team for each of the
        sixteen teams in the region.
    rounds (dict) : a dict with Rounds -> list of Match objects
        for each of the six rounds in the tournament.
    alpha (Alpha) : an Alpha object to query alpha values.
    winner (Team) : stores the winning Team in the region
        (AKA the winner of the Elite Eight Matchup in a particular region).
    '''
    def __init__(self, name:str, teams: dict, alpha: Alpha, 
        sample_seeds: list=None, sample_round: Rounds=None):
        '''
        Constructs a Region object.

        Parameters
        ----------
        name (str): the region name
        teams (dict) : a map of seed onto team name for each particular region.
        region (Regions) : a Regions enum value storing the region.
        alpha (Alpha) : an Alpha object to look up alpha values (see alpha.py and alpha.toml).
        '''
        self.name = name
        self.teams = { s: Team(s, n) for s, n in teams.items() }
        self.rounds = { rnd: [] for rnd in Rounds if rnd.value < Rounds.FINAL_4.value }
        self.alpha = alpha
        self.sample_seeds = sample_seeds
        self.sample_round = sample_round

    def run(self) -> Team:
        '''
        Returns the winning team in the region and fills in all the matches played.
        ''' 

        # initialize known first round matchups.
        for s1, s2 in pairwise(matchorder):
            self.rounds[Rounds.ROUND_OF_64].append(Match(self.teams[s1], self.teams[s2],
                Rounds.ROUND_OF_64, self.alpha.get_alpha(Rounds.ROUND_OF_64, s1, s2), 
                self.get_winner(self.teams[s1], self.teams[s2])))

        # Start at the round of 32 b/c the round of 64 is initialized from the file data.
        rnd = Rounds.ROUND_OF_32

        while rnd.value < Rounds.FINAL_4.value:
            # Each match is formed from the winners of the previous two matches,
            for m1, m2 in pairwise(self.rounds[Rounds(rnd.value - 1)]):
                t1 = m1.winner
                t2 = m2.winner
                winner = None
                if self.sample_round:
                    winner = self.get_winner(t1, t2) if rnd.value <= self.sample_round.value else None
                self.rounds[rnd].append(Match(t1, t2, rnd, self.alpha.get_alpha(rnd, t1.seed, t2.seed), winner))
            rnd = Rounds(rnd.value + 1)

    def get_winner(self, t1, t2) -> int:
        '''
        If t1 xor t2 are in the sampled seeds then return the seed of the winner, else return None.
        '''
        if not self.sample_seeds:
            return None
        elif t1.seed in self.sample_seeds and t2.seed in self.sample_seeds:
            return None
        elif t1.seed in self.sample_seeds:
            return t1
        elif t2.seed in self.sample_seeds:
            return t2
        return None