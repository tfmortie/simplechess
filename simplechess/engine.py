"""
File containing code for the chess engines.
Author: Thomas Mortier
Date: March 2021
"""
import random
import math

import numpy as np

from logic import getComponents, getValidPositions, isCheck, isChecked, isStalemated

class RandomEngine:
    def __init__(self, color, orientation):
        self.color = color
        self.orientation = orientation

    def getMove(self, state, score, ep, castle):
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
        self.color = color  # represents the color of the opponent
        self.orientation = orientation
        self.depth = depth

    def getMove(self, state, score, ep, castle):
        c, ps, score = self.alphabeta(state, None, None, score, self.color, ep, castle, self.depth, math.inf*-1, math.inf, True)
        return c, ps

    def alphabeta(self, state, comp, comppos, score, color, ep, castle, depth, alpha, beta, maxp):
        """
        Arguments:
            state : the (current) state of game 
            comp : the component of current state
            comppos : the position of current state
            score : list of scores for both opponents for current state
            color : the current player for which we would like to calculate possible moves and scores
            ep : state for en-passant
            castle : state for castling
            depth : current depth in game tree
            alpha : alpha score
            beta : beta score
            maxp : is current player the maximizing player?
        Return:
            best_move_comp : component of best move
            best_move_pos : position of best move
            score : score of best move
        """
        # is current node in check?
        checked = isChecked(color, state, self.orientation, ep, castle)
        # is current node stalemated?
        stalemated = isStalemated(color, state, self.orientation, ep, castle)
        if depth == 0 or (checked and stalemated):
            # we reached a terminal node (either due to depth=0 or checkmate)
            if (checked and stalemated):
                return comp, comppos, 100
            else:
                #return comp, comppos, (score[1] if not maxp else score[0])
                return comp, comppos, score[1]-score[0]
        if maxp:
            if depth==self.depth:
                # opponent's turn
                best_c, best_cp, best_value = None, None, math.inf*-1
                # get all possible moves 
                states = self.getStates(color, state, score, ep, castle)
                # sort in decreasing order (max-player) in order to improve runtime
                states = sorted(states, key=lambda x: x[3])[::-1]
                for st in states: 
                    c, cp, s = self.alphabeta(st[2], st[0], st[1], st[3], ("white" if color=="black" else "black"), st[4], st[5], depth-1, alpha, beta, False) 
                    if s > best_value:
                        best_value = s
                        best_c = c
                        best_cp = cp
                    alpha = max(alpha, best_value)
                    if alpha >= beta:
                        break
                return best_c, best_cp, best_value 
            else:
                # opponent's turn
                best_value = math.inf*-1
                # get all possible moves 
                states = self.getStates(color, state, score, ep, castle)
                # sort in decreasing order (max-player) in order to improve runtime
                states = sorted(states, key=lambda x: x[3])[::-1]
                for st in states: 
                    c, cp, s = self.alphabeta(st[2], comp, comppos, st[3], ("white" if color=="black" else "black"), st[4], st[5], depth-1, alpha, beta, False) 
                    if s > best_value:
                        best_value = s
                    alpha = max(alpha, best_value)
                    if alpha >= beta:
                        break
                return comp, comppos, best_value 
        else:
            # our turn
            best_c, best_cp, best_value = None, None, math.inf
            # get all possible moves 
            states = self.getStates(color, state, score, ep, castle)
            # sort in increasing order (min-player)  in order to improve runtime
            states = sorted(states, key=lambda x: x[3])
            for st in states: 
                c, cp, s = self.alphabeta(st[2], comp, comppos, st[3], ("white" if color=="black" else "black"), st[4], st[5], depth-1, alpha, beta, True) 
                if s < best_value:
                    best_value = s
                    best_c = c
                    best_cp = cp
                beta = min(beta, best_value)
                if beta <= alpha:
                    break
            return best_c, best_cp, best_value 
            
    def getStates(self, color, state, score, ep, castle):
        """
        Arguments:
            color : the current player for which we would like to calculate possible moves and scores
            state : the (current) state of game 
            score : list of scores for both opponents for current state
            ep : state for en-passant
            castle : state for castling
        Return:
            ret_states : list of (c, p, s, score, ep, castle)-tuples 
        """
        # init states
        ret_states = []
        # get all possible components
        comps = getComponents(color, state)
        # run over components and get score for all possible positions
        for c in comps:
            c_pos = getValidPositions(c, state, self.orientation, ep, castle)
            for cp in c_pos:
                # also check whether the current move does not lead to a check
                if not isCheck(c, cp, state, self.orientation):
                    if ep is not None:
                        ret_states.append(self.applyMove(c, cp, np.copy(state), score.copy(), self.orientation, ep.copy(), castle.copy(), (color==self.color)))        
                    else:
                        ret_states.append(self.applyMove(c, cp, np.copy(state), score.copy(), self.orientation, None, castle.copy(), (color==self.color)))

        random.shuffle(ret_states)
        return ret_states

    def getPromotion(self):
        # just pick queen (TODO could be improved)
        return 3

    def applyMove(self, comp, comppos, state, score, orientation, ep, castle, opponent):
        """
        Important: arguments that are going to be modified: state, score, ep, castle 

        Arguments:
            comp : component of move to be applied
            comppos : new position of component
            state : the (current, ie, before new move) state of game
            score : list of scores for both opponents for current (ie, before new move) state
            orientation : orientation of the game 
            ep : current (ie, before new move) state for en-passant
            castle : current (ie, before new move) state for castling
            opponent : whether the component of the applied move represents a component of the opponent 
        Return:
            comp : component of move applied
            comppos : position of applied move of component
            state : new state of game after applied move 
            score : new score of game after applied move 
            ep : new ep state of game after applied move
            castle : new castle state of game after applied move
        """
        poption = None
        # checks for double pawn or en passant 
        if comppos[1]==comp[1] and abs(comppos[0]-comp[0])==2 and state[comp] in [1,7]:
            ep = list(comppos)
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
            poption = self.getPromotion()
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
