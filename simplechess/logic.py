"""
File containing code for chess logic.
Author: Thomas Mortier
Date: March 2021
"""
import itertools

def isValidComponentPosition(coord, new_coord, state, orientation):
    # get all possible valid moves for component
    moves = getValidPositions(coord, state, orientation)
    if new_coord in moves:
        return True
    else: 
        return False

def getValidPositions(coord, state, orientation):
    # pawn = 1 (black) 7 (white)
    # rook = 2 (black) 8 (white) 
    if state[coord]==1 or state[coord]==7:
        # pawn logic
        moves = []
        if (state[coord]==1 and orientation=="black") or (state[coord]==7 and orientation=="white"):
            # N
            for j in range(coord[0]-1,max(coord[0]-(3 if coord[0]==6 else 2),-1),-1):
                if state[j,coord[1]] == 0:
                    moves.append((j,coord[1]))
                else:
                    break
            # NW & NE
            if (coord[0]>0 and coord[1]>0) and (state[coord]//7!=state[coord[0]-1,coord[1]-1]//7 and state[coord[0]-1,coord[1]-1]!=0):
                moves.append((coord[0]-1,coord[1]-1))
            if (coord[0]>0 and coord[1]<7) and (state[coord]//7!=state[coord[0]-1,coord[1]+1]//7 and state[coord[0]-1,coord[1]+1]!=0):
                moves.append((coord[0]-1,coord[1]+1))
        else:
            # S
            for j in range(coord[0]+1,min(coord[0]+(3 if coord[0]==1 else 2),8)):
                if state[j,coord[1]] == 0:
                    moves.append((j,coord[1]))
                else:
                    break
            # SW & SE
            if (coord[0]<7 and coord[1]>0) and (state[coord]//7!=state[coord[0]+1,coord[1]-1]//7 and state[coord[0]+1,coord[1]-1]!=0):
                moves.append((coord[0]+1,coord[1]-1))
            if (coord[0]<7 and coord[1]<7) and (state[coord]//7!=state[coord[0]+1,coord[1]+1]//7 and state[coord[0]+1,coord[1]+1]!=0):
                moves.append((coord[0]+1,coord[1]+1))
        return moves
    elif state[coord]==2 or state[coord]==8:
        # rook logic
        return []
    else:
        return list(itertools.product(range(8),range(8))) 
