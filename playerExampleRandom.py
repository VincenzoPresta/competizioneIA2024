
#import playingStrategies
import random
import game
#from board import Board,draw_board
#import multiprocessing
#import time

# Hadron Game
# The moves of player have the form (y,x), where y is the column number and x the row number (starting with 0)
# In the visualization, they are in the form (row, column) starting with 1.

# If it receives - 1 as the number of moves, then the game is finished



# The third argument is for debugging (it's a log of choices)
def playerStrategy (game,state):
    return random.choice(list(game.actions(state)))


