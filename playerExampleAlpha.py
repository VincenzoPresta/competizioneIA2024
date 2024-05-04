import playingStrategies

# import random
import game
# The moves of player have the form (x,y), where y is the column number and x the row number (starting with 0)

def playerStrategy(game, state):
    #cutOff = 0 
    captures = 0
    value, move = playingStrategies.h_alphabeta_search(game,state,dynamic_cutoff(game,state,captures))
    if"capturing" in move: 
         captures = captures + 1
   
    return move
    

def dynamic_cutoff(game, state, captures):
    initial_piece_count_adv = len(game.initial.occupiedPos(state.to_move))
    total_pieces_adv = initial_piece_count_adv-captures
    print("\n Total pieces: ", total_pieces_adv,)
    if total_pieces_adv <= initial_piece_count_adv:
        return 0
    elif total_pieces_adv <= initial_piece_count_adv // 2:
        print("\nCAMBIO CUTOFF ")
        return 2
    return 1
        
