#!/usr/bin/env python
import csv, json, os

class Team:
    '''
    Defines a single team in the tournament.

    Attributes
    ----------
    seed (int) - the team's tournament seed in the range [1, 16].
    name (str) - the team's name.
    '''
    def __init__(self, seed: int, name: str):
        '''
        Constructs a Team object.

        Parameters
        ----------
        seed (int) : the team's seed in the tournament.
        name (str) : the name of the team.
        '''
        self.seed = seed
        self.name = name

    def to_json(self) -> dict:
        '''
        Returns a json serializeable dict representation of a Team.
        '''
        return {
            'seed': self.seed,
            'name': self.name
        }