"""
File containing code for main program.
Author: Thomas Mortier
Date: March 2021

TODO: 
    1) add clock and different clock modes
    2) show current score (ie total score of components captured)
    3) add intelligence (idea: use different levels: free, low, medium, high, ...)
    4) improve GUI (eg. logging and messaging via GUI instead of console)
"""
import sys
import pygame
import argparse
import random
import time
import logging
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

import numpy as np

from logic import isValidComponentPosition, isChecked, isStalemated
from engine import getRandomMove, getRandomPromotion

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

def applyMove(coord, new_coord, state, orientation, ep, castle, opponent=False):
    poption = None
    moved = False
    # check if move is valid
    valid_move = False
    if opponent:
        valid_move = True
    else:
        valid_move = isValidComponentPosition(coord, new_coord, state, orientation, ep, castle)
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
        # check for pawn promotion
        if coord[0]!=new_coord[0] and state[coord] in [1,7] and (new_coord[0]==0 or new_coord[0]==7):
            if opponent:
                poption = getRandomPromotion(("white" if orientation=="black" else "black"), state, orientation, ep, castle)
            else:
                while True:
                    logging.info("Pawn promotion! Enter option (0=bishop, 1=knight, 2=rook, 3=queen) and press any key to continue...")
                    try:
                        poption = int(input(""))
                        if poption not in [0,1,2,3]:
                            raise ValueError()
                        else:
                            break
                    except Exception as e:
                        logging.info("Invalid option!")
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
        if poption is not None:
            if poption==0:
                state[new_coord] = 4+((state[coord]//7)*6)
            elif poption==1:
                state[new_coord] = 3+((state[coord]//7)*6)   
            elif poption==2:
                state[new_coord] = 2+((state[coord]//7)*6)   
            else:
                state[new_coord] = 5+((state[coord]//7)*6)   
        else:
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

def checkGameEvent(color, state, orientation, ep, castle):
    # is checked?
    checked = isChecked(color, state, orientation, ep, castle)
    # is stalemated?
    stalemated = isStalemated(color, state, orientation, ep, castle)
    if checked and not stalemated:
        logging.info('King {0} is checked!'.format(color))
    elif not checked and stalemated:
        logging.info('King {0} is stalemated! Draw!'.format(color))
        input("Press any key to exit game...")
        sys.exit()
    elif checked and stalemated:
        logging.info('Checkmate! Player {0} has won!'.format(("white" if color=="black" else "black")))
        input("Press any key to exit game...")
        sys.exit()
 
def main(args):  
    # init pygame
    pygame.init()
    # screen/window setup
    screen = pygame.display.set_mode(S_SIZE[args.size])
    pygame.display.set_caption("Simple Chess")
    # init background and state
    state = np.zeros((8,8),dtype=np.int)
    orientation = args.colour
    if orientation == "random":
        m = random.choice(["w","b"])
        orientation = "white" if m=="w" else "black"
    if orientation == "black":
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
    coord = (-1,-1)
    ep = None
    castle = [False]*6
    # draw initial board
    drawBoard(state, screen, chessbg, S_OFFSET[args.size], clock)
    while True: 
        if orientation == "black":
            if coord != (-1,-1):
                time.sleep(1)
            comp, pos = getRandomMove("white", state, orientation, ep, castle) 
            ep, coord, _ = applyMove(comp, pos, state, orientation, ep, castle, True)
            drawBoard(state, screen, chessbg, S_OFFSET[args.size], clock)
            # check for game event
            checkGameEvent("black", state, orientation, ep, castle)
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
                            ep, coord, moved = applyMove(coord, new_coord, state, orientation, ep, castle, False)
            drawBoard(state, screen, chessbg, S_OFFSET[args.size], clock)
            # check for game event
            checkGameEvent(("white" if orientation=="black" else "black"), state, orientation, ep, castle)
        moved = False
        if orientation == "white":
            time.sleep(1)
            comp, pos = getRandomMove("black", state, orientation, ep, castle) 
            ep, coord, _ = applyMove(comp, pos, state, orientation, ep, castle, True)
            drawBoard(state, screen, chessbg, S_OFFSET[args.size], clock)
            # check for game event
            checkGameEvent("white", state, orientation, ep, castle)
    # end game
    pygame.quit()

if __name__=='__main__':
    screensize = ["small", "medium", "large"]
    colour = ["black", "white", "random"]
    parser = argparse.ArgumentParser(description="Simple Chess") 
    parser.add_argument("-s", "--size", dest='size', default="medium", choices=screensize)
    parser.add_argument("-c", "--colour", dest="colour", default="random", choices=colour)
    parser.add_argument("-f", "--fps", dest="fps", type=int, default=60)
    args = parser.parse_args()
    main(args)
