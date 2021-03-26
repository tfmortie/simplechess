"""
File containing code for main program.
Author: Thomas Mortier
Date: March 2021

TODO: 
    2) add motion constraints (incl. castling)
    3) add intelligence (idea: use different levels: free, low, medium, high, ...)
    4) add different modes (free -> no intelligence, just free movement, timer, etc.)
    5) improve GUI
"""
import sys
import pygame
import argparse
import random

import numpy as np

from logic import isValidComponentPosition

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
    coord = None
    while True:
        # listen for events
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
                        # check if move is valid
                        if isValidComponentPosition(coord, new_coord, state, gamemode):
                            state[new_coord] = state[coord]
                            state[coord] = 0 
                            coord = None
        # set background
        screen.blit(chessbg, (0,0))
        updateBoard(state, S_OFFSET[args.size], screen)
        # update screen
        pygame.display.update()
        # wait fps seconds
        clock.tick(args.fps)
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
