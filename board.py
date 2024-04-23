# from collections import namedtuple, Counter, defaultdict
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt

import functools

cache = functools.lru_cache(10 ** 6)

### PREPARE THE BOARD ###
# Crea una figura e degli assi
# define the colors
# usiamo un colore più scuro per le dame
fScuro = 0.65 
colorX = (90/255,98/255,152/255)
colorK = (90/255*fScuro,98/255*fScuro,152/255*fScuro)
colorO = (203/255,70/255,55/255)
colorQ = (203/255*fScuro,70/255*fScuro,55/255*fScuro)
squareColor = (242/255,211/255,186/255)
# create a new figure
fig, ax = plt.subplots()
plt.ion()

# Manteniamo una copia del vecchio board per mostrare le variazioni delle mosse
oldBoard = None
lastMove = None

player1 = ""
player2 = ""

def initGraphicalBoard(game, p1="X", p2="O"):
    global player1, player2
    player1 = p1
    player2 = p2
    #plt.get_current_fig_manager().canvas.set_window_title('King and Courtesan')
    # draw the board background
    ax.set_facecolor((1,1,1))
    # set the limits of the axes
    ax.set_xlim([0, game.height])
    ax.set_ylim([0, game.width])

    # hide the tick labels
    #ax.set_xticklabels([])
    #ax.set_yticklabels([])

    # hide the axes
    ax.axis('off')

    # draw the squares on the board
    for (row,col) in game.squares:
        rect = plt.Rectangle((col, row), 1, 1, facecolor=squareColor, edgecolor=(0, 0, 0))
        ax.add_patch(rect)
    
    # add a title to the figure
    ax.set_title("King and Courtesan")
    
    # add player names
    ax.text(0.5, -0.1, f"Player blue: {player1} VS Player red: {player2}", transform=ax.transAxes, ha='center')
    
    plt.show()


# A board encodes a state of the game, in Hadron and similar board games
class Board(defaultdict):
    """A board has the player to move, a cached utility value,
    and a dict of {(x, y): player} entries, where player is 'X' or 'O'."""
    empty = ' '
    off = '#'

    def __init__(self, pos ={}, width=8, height=8, to_move=None,  **kwds):
        self.__dict__.update(width=width, height=height, to_move=to_move, **kwds)
        self.utility = 0
        self.to_move = to_move
        # update self with pos if pos is a dict
        if type(pos) == dict:
            self.update(pos)

    def new(self, changes: dict, to_move) -> 'Board':
        "Given a dict of {(x, y): contents} changes, return a new Board with the changes."
        board = Board(width=self.width, height=self.height, to_move=to_move)
        board.update(self)
        board.update(changes)
        board.utility = self.utility
        return board
    
    def occupiedPos(self,player=''):
        if player == '':
            player = self.to_move
        if player == 'X':
            c = ['x', 'K']
        else:
            c = ['o', 'Q']
        return {pos for pos in self if self[pos] in c}

    def __missing__(self, loc):
        x, y = loc
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.empty
        else:
            return self.off

    def __hash__(self):
        return hash(tuple(sorted(self.items()))) + hash(self.to_move)

    def __repr__(self):
        def row(x): return ' '.join(self[x, y] for y in range(self.height))

        return '\n'.join(map(row, range(self.width))) + '\n'

    def __reduce__(self):
        return (self.__class__, (self.width, self.height, self.to_move), None, None, iter(self.items()))



def draw_board(game,board,action=None,result=None):
    global oldBoard, lastMove

    if oldBoard is None:  # first call to draw_board
        # draw the board
        for (row,col) in board:
            if board[(row,col)] == 'x':
                circle = plt.Circle((col + 0.5, board.height - 1 - row + 0.5), 0.4, color=colorX)
            elif board[(row,col)] == 'o':
                circle = plt.Circle((col + 0.5, board.height - 1 - row + 0.5), 0.4, color=colorO)
            elif board[(row,col)] == 'K':
                circle = plt.Circle((col + 0.5, board.height - 1 - row + 0.5), 0.4, color=colorK)
            elif board[(row,col)] == 'Q':
                circle = plt.Circle((col + 0.5, board.height - 1 - row + 0.5), 0.4, color=colorQ)
            ax.add_patch(circle)
    else:
        move = {}
        move[action[1]]= ''
        move[action[2]]= ''
        for square in move:
            if square not in board and square not in oldBoard:
                continue
            if square in oldBoard and square in board and oldBoard[square] != board[square]: # square has changed            
                move[square] = board[square]
            elif square not in oldBoard and square in board: # square has been added
                            move[square] = board[square]
            #elif square in oldBoard and square not in board: # square has been removed
            #    move[square] = ''    # This is already set by default
            
        #rimuovi visualizzazione precedente mossa
        if lastMove is not None:
            for (row,col) in lastMove:
                rect = plt.Rectangle((col, board.height - 1 - row), 1, 1, facecolor=squareColor, edgecolor=(0, 0, 0))
                ax.add_patch(rect)
                circle = None
                if board[(row,col)] == 'x':
                # debug
                # print("col",col,"row",row,"board.height-1",board.height - 1)
                    circle = plt.Circle((col + 0.5, board.height - 1 - row + 0.5), 0.4, color=colorX)
                elif board[(row,col)] == 'o':
                    circle = plt.Circle((col + 0.5, board.height - 1 - row + 0.5), 0.4, color=colorO)
                elif board[(row,col)] == 'K':
                    circle = plt.Circle((col + 0.5, board.height - 1 - row + 0.5), 0.4, color=colorK)
                elif board[(row,col)] == 'Q':
                    circle = plt.Circle((col + 0.5, board.height - 1 - row + 0.5), 0.4, color=colorQ)
                if circle is not None:
                    ax.add_patch(circle)
        lastMove = move

        # draw the new move
        for (row,col) in move:
            modSquareColor = 'yellow'
            if action[3] == 'capturing' and row == action[2][0] and col == action[2][1]:
                if action[0] == 'X':
                    modSquareColor = colorO
                else:
                    modSquareColor = colorX
            rect = plt.Rectangle((col, board.height - 1 - row), 1, 1, facecolor=modSquareColor, edgecolor=(0, 0, 0))
            ax.add_patch(rect)
            circle = None
            if board[(row,col)] == 'x':
                # debug
                # print("col",col,"row",row,"board.height-1",board.height - 1)
                circle = plt.Circle((col + 0.5, board.height - 1 - row + 0.5), 0.4, color=colorX)
            elif board[(row,col)] == 'o':
                circle = plt.Circle((col + 0.5, board.height - 1 - row + 0.5), 0.4, color=colorO)
            elif board[(row,col)] == 'K':
                circle = plt.Circle((col + 0.5, board.height - 1 - row + 0.5), 0.4, color=colorK)
            elif board[(row,col)] == 'Q':
                circle = plt.Circle((col + 0.5, board.height - 1 - row + 0.5), 0.4, color=colorQ)
            if circle is not None:
                ax.add_patch(circle)
    
    oldBoard = board
    if result is not None:
        if result == 1:
            ax.text(0.5, -0.15, f"{player1} wins", transform=ax.transAxes, ha='center')
        elif result == -1:
            ax.text(0.5, -0.15, f"{player2} wins", transform=ax.transAxes, ha='center')
        else:
            ax.text(0.5, -0.15, "Draw", transform=ax.transAxes, ha='center')

    fig.canvas.draw()
    plt.pause(0.5)

  
