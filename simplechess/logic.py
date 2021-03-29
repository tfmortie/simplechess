"""
File containing code for chess logic.
Author: Thomas Mortier
Date: March 2021
"""
import itertools

import numpy as np

def isValidComponentPosition(coord, new_coord, state, orientation, ep, castle):
    # get all possible valid moves for component
    moves = getValidPositions(coord, state, orientation, ep, castle)
    if new_coord in moves:
        if not isCheck(coord, new_coord, state, orientation):
            return True
        else:
            return False
    else: 
        return False

def getValidPositionsHorizontal(coord, state):
    moves = []
    # W
    for j in range(coord[1]-1,-1,-1):
        if state[coord[0],j]==0:
            moves.append((coord[0],j))
        elif state[coord]//7!=state[coord[0],j]//7:
            moves.append((coord[0],j))
            break
        else:
            break
    # E
    for j in range(coord[1]+1,8):
        if state[coord[0],j]==0:
            moves.append((coord[0],j))
        elif state[coord]//7!=state[coord[0],j]//7:
            moves.append((coord[0],j))
            break
        else:
            break
    return moves

def getValidPositionsVertical(coord, state):
    moves = []
    # N
    for j in range(coord[0]-1,-1,-1):
        if state[j,coord[1]]==0:
            moves.append((j,coord[1]))
        elif state[coord]//7!=state[j,coord[1]]//7:
            moves.append((j,coord[1]))
            break
        else:
            break
    # S
    for j in range(coord[0]+1,8):
        if state[j,coord[1]]==0:
            moves.append((j,coord[1]))
        elif state[coord]//7!=state[j,coord[1]]//7:
            moves.append((j,coord[1]))
            break
        else:
            break
    return moves

def getValidPositionsDiagonal(coord, state):
    moves = []
    # NW
    for o in list(range(1,min(coord[0],coord[1])+1)):
        if state[coord[0]-o,coord[1]-o]==0:
            moves.append((coord[0]-o,coord[1]-o))
        elif state[coord]//7!=state[coord[0]-o,coord[1]-o]//7:
            moves.append((coord[0]-o,coord[1]-o))
            break
        else:
            break
    # NE
    for o in list(range(1,min(coord[0],7-coord[1])+1)):
        if state[coord[0]-o,coord[1]+o]==0:
            moves.append((coord[0]-o,coord[1]+o))
        elif state[coord]//7!=state[coord[0]-o,coord[1]+o]//7:
            moves.append((coord[0]-o,coord[1]+o))
            break
        else:
            break
    # SW
    for o in list(range(1,min(7-coord[0],coord[1])+1)):
        if state[coord[0]+o,coord[1]-o]==0:
            moves.append((coord[0]+o,coord[1]-o))
        elif state[coord]//7!=state[coord[0]+o,coord[1]-o]//7:
            moves.append((coord[0]+o,coord[1]-o))
            break
        else:
            break
    # SE
    for o in list(range(1,min(7-coord[0],7-coord[1])+1)):
        if state[coord[0]+o,coord[1]+o]==0:
            moves.append((coord[0]+o,coord[1]+o))
        elif state[coord]//7!=state[coord[0]+o,coord[1]+o]//7:
            moves.append((coord[0]+o,coord[1]+o))
            break
        else:
            break
    return moves

def getValidPositions(coord, state, orientation, ep=None, castle=None):
    moves = []
    if state[coord]==1 or state[coord]==7:
        # pawn logic
        if (state[coord]==1 and orientation=="black") or (state[coord]==7 and orientation=="white"):
            # N
            for j in range(coord[0]-1,max(coord[0]-(3 if coord[0]==6 else 2),-1),-1):
                if state[j,coord[1]]==0:
                    moves.append((j,coord[1]))
                else:
                    break
            # NW & NE
            if (coord[0]>0 and coord[1]>0) and ((state[coord]//7!=state[coord[0]-1,coord[1]-1]//7 and state[coord[0]-1,coord[1]-1]!=0) or (state[coord[0]-1,coord[1]-1]==0 and (coord[0],coord[1]-1)==ep)):
                moves.append((coord[0]-1,coord[1]-1))
            if (coord[0]>0 and coord[1]<7) and ((state[coord]//7!=state[coord[0]-1,coord[1]+1]//7 and state[coord[0]-1,coord[1]+1]!=0) or (state[coord[0]-1,coord[1]+1]==0 and (coord[0],coord[1]+1)==ep)):
                moves.append((coord[0]-1,coord[1]+1))
        else:
            # S
            for j in range(coord[0]+1,min(coord[0]+(3 if coord[0]==1 else 2),8)):
                if state[j,coord[1]]==0:
                    moves.append((j,coord[1]))
                else:
                    break
            # SW & SE
            if (coord[0]<7 and coord[1]>0) and ((state[coord]//7!=state[coord[0]+1,coord[1]-1]//7 and state[coord[0]+1,coord[1]-1]!=0) or (state[coord[0]+1,coord[1]-1]==0 and (coord[0],coord[1]-1)==ep)):
                moves.append((coord[0]+1,coord[1]-1))
            if (coord[0]<7 and coord[1]<7) and ((state[coord]//7!=state[coord[0]+1,coord[1]+1]//7 and state[coord[0]+1,coord[1]+1]!=0) or (state[coord[0]+1,coord[1]+1]==0 and (coord[0],coord[1]+1)==ep)):
                moves.append((coord[0]+1,coord[1]+1))
        return moves
    elif state[coord]==2 or state[coord]==8:
        # rook logic
        moves.extend(getValidPositionsHorizontal(coord, state))
        moves.extend(getValidPositionsVertical(coord, state))
    elif state[coord]==3 or state[coord]==9:
        # knight logic
        for i in [-2,-1,1,2]:
            ji = (1 if abs(i)==2 else 2)
            for j in [ji, -1*ji]:
                if 0<=coord[0]+i<=7 and 0<=coord[1]+j<=7 and (state[coord]//7!=state[coord[0]+i,coord[1]+j]//7 or state[coord[0]+i,coord[1]+j]==0):
                    moves.append((coord[0]+i,coord[1]+j))
    elif state[coord]==4 or state[coord]==10:
        # bishop logic
        moves.extend(getValidPositionsDiagonal(coord, state))
    elif state[coord]==5 or state[coord]==11:
        # queen logic
        moves.extend(getValidPositionsDiagonal(coord, state))
        moves.extend(getValidPositionsHorizontal(coord, state))
        moves.extend(getValidPositionsVertical(coord, state))    
    else:
        # king logic
        for ox in [-1,0,1]:
            for oy in [-1,0,1]:
                if not(ox==0 and oy==0):
                    if 0<=coord[0]+ox<=7 and 0<=coord[1]+oy<=7 and (state[coord]//7!=state[coord[0]+ox,coord[1]+oy]//7 or state[coord[0]+ox,coord[1]+oy]==0):
                        moves.append((coord[0]+ox,coord[1]+oy))
        # now also check whether castling is allowed
        if castle is not None:
            if coord[0]==0 or coord[0]==7:
                # W
                if castle[(1 if coord[0]==0 else 4)]!=True and castle[(0 if coord[0]==0 else 3)]!=True:
                    if np.all(state[coord[0],1:coord[1]]==0) and not isAttacked([(coord[0],coord[1]-j) for j in range(3)],state,("white" if state[coord]<7 else "black"), orientation):
                        moves.append((coord[0],coord[1]-2))
                # E
                if castle[(1 if coord[0]==0 else 4)]!=True and castle[(2 if coord[0]==0 else 5)]!=True:
                    if np.all(state[coord[0],coord[1]+1:7]==0) and not isAttacked([(coord[0],coord[1]+j) for j in range(3)],state,("white" if state[coord]<7 else "black"), orientation):
                        moves.append((coord[0],coord[1]+2))
    return moves

def isAttacked(pos, state, attacker, orientation):
    attacked = False
    for i in range(8):
        for j in range(8):
            # check if we have a component of the attacker
            if state[i,j]//7==(0 if attacker=="black" else 1) and state[i,j]!=0:
                # check if the current component attacks any of the positions in pos
                att_pos = getValidPositions((i,j), state, orientation, None, None)
                for p in pos:
                    if p in att_pos:
                        attacked=True
                        break
                if attacked:
                    break
        if attacked:
            break
    return attacked

def isCheck(coord, new_coord, state, orientation):
    # create snapshot of state after new move
    new_state = np.copy(state) 
    new_state[new_coord] = state[coord]
    new_state[coord] = 0
    # find position of king
    pos_king = [c[0] for c in np.where(new_state==6*((state[coord]//7)+1))]
    # check if attacked
    return isAttacked([tuple(pos_king)], new_state, ("white" if state[coord]//7==0 else "black"), orientation)
