import playingStrategies

# import random
import game
# The moves of player have the form (x,y), where y is the column number and x the row number (starting with 0)

def playerStrategy(game, state):
    cutOff = 2 
    captures = 0
    value, move = playingStrategies.h_alphabeta_search_adv(game,state,playingStrategies.cutoff_depth(cutOff))
   
    return move
    