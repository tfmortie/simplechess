"""
File containing code for main program.
Author: Thomas Mortier
Date: March 2021

TODO: 
    1) make sure to handle checkmate situations + fast move selection in case of check 
    2) add clock and different clock modes
    3) show current score (ie total score of components captured)
    4) add intelligence (idea: use different levels: free, low, medium, high, ...)
    5) improve GUI
"""
import sys
import pygame
import argparse
import random
import time # TODO: remove

import numpy as np

from logic import isValidComponentPosition
from engine import getRandomMove

S_OFFSET = {
    "small": (23,14,47.5),
    "medium": (32,17,71),
    "large": (45,25,95)}

S_SIZE = {
    "small": (400,400),
    "medium": (600,600),
    "large": (800,800)}

S_PSIZE = {
    "small": (30,30),
    "medium": (50,50),
    "large": (65,65)}

IND_2_P = ["bpawn", "brook", "bknight", "bbishop", "bqueen", "bking", "wpawn", "wrook", "wknight", "wbishop", "wqueen", "wking"]

P_SPRITE = {}

def initSprites(args):
    global P_SPRITE
    P_SPRITE = {
        "bpawn": pygame.transform.scale(pygame.image.load("assets/b_pawn.png"), S_PSIZE[args.size]),
        "brook": pygame.transform.scale(pygame.image.load("assets/b_rook.png"), S_PSIZE[args.size]),
        "bknight": pygame.transform.scale(pygame.image.load("assets/b_knight.png"), S_PSIZE[args.size]),
        "bbishop": pygame.transform.scale(pygame.image.load("assets/b_bishop.png"), S_PSIZE[args.size]),
        "bqueen": pygame.transform.scale(pygame.image.load("assets/b_queen.png"), S_PSIZE[args.size]),
        "bking": pygame.transform.scale(pygame.image.load("assets/b_king.png"), S_PSIZE[args.size]),
        "wpawn": pygame.transform.scale(pygame.image.load("assets/w_pawn.png"), S_PSIZE[args.size]),
        "wrook": pygame.transform.scale(pygame.image.load("assets/w_rook.png"), S_PSIZE[args.size]),
        "wknight": pygame.transform.scale(pygame.image.load("assets/w_knight.png"), S_PSIZE[args.size]),
        "wbishop": pygame.transform.scale(pygame.image.load("assets/w_bishop.png"), S_PSIZE[args.size]),
        "wqueen": pygame.transform.scale(pygame.image.load("assets/w_queen.png"), S_PSIZE[args.size]),
        "wking": pygame.transform.scale(pygame.image.load("assets/w_king.png"), S_PSIZE[args.size])}

def updateBoard(state, coord, screen):
        start_pos_x, start_pos_y, offset = coord 
        for i in range(8):
            for j in range(8):
                if state[i,j] > 0:
                    screen.blit(P_SPRITE[IND_2_P[state[i,j]-1]], (start_pos_x+(j*offset), start_pos_y+(i*offset)))

def isValidMousePosition(mousepos, coord):
    if not coord[0]<=mousepos[0]<=(coord[1]+(8*coord[2])):
        return False
    elif not coord[1]<=mousepos[1]<=(coord[1]+(8*coord[2])):
        return False
    else:
        return True

def applyMove(coord, new_coord, state, gamemode, ep, castle, opponent=False):
    moved = False
    # check if move is valid
    valid_move = False
    if opponent:
        valid_move = True
    else:
        valid_move = isValidComponentPosition(coord, new_coord, state, gamemode, ep, castle)
    if valid_move:
        # checks for double pawn or en passant 
        if new_coord[1]==coord[1] and abs(new_coord[0]-coord[0])==2 and state[coord] in [1,7]:
            ep = new_coord
        elif state[coord] in [1,7] and state[new_coord]==0 and new_coord[0]!=coord[0] and new_coord[1]!=coord[1] and ep!=None:
            # en passant move
            if new_coord[0] > coord[0]:
                state[new_coord[0]-1,new_coord[1]] = 0
            else:
                state[new_coord[0]+1,new_coord[1]] = 0
            ep = None
        else:
            ep = None
        # check whether we have a rook or king move
        if state[coord] in [2,8]:
            if coord==(0,0):
                castle[0]=True
            elif coord==(0,7):
                castle[2]=True
            elif coord==(7,0):
                castle[3]=True
            elif coord==(7,7):
                castle[5]=True
        if state[coord] in [6,12]:
            if (coord==(0,4) and state[coord]==6) or (coord==(0,3) and state[coord]==12):
                castle[1]=True
            elif (coord==(7,3) and state[coord]==6) or (coord==(7,4) and state[coord]==12):
                castle[4]=True
            # check if castled -> change rooks
            if abs(coord[1]-new_coord[1])==2:
                # check if W or E
                if coord[1]<new_coord[1]:
                    state[new_coord[0],new_coord[1]-1] = state[coord[0],7]
                    state[coord[0],7] = 0
                else:
                    state[new_coord[0],new_coord[1]+1] = state[coord[0],0]
                    state[coord[0],0] = 0
        state[new_coord] = state[coord]
        state[coord] = 0 
        coord = None
        moved = True
    return ep, coord, moved

