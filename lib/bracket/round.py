#!/usr/bin/env python
from enum import Enum

class Rounds(Enum):
    '''
    Defines the 6 Rounds in the tournament.
    '''
    ROUND_OF_64 = 1
    ROUND_OF_32 = 2
    SWEET_16 = 3
    ELITE_8 = 4
    FINAL_4 = 5
    CHAMPIONSHIP = 6