"""
File containing code for the chess engines.
Author: Thomas Mortier
Date: March 2021
"""
import random

from logic import getComponents, getValidPositions, isCheck

def getRandomMove(color, state, orientation, ep, castle):
    comp, pos = None, None
    # get components and shuffle
    comps = getComponents(color, state)
    random.shuffle(comps)
    # run over components
    for c in comps:
        # get valid positions and shuffle
        c_pos = getValidPositions(c, state, orientation, ep, castle)
        random.shuffle(c_pos)
        # do we have options?
        if len(c_pos) > 0:
            for p in c_pos:
                if not isCheck(c, p, state, orientation):
                    comp, pos = c, p
                    break
        if comp is not None and pos is not None:
            break
    return comp, pos

def getRandomPromotion(color, state, orientation, ep, castle):
    # just pick a random option from {0,1,2,3}
    return random.choice([0,1,2,3])