def drawBoard(state, screen, chessbg, offs, clock):
    # set background
    screen.blit(chessbg, (0,0))
    updateBoard(state, S_OFFSET[args.size], screen)
    # update screen
    pygame.display.update()
    # wait fps seconds
    clock.tick(args.fps)
           
def main(args):  
    # init pygame
    pygame.init()
    # screen/window setup
    screen = pygame.display.set_mode(S_SIZE[args.size])
    pygame.display.set_caption("Simple Chess")
    # init background and state
    state = np.zeros((8,8),dtype=np.int)
    gamemode = args.colour
    if gamemode == "random":
        m = random.choice(["w","b"])
        gamemode = "white" if m=="w" else "black"
    if gamemode == "black":
        chessbg = pygame.image.load("assets/backgroundb.png")
        # init pawns
        state[6,:] = np.ones(8)
        state[1,:] = np.ones(8)*7
        # init border ranks
        state[7,:] = np.array([2,3,4,6,5,4,3,2])
        state[0,:] = np.array([8,9,10,12,11,10,9,8])
    else:
        chessbg = pygame.image.load("assets/backgroundw.png")
        # init pawns
        state[6,:] = np.ones(8)*7
        state[1,:] = np.ones(8)
        # init border ranks
        state[7,:] = np.array([8,9,10,11,12,10,9,8])
        state[0,:] = np.array([2,3,4,5,6,4,3,2])
    chessbg = pygame.transform.scale(chessbg, S_SIZE[args.size])
    # init sprites
    initSprites(args)
    # init clock for fps
    clock = pygame.time.Clock()
    # game loop
    moved = False
    coord = None
    ep = None
    castle = [False]*6
    while True: 
        drawBoard(state, screen, chessbg, S_OFFSET[args.size], clock)
        if gamemode == "black":
            time.sleep(1)
            comp, pos = getRandomMove("white", state, gamemode, ep, castle) 
            ep, coord, _ = applyMove(comp, pos, state, gamemode, ep, castle, True)
            drawBoard(state, screen, chessbg, S_OFFSET[args.size], clock)
        while not moved:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # check if L mouse button was used
                    if event.button == 1:
                        mouseposxy = pygame.mouse.get_pos()
                        # check which component has been selected
                        coord = int((mouseposxy[1]-S_OFFSET[args.size][1])//S_OFFSET[args.size][2]), int((mouseposxy[0]-S_OFFSET[args.size][0])//S_OFFSET[args.size][2])
                        # if no component has been selected, do nothing
                        if state[coord] == 0:
                            coord = None
                elif event.type == pygame.MOUSEBUTTONUP and coord is not None:
                    if event.button == 1:
                        # L mouse button released, hence, check new position and update state
                        mouseposxy = pygame.mouse.get_pos()
                        new_coord = int((mouseposxy[1]-S_OFFSET[args.size][1])//S_OFFSET[args.size][2]), int((mouseposxy[0]-S_OFFSET[args.size][0])//S_OFFSET[args.size][2])
                        # move component in case of new position which is valid
                        if coord != new_coord and isValidMousePosition(mouseposxy, S_OFFSET[args.size]):
                            ep, coord, moved = applyMove(coord, new_coord, state, gamemode, ep, castle, False)
            drawBoard(state, screen, chessbg, S_OFFSET[args.size], clock)
        moved = False
        if gamemode == "white":
            time.sleep(1)
            comp, pos = getRandomMove("black", state, gamemode, ep, castle) 
            ep, coord, _ = applyMove(comp, pos, state, gamemode, ep, castle, True)
    # end game
    pygame.quit()

if __name__=='__main__':
    screensize = ["small", "medium", "large"]
    colour = ["black", "white", "random"]
    parser = argparse.ArgumentParser(description="Simple Chess") 
    parser.add_argument("-s", "--size", dest='size', default="medium", choices=screensize)
    parser.add_argument("-c", "--colour", dest="colour", default="random", choices=colour)
    parser.add_argument("-f", "--fps", dest="fps", type=int, default=30)
    args = parser.parse_args()
    main(args)
