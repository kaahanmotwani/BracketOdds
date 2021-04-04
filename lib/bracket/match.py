#!/usr/bin/env python
import json, random
from .round import Rounds
from .team import Team

class Match():
    '''
    Defines one game between two teams.

    Attributes
    ----------
    t1 (Team) : Team name representing one team in the game.
    t2 (Team) : Team name representing the other team in the game.
    rnd (Rounds) : A Rounds enum value representing the round in which the match takes place.
    alpha (float) : The alpha (actual or default) value for the pair of seeds and round.
    prob (float) : The probability that team 1 wins according to the model.
    winner (Team) : The team object that wins according to a simulation with the probability.
    '''
    def __init__(self, team1: Team, team2: Team, rnd: Rounds, alpha: float=None, winner: Team=None):
        '''
        Constructs a Match object.

        Parameters
        ----------
        team1 (Team) : the Team object for t1.
        team2 (Team) : the Team object for t2.
        rnd (Rounds) : the rnd enum value representing the current round.
        alpha (float) : an alpha value for the matchup
        '''
        self.t1 = team1
        self.t2 = team2
        self.rnd = rnd
        self.alpha = alpha
        self.prob = self.win_prob() if alpha != None else None
        self.winner = winner if winner else self.get_winner() 

    def win_prob(self) -> float:
        '''
        Returns the probability that team 1 wins.
        '''
        return (1.0 * self.t2.seed ** self.alpha) / (self.t1.seed ** self.alpha + self.t2.seed ** self.alpha)

    def get_winner(self) -> Team:
        '''
        Returns the winning Team object.
        '''
        rand = random.random() 
        return self.t1 if rand < self.prob else self.t2

    def bits(self) -> bool:
        '''
        Return 0 if Team 1 wins, else return 1.
        '''
        return 0 if self.winner == self.t1 else 1
        
    def to_json(self) -> str:
        '''
        Returns a json string represenation of a Match which is json serializeable.
        '''
        return json.dumps({
            't1': self.t1.to_json(),
            't2': self.t2.to_json(),
            'rnd': self.rnd.value,
            'winner': self.winner.to_json()
        })