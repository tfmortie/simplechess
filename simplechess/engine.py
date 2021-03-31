"""
File containing code for the chess engines.
Author: Thomas Mortier
Date: March 2021
"""
import random

from logic import getComponents, getValidPositions, isCheck

def getRandomMove(color, state, orientation, ep, castle):
    comp, pos = None, None
    while pos is None:
        # pick random component
        comp = random.choice(getComponents(color, state))
        # get valid positions
        comp_pos = getValidPositions(comp, state, orientation, ep, castle)
        if len(comp_pos) > 1:
            pos = random.choice(comp_pos)
            if isCheck(comp, pos, state, orientation):
                comp, pos = None, None

    return comp, pos

