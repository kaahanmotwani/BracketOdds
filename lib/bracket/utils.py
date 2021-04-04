#!/usr/bin/env python
from os.path import dirname, realpath

# an iterator for pairwise iteration. 
# [a, b, c, d, e, f] : (a, b) -> (c, d) -> (e, f)
def pairwise(iterable):
    a = iter(iterable)
    return zip(a, a)

# The order of seeds (pairwise) in which the matches are played
matchorder = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]

# A sorted list of all teams in the top half of the bracket
top = [1, 4, 5, 8, 9, 12, 13, 16]

# A sorted list of all teams in the bottom half of the bracket.
bottom = [2, 3, 6, 7, 10, 11, 14, 15]

# The base file path
path = dirname(dirname(realpath(__file__))) + "/"

# The file path for the men's data folder.
men_path = path + 'data/men/'

# the file path for the women's data folder.
women_path = path + 'data/women/'

# File paths to the sample configuration file.
sample_path = path + 'data/sample.toml'