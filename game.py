import functools
cache = functools.lru_cache(10**6)

#from players import *

#import playingStrategies
import random
from board import Board,draw_board,initGraphicalBoard
import concurrent.futures
import time

import sys
#sys.path.append("Progetti studenti maggio 2024")


# EXAMPLE VERSION
# #######################
import playerExampleAlpha as playerXmodule
import playingStrategies as playerOmodule
# #######################


# King and Courtesan Game
# The moves of player have the form (y,x), where y is the column number and x the row number (starting with 0)
# In the vif
# alization, they are in the form (row, column) starting with 1.

class Game:
    """A game is similar to a problem, but it has a terminal test instead of
    a goal test, and a utility for each terminal state. To create a game,
    subclass this class and implement `actions`, `result`, `is_terminal`,
    and `utility`. You will also need to set the .initial attribute to the
    initial state; this can be done in the constructor."""

    def actions(self, state):
        """Return a collection of the allowable moves from this state."""
        raise NotImplementedError

    def result(self, state, move):
        """Return the state that results from making a move from a state."""
        raise NotImplementedError

    def is_terminal(self, state):
        """Return True if this is a final state for the game."""
        return not self.actions(state)

    def utility(self, state, player):
        """Return the value of this final state to player."""
        raise NotImplementedError

class KingCourt(Game):

    def __init__(self, height=8, width=8):
        self.height=height*2-1 #Immergiamo la scacchiera romboidale in un campo più grande quadrato
        self.width=width*2-1
        # Generiamo le caselle del rombo e anche le posizioni iniziali
        # Re e regina (cioè il re degli avversari) saranno collocati in (0,7) e (14,7) e all'inizio l'ottava riga (di indice 7) sarà libera 
        positions = {(0,7):'K',(14,7):'Q'}
        coda = [(0,7)]
        self.squares = set(coda)
        while len(coda)>0:
            #print(coda)
            p = coda.pop()
            if p[0] == height-1:
                continue
            c1 = (p[0]+1, p[1]-1)
            c2= (p[0]+1, p[1]+1)
            if c1 not in coda:
                if c1[0] < height-1:
                    positions.update({c1:'x'})
                coda.insert(0,c1)
                self.squares.update({c1})
                coda.insert(0,c1)
                self.squares.update({c1})
            if c2 not in coda:
                if c2[0] < height-1:
                    positions.update({c2:'x'})
                coda.insert(0,c2)
                self.squares.update({c2})
            
        coda = [(14,7)]
        self.squares.update({(14, 7)})
        while len(coda)>0:
            p = coda.pop()
            if p[0] == height:
                continue
            c1 = (p[0]-1, p[1]-1)
            c2 = (p[0]-1, p[1]+1)
            if c1 not in coda:
                if c1[0] >= height:
                    positions.update({c1:'o'})
                coda.insert(0,c1)
                self.squares.update({c1})
            if c2 not in coda:
                if c2[0] >= height:
                    positions.update({c2:'o'})
                coda.insert(0,c2)
                self.squares.update({c2})
            
        self.initial = Board(positions,height=self.height, width=self.width, to_move='X', utility=0)


    def actions(self, board):
        """Legal moves """
        freeCells=set(self.squares)-set(board)
        ret=set()
        player = board.to_move
        #opponent = 'O' if player == 'X' else 'X'
        occupied = board.occupiedPos(player)  # set of occupied positions from the player to move (according to the information in the board, you can also pass the player as parameter) 
        for (r,c) in occupied:
            possiblesquares = [(r-1,c-1),(r-1,c+1),(r-2,c),(r+2,c),(r+1,c+1),(r+1,c-1),(r,c-2),(r,c+2)]  # possible squares for the player to move
            for square in possiblesquares:
                if square not in self.squares:
                    continue
                action = [player,(r,c),square]
                ok = True
                if square not in occupied:
                    if square in freeCells:
                        if player == 'X' and square[0] <= r:
                            ok = False
                        if player == 'O' and square[0] >= r:
                            ok = False
                        action.append('nonCapturing')
                    else:
                        action.append('capturing')
                elif square in occupied:
                    if player == 'X' and (board[(r,c)] != 'K' or board[(r,c)] == 'K' and square[0] <= r):
                        ok = False
                    if player == 'O' and (board[(r,c)] != 'Q' or board[(r,c)] == 'Q' and square[0] >= r):
                        ok = False
                    action.append('exchange')
                else:
                    action.append('capturing')
                if ok:
                    ret.add(tuple(action))
                    #if len(action) < 4:
                    #    print(action)
        return ret
                

    def result(self, board, action):
        """Return the board that results from making a move from a state"""
        #print(action)
        player = action[0]
        squareIn = action[1]
        squareDest = action[2]
        moveType = action[3]
        opponent = 'O' if player == 'X' else 'X'
        opponentKing = 'Q' if player == 'X' else 'K'
        king = 'K' if player == 'X' else 'Q'
        checker = board[squareIn]

        goalSquare = (0,7) if player == 'O' else (14,7)
        win = False

        if board[squareDest] == opponentKing or (squareDest == goalSquare and checker == king):
                win = True

        board = board.new({squareDest: checker}, to_move=('O' if player == 'X' else 'X'))

        if moveType == 'nonCapturing' or moveType == 'capturing':
            del board[squareIn]
        else: # moveType == 'exchange'
            checkerModified = 'x' if checker == 'K' else 'o'
            board.update({squareIn:checkerModified})  
            
        board.utility = (0 if not win else +1 if player == 'X' else -1)
        return board


    def utility(self, board, player):
        """Return the value to player; 1 for win, -1 for loss, 0 otherwise."""
        return board.utility if player == 'X' else -board.utility

    def is_terminal(self, board):
        """A board is a terminal state if it is won"""
        return board.utility != 0 

    def display(self, board):
        print(board)



def play_game(game, verbose=False, passoPasso = False, timeout = 3):
    """Play a turn-taking game. `strategies` is a {player_name: function} dict,
    where function(state, game) is used to get the player's move."""
    state = game.initial
    number_of_move = 0
    move = None

    if verbose:
        print(state)

    initGraphicalBoard(game)
    draw_board(game,state)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    
        while not game.is_terminal(state):
            player = state.to_move
            number_of_move += 1
            available_moves = list(game.actions(state))
            trouble = False
            
            if player == 'X':
                playerResult = executor.submit(playerXmodule.playerStrategy, game, state)
            else:
                playerResult = executor.submit(playerOmodule.playerStrategy, game, state)
            try:
                move = playerResult.result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                print("La funzione è stata interrotta a causa del timeout")
                move = None
            #finally:
            #    executor.shutdown(wait=False)

            if move is None:
                print("Timeout, random choice for player ", player) 
                move = random.choice(available_moves)
            if move not in available_moves:
                print("Illegal move ", move, " by player ", player)
                move = random.choice(available_moves)

            state = game.result(state, move)
            if verbose:
                print('Player', player, 'move: ', move)
                print(state)

            draw_board(game,state,move)
            
            if game.is_terminal(state):
                print ("Result for player blue (X): ",game.utility(state,'X'))
                draw_board(game,state,move,game.utility(state,'X'))
                input("Press Enter to exit")
            else:
                draw_board(game,state,move)
            
            if passoPasso:
                scelta = input("Press Enter to continue (F to go fast, without stopping at each move) ")
                if scelta == 'F' or scelta == 'f':
                    passoPasso = False
            
    return state


#def random_player(game, state): return random.choice(list(game.actions(state)))

def player(search_algorithm):
    """A game player who uses the specified search algorithm"""
    return lambda game, state: search_algorithm(game, state)[1]


if __name__ == '__main__':
    game = KingCourt()
    play_game(game, verbose=True,passoPasso=True, timeout = 3)
    

