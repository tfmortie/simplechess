"""
File containing code for the chess engines.
Author: Thomas Mortier
Date: March 2021
"""
import random
import math

from logic import getComponents, getValidPositions, isCheck

class RandomEngine:
    def __init__(self, color, orientation):
        self.color = color
        self.orientation = orientation

    def getMove(self, state, ep, castle):
        comp, pos = None, None
        # get components and shuffle
        comps = getComponents(self.color, state)
        random.shuffle(comps)
        # run over components
        for c in comps:
            # get valid positions and shuffle
            c_pos = getValidPositions(c, state, self.orientation, ep, castle)
            random.shuffle(c_pos)
            # do we have options?
            if len(c_pos) > 0:
                for p in c_pos:
                    if not isCheck(c, p, state, self.orientation):
                        comp, pos = c, p
                        break
            if comp is not None and pos is not None:
                break
        return comp, pos

    def getPromotion(self):
        # just pick a random option
        return random.choice([0, 1, 2, 3])

class ABPEngine:
    def __init__(self, color, orientation, depth):
        self.color = color # represents the color of the opponent
        self.orientation = orientation
        self.depth = depth

    def getMove(self, state, ep, castle):
        best_move_score, best_move_comp, best_move_pos = math.inf*-1, None, None
        # get all possible moves (ie. states)
        states = self.getStates(self.color, np.copy(state), ep, castle)
        for (c,p,s,ep,castle) in states: 
            score = self.alphabeta(s, ("white" if self.color=="black" else "black"), ep, castle, self.depth-1, math.inf*-1, math.inf, False)
            # did we find an improved move?
            if score > best_move_score:
                best_move_score = score
                best_move_comp = c
                best_move_pos = p

        return best_move_comp, best_move_pos 

    def alphabeta(self, state, color, ep, castle, depth, alpha, beta, maxp):
        return None
        """
        if depth == 0 or node is a terminal node then
            return the heuristic value of node
        if maxp:
            value = math.inf*-1
            for each child of node do
                value := max(value, alphabeta(child, depth − 1, α, β, FALSE))
                α := max(α, value)
                if α ≥ β then
                    break (* β cutoff *)
            return value
        else:
            value := +∞
            for each child of node do
                value := min(value, alphabeta(child, depth − 1, α, β, TRUE))
                β := min(β, value)
                if β ≤ α then
                    break (* α cutoff *)
            return value
        """

    def getStates(self, color, state, ep, castle):
        # init states
        ret_states = []
        # get all possible components
        comps = getComponents(color, state)
        # run over components and get score for all possible positions
        for c in comps:
            c_pos = getValidPositions(c, state, self.orientation, ep, castle)
            for cp in c_pos:
                ret_states.append(self.applyMove(c, cp, np.copy(state), self.orientation, ep, castle, ("black" if color=="white" else "white"))
)        
        return ret_states

    def getPromotion(self):
        # just pick queen
        return 3

    def getScoreState(state, color):
        """ return score of a particular state for opponent color """
        return 0

    def applyMove(self, comp, comppos, state, score, orientation, ep, castle, opponent):
        """
        return needs following format: (c,p,s,ep,castle)
        with 
        c: (x,y) the component which moves 
        p: (x,y) the new position for component
        s: state after new position have been applied
        score: score for both players after new position have been applied
        ep: en passant state
        castle: castle state
        """
        poption = None
        # checks for double pawn or en passant 
        if comppos[1]==comp[1] and abs(comppos[0]-comp[0])==2 and state[comp] in [1,7]:
            ep = comppos
        elif state[comp] in [1,7] and state[comppos]==0 and comppos[0]!=comp[0] and comppos[1]!=comp[1] and ep!=None:
            # en passant move
            if comppos[0] > comp[0]:
                state[comppos[0]-1,comppos[1]] = 0
            else:
                state[comppos[0]+1,comppos[1]] = 0
            ep = None
        else:
            ep = None
        # check for pawn promotion
        if comp[0]!=comppos[0] and state[comp] in [1,7] and (comppos[0]==0 or comppos[0]==7): 
            poption = self.getPromotion(state, ep, castle)
        # check whether we have a rook or king move
        if state[comp] in [2,8]:
            if comp==(0,0):
                castle[0]=True
            elif comp==(0,7):
                castle[2]=True
            elif comp==(7,0):
                castle[3]=True
            elif comp==(7,7):
                castle[5]=True
        if state[comp] in [6,12]:
            if (comp==(0,4) and state[comp]==6) or (comp==(0,3) and state[comp]==12):
                castle[1]=True
            elif (comp==(7,3) and state[comp]==6) or (comp==(7,4) and state[comp]==12):
                castle[4]=True
            # check if castled -> change rooks
            if abs(comp[1]-comppos[1])==2:
                # check if W or E
                if comp[1]<comppos[1]:
                    state[comppos[0],comppos[1]-1] = state[comp[0],7]
                    state[comp[0],7] = 0
                else:
                    state[comppos[0],comppos[1]+1] = state[comp[0],0]
                    state[comp[0],0] = 0
        # check if piece is captured
        if state[comppos] != 0:
            # get points
            points = 0
            if state[comppos] in [1,7]:
                points = 1
            elif state[comppos] in [2,8]:
                points = 5
            elif state[comppos] in [5,11]:
                points = 9
            else:
                points = 3
            if opponent:
                score[1] += points
            else:
                score[0] += points
        if poption is not None:
            if poption==0:
                state[comppos] = 4+((state[comp]//7)*6)
            elif poption==1:
                state[comppos] = 3+((state[comp]//7)*6)   
            elif poption==2:
                state[comppos] = 2+((state[comp]//7)*6)   
            else:
                state[comppos] = 5+((state[comp]//7)*6)   
        else:
            state[comppos] = state[comp]
        state[comp] = 0 
      return comp, comppos, state, score, ep, castle

"""
function alphabeta(node, depth, α, β, maximizingPlayer) is
    if depth = 0 or node is a terminal node then
        return the heuristic value of node
    if maximizingPlayer then
        value := −∞
        for each child of node do
            value := max(value, alphabeta(child, depth − 1, α, β, FALSE))
            α := max(α, value)
            if α ≥ β then
                break (* β cutoff *)
        return value
    else
        value := +∞
        for each child of node do
            value := min(value, alphabeta(child, depth − 1, α, β, TRUE))
            β := min(β, value)
            if β ≤ α then
                break (* α cutoff *)
        return value
"""
