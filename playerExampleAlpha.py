import playingStrategies

# import random
import game

# The moves of player have the form (x,y), where y is the column number and x the row number (starting with 0)


def playerStrategy(game, state):
    cutOff = dynamic_cutoff(game, state)
    value, move = playingStrategies.h_alphabeta_search(
        game,
        state,
        playingStrategies.cutoff_depth(cutOff),
    )
    
def dynamic_cutoff(game, state):
    
    return 0; #TODO
    initial_piece_count = len(game.initial.occupiedPos(state.to_move))
    total_pieces = len(state.occupiedPos(state.to_move))
    if total_pieces == initial_piece_count:
        return 0
    elif total_pieces <= initial_piece_count and total_pieces > initial_piece_count // 2:
        return 2
    else:
        return 4


    return move
