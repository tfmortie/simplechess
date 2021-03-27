"""
File containing code for chess logic.
Author: Thomas Mortier
Date: March 2021
"""
import itertools

def isValidComponentPosition(coord, new_coord, state, orientation, ep):
    # get all possible valid moves for component
    moves = getValidPositions(coord, state, orientation, ep)
    if new_coord in moves:
        return True
    else: 
        return False

def getValidPositions(coord, state, orientation, ep=None):
    # pawn = 1 (black) 7 (white)
    # rook = 2 (black) 8 (white) 
    moves = []
    if state[coord]==1 or state[coord]==7:
        # pawn logic
        if (state[coord]==1 and orientation=="black") or (state[coord]==7 and orientation=="white"):
            # N
            for j in range(coord[0]-1,max(coord[0]-(3 if coord[0]==6 else 2),-1),-1):
                if state[j,coord[1]] == 0:
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
                if state[j,coord[1]] == 0:
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
        # N
        for j in range(coord[0]-1,-1,-1):
            if state[j,coord[1]] == 0:
                moves.append((j,coord[1]))
            elif state[coord]//7!=state[j,coord[1]]//7:
                moves.append((j,coord[1]))
                break
            else:
                break
        # S
        for j in range(coord[0]+1,8):
            if state[j,coord[1]] == 0:
                moves.append((j,coord[1]))
            elif state[coord]//7!=state[j,coord[1]]//7:
                moves.append((j,coord[1]))
                break
            else:
                break
        # W
        for j in range(coord[1]-1,-1,-1):
            if state[coord[0],j] == 0:
                moves.append((coord[0],j))
            elif state[coord]//7!=state[coord[0],j]//7:
                moves.append((coord[0],j))
                break
            else:
                break
        # E
        for j in range(coord[1]+1,8):
            if state[coord[0],j] == 0:
                moves.append((coord[0],j))
            elif state[coord]//7!=state[coord[0],j]//7:
                moves.append((coord[0],j))
                break
            else:
                break
    else:
        moves = list(itertools.product(range(8),range(8))) 

    return moves
