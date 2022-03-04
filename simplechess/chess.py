"""
File containing code for main program.
Author: Thomas Mortier
Date: March 2021

TODO: 
    * (E) Additional GUI features: 
        * logging via GUI (eg. window) 
        * arguments via menu instead of command-line
"""
import sys
import os
import pygame
import argparse
import random
import time
import threading

import numpy as np

from simplechess.logic import isValidComponentPosition, isChecked, isStalemated
from simplechess.engine import RandomEngine, ABPEngine
from threading import Timer

S_OFFSET = {
    "small": (23,47,47.5),
    "medium": (34,67,71),
    "large": (45,91,95)}

S_SIZE = {
    "small": (400,400),
    "medium": (600,600),
    "large": (800,800)}

S_PSIZE = {
    "small": (30,30),
    "medium": (50,50),
    "large": (65,65)}

S_TEXTSIZE = {
    "small": (15, 2, 10),
    "medium": (24, 5, 13),
    "large": (32, 8, 16)
}

IND_2_P = ["bpawn", "brook", "bknight", "bbishop", "bqueen", "bking", "wpawn", "wrook", "wknight", "wbishop", "wqueen", "wking"]

P_SPRITE = {}

class Clock:
    def __init__(self, timeout, tevent, callback):
        self.timer = Timer(timeout, callback, [tevent])
        self.start_time = None
        self.cancel_time = None
        self.timeout = timeout
        self.tevent = tevent
        self.callback = callback

    def cancel(self):
        self.timer.cancel()

    def start(self):
        self.start_time = time.time()
        self.timer.start()

    def pause(self):
        self.cancel_time = time.time()
        self.cancel()

    def resume(self):
        self.timeout = self.get_remaining_time()
        self.timer = Timer(self.timeout, self.callback, [self.tevent])
        self.start_time = time.time()
        self.timer.start()
        self.cancel_time = None

    def get_remaining_time(self):
        if not self.tevent.is_set():
            if self.cancel_time is not None and self.start_time is not None:
                return self.timeout - (self.cancel_time - self.start_time)
            else:
                if self.cancel_time is None and self.start_time is None:
                    return self.timeout
                else:
                    return self.timeout - (time.time() - self.start_time)
        else:
            return 0

def logConsole(s):
    sys.stdout.write(s)
    sys.stdout.write('\n')
    sys.stdout.flush()

def initSprites(args):
    global P_SPRITE
    P_SPRITE = {
        "bpawn": pygame.transform.scale(pygame.image.load("simplechess/assets/b_pawn.png"), S_PSIZE[args.size]),
        "brook": pygame.transform.scale(pygame.image.load("simplechess/assets/b_rook.png"), S_PSIZE[args.size]),
        "bknight": pygame.transform.scale(pygame.image.load("simplechess/assets/b_knight.png"), S_PSIZE[args.size]),
        "bbishop": pygame.transform.scale(pygame.image.load("simplechess/assets/b_bishop.png"), S_PSIZE[args.size]),
        "bqueen": pygame.transform.scale(pygame.image.load("simplechess/assets/b_queen.png"), S_PSIZE[args.size]),
        "bking": pygame.transform.scale(pygame.image.load("simplechess/assets/b_king.png"), S_PSIZE[args.size]),
        "wpawn": pygame.transform.scale(pygame.image.load("simplechess/assets/w_pawn.png"), S_PSIZE[args.size]),
        "wrook": pygame.transform.scale(pygame.image.load("simplechess/assets/w_rook.png"), S_PSIZE[args.size]),
        "wknight": pygame.transform.scale(pygame.image.load("simplechess/assets/w_knight.png"), S_PSIZE[args.size]),
        "wbishop": pygame.transform.scale(pygame.image.load("simplechess/assets/w_bishop.png"), S_PSIZE[args.size]),
        "wqueen": pygame.transform.scale(pygame.image.load("simplechess/assets/w_queen.png"), S_PSIZE[args.size]),
        "wking": pygame.transform.scale(pygame.image.load("simplechess/assets/w_king.png"), S_PSIZE[args.size])}

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

def applyMove(coord, new_coord, state, score, orientation, ep, castle, opponent, engine):
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
            ep = list(new_coord)
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
                poption = engine.getPromotion()
            else:
                while True:
                    logConsole("Pawn promotion! Enter option (0=bishop, 1=knight, 2=rook, 3=queen) and press any key to continue...")
                    try:
                        poption = int(input(""))
                        if poption not in [0,1,2,3]:
                            raise ValueError()
                        else:
                            break
                    except Exception as e:
                        logConsole("Invalid option!")
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
        # check if piece is captured
        if state[new_coord] != 0:
            # get points
            points = 0
            if state[new_coord] in [1,7]:
                points = 1
            elif state[new_coord] in [2,8]:
                points = 5
            elif state[new_coord] in [5,11]:
                points = 9
            else:
                points = 3
            if opponent:
                score[1] += points
            else:
                score[0] += points
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

def drawBoard(args, state, screen, chessbg, offs, gameclock, clocks, score):
    screen.fill(pygame.Color("black"))
    # set background
    xoff = S_SIZE[args.size][0]//12
    screen.blit(chessbg, (0,xoff))
    updateBoard(state, S_OFFSET[args.size], screen)
    # create font instance for game info
    font = pygame.font.Font(pygame.font.get_default_font(), S_TEXTSIZE[args.size][0])
    # print info opponent
    info_opponent = str(time.strftime('%H:%M:%S', time.gmtime(clocks[1].get_remaining_time())))+"   ({0})".format(score[1])
    text_surface = font.render(info_opponent, False, (255, 255, 255))
    screen.blit(text_surface, dest=(S_TEXTSIZE[args.size][1], S_TEXTSIZE[args.size][2]))
    # print info player
    info_player = str(time.strftime('%H:%M:%S', time.gmtime(clocks[0].get_remaining_time())))+"   ({0})".format(score[0])
    text_surface = font.render(info_player, False, (255, 255, 255))
    screen.blit(text_surface, dest=(S_TEXTSIZE[args.size][1],S_SIZE[args.size][0]+xoff+S_TEXTSIZE[args.size][2]))
    # update screen
    pygame.display.update()
    # wait fps seconds
    gameclock.tick(args.fps)

def checkGameEvent(color, state, orientation, ep, castle, clocks):
    # is checked?
    checked = isChecked(color, state, orientation, ep, castle)
    # is stalemated?
    stalemated = isStalemated(color, state, orientation, ep, castle)
    if checked and not stalemated:
        logConsole('King {0} is checked!'.format(color))
    elif not checked and stalemated:
        clocks[0].cancel()
        clocks[1].cancel()
        logConsole('King {0} is stalemated! Draw!'.format(color))
        input("Press any key to exit game...")
        sys.exit()
    elif checked and stalemated:
        clocks[0].cancel()
        clocks[1].cancel()
        logConsole('Checkmate! Player {0} has won!'.format(("white" if color=="black" else "black")))
        input("Press any key to exit game...")
        sys.exit() 

def main(args):  
    # welcome message
    logConsole("\n--------------------\n| SIMPLE CHESS v1.0 |\n--------------------\n\n")
    # init pygame
    pygame.init()
    # screen/window setup
    size_screen = (S_SIZE[args.size][0], S_SIZE[args.size][0]+(S_SIZE[args.size][0]//6))
    screen = pygame.display.set_mode((size_screen))
    pygame.display.set_caption("Simple Chess")
    # init background and state
    state = np.zeros((8,8),dtype=np.int)
    orientation = args.colour
    if orientation == "random":
        m = random.choice(["w","b"])
        orientation = "white" if m=="w" else "black"
    if orientation == "black":
        chessbg = pygame.image.load("simplechess/assets/backgroundb.png")
        # init pawns
        state[6,:] = np.ones(8)
        state[1,:] = np.ones(8)*7
        # init border ranks
        state[7,:] = np.array([2,3,4,6,5,4,3,2])
        state[0,:] = np.array([8,9,10,12,11,10,9,8])
    else:
        chessbg = pygame.image.load("simplechess/assets/backgroundw.png")
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
    gameclock = pygame.time.Clock()
    # init state vars
    score = [0, 0]
    moved = False
    coord = (-1,-1)
    ep = None
    castle = [False]*6
    # init game engine
    if args.level == 0:
        engine = RandomEngine(("white" if orientation=="black" else "black"), orientation)
    else:
        engine = ABPEngine(("white" if orientation=="black" else "black"), orientation, args.level)
    # init chess clocks
    clock_player_exceeded = threading.Event()
    clock_opponent_exceeded = threading.Event()
    clock_player = Clock(args.timeout*60, clock_player_exceeded, lambda x: x.set())
    clock_opponent = Clock(args.timeout*60, clock_opponent_exceeded, lambda x: x.set())
    # start the clocks
    if orientation=="black":
        clock_opponent.start()
    else:
        clock_player.start()
    # draw initial board
    drawBoard(args, state, screen, chessbg, S_OFFSET[args.size], gameclock, [clock_player, clock_opponent], score)
    # game loop
    while True:   
        if orientation == "black":
            if coord != (-1,-1):
                time.sleep(1)
            comp, pos = engine.getMove(state, score, ep, castle)
            ep, coord, _ = applyMove(comp, pos, state, score, orientation, ep, castle, True, engine)
            drawBoard(args, state, screen, chessbg, S_OFFSET[args.size], gameclock, [clock_player, clock_opponent], score)
            # check for game event
            checkGameEvent("black", state, orientation, ep, castle, [clock_player, clock_opponent])
            clock_opponent.pause()
            clock_player.resume()
        while not moved and not clock_opponent_exceeded.is_set() and not clock_player_exceeded.is_set():
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    clock_player.cancel()
                    clock_opponent.cancel()
                    sys.exit();
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
                            ep, coord, moved = applyMove(coord, new_coord, state, score, orientation, ep, castle, False, engine)
            drawBoard(args, state, screen, chessbg, S_OFFSET[args.size], gameclock, [clock_player, clock_opponent], score)
            # check for game event
            checkGameEvent(("white" if orientation=="black" else "black"), state, orientation, ep, castle, [clock_player, clock_opponent])
        # check if loop was terminated due to exceeded clocks
        if clock_player_exceeded.is_set():
            clock_opponent.cancel()
            clock_player.cancel()
            logConsole('King {0} won in time!'.format(("white" if orientation=="black" else "black")))
            input("Press any key to exit game...")
            sys.exit()
        elif clock_opponent_exceeded.is_set():
            clock_opponent.cancel()
            clock_player.cancel()
            logConsole('King {0} won in time!'.format(orientation))
            input("Press any key to exit game...")
            sys.exit()
        else:
            # pause clock of player
            clock_player.pause()
            clock_opponent.resume()
            moved = False
            if orientation == "white":
                time.sleep(1)
                comp, pos = engine.getMove(state, score, ep, castle)
                ep, coord, _ = applyMove(comp, pos, state, score, orientation, ep, castle, True, engine)
                drawBoard(args, state, screen, chessbg, S_OFFSET[args.size], gameclock, [clock_player, clock_opponent], score)
                # check for game event
                checkGameEvent("white", state, orientation, ep, castle, [clock_player, clock_opponent])
                clock_opponent.pause()
                clock_player.resume()
    # end game
    pygame.quit()

if __name__=='__main__':
    screensize = ["small", "medium", "large"]
    colour = ["black", "white", "random"]
    parser = argparse.ArgumentParser(description="Simple Chess") 
    parser.add_argument("-l", "--level", dest="level", type=int, default=0)
    parser.add_argument("-t", "--timer", dest="timeout", type=int, default=10)
    parser.add_argument("-s", "--size", dest='size', default="medium", choices=screensize)
    parser.add_argument("-c", "--colour", dest="colour", default="random", choices=colour)
    parser.add_argument("-f", "--fps", dest="fps", type=int, default=60)
    args = parser.parse_args()
    main(args)
