import math

infinity = math.inf

# ---------------------------------GLOBAL VARIABLES---------------------------------#
pawn4line = {
    0: 0,
    1: 0,
    2: 0,
    3: 0,
    4: 0,
    5: 0,
    6: 0,
    7: 0,  # Central line
    8: 7,
    9: 6,
    10: 5,
    11: 3,
    12: 2,
    13: 2,
    14: 1,
}

#These are the target positions we want to reach for check. Updated if we have a pawn near the opponent's king's outer circle.
checkObj_list = []

# These are the positions of pawns that are already in the opponent's king's outer circle that could potentially check.
check_list = []

possibleCheck = False
checkType1 = False
check = False

king_in_danger = False





# è la lista delle posizioni dell'intorno grande del re in modo che non si debbano calcolare ad ogni verifica di check ma si genera la lista ogni volta che il re viene spostato
encirclement_list = []

defensive_line = 9
kingAdv_position = (0, 7)
king_position = (14, 7)

# ---------------------------------------------------------------------------------#

# ---------------------------------AUXILIAR FUNCTIONS---------------------------------#


def cache1(function):
    "Like lru_cache(None), but only considers the first argument of function."
    cache = {}

    def wrapped(x, *args):
        if x not in cache:
            cache[x] = function(x, *args)
        return cache[x]

    return wrapped


def cutoff_depth(d):
    """A cutoff function that searches to depth d."""
    return lambda game, state, depth: depth > d


def updatePawn4line(move):
    if "exchange" not in move:
        pawn4line[move[2][0]] += 1
        pawn4line[move[1][0]] -= 1


def updateDefensiveLine(state, move, defensive_line):
    attacking_pawn_alive = 0
    for r in range(0, defensive_line):
        for c in range(7 - r, 7 + r + 1):
            if state[(r, c)] == "o":
                attacking_pawn_alive += 1
    if attacking_pawn_alive == 0 or pawn4line[defensive_line] == 0:
        defensive_line += 1
    return defensive_line


# Al seguente link è presente la spiegazione visiva: https://drive.google.com/file/d/1y0hljj_UofBwEVEe1YoHZgEH9wiXcpvg/view?usp=sharing
def isAPossibleCheck(state):

    global kingAdv_position
    global check
    global checkType1

    # Check if the opponent's king's surrounding area is empty, guaranteeing that an exchange is impossible.
    if (
        state[kingAdv_position[0] + 1, kingAdv_position[1] - 1] != "x"
        and state[kingAdv_position[0] + 1, kingAdv_position[1] + 1] != "x"
        and state[kingAdv_position[0] + 2, kingAdv_position[1]] != "x"
    ):

        # Controllo eventuale riguardo la propria mossa, se spostando la pedina siamo a rischio mangiata allora la mossa non è di scacco
        for element in encirclement_list:
            if state[element] == 'o':
                updateCheck(element)
                return True
    return False


def updateCheck(pawn_position):
    global kingAdv_position
    global check
    global checkType1
    global checkObj_list
    # Verifichiamo se siamo nell'intorno
    # Se l'intorno del re è vuoto (verificato nella chiamata isAPossibleCheck) e non siamo in posizione di rischio di mangiata allora abbiamo 3 possibili posizioni
    # che ci permetterebbero di raggiungere lo scacco
    check_list.append(pawn_position)

    if (
        pawn_position[0] == kingAdv_position[0] + 4
        and pawn_position[1] == kingAdv_position[1]
        ):
        checkObj_list.append((pawn_position[0] - 2, pawn_position[1]))
        checkType1 = True

    # Stiamo salendo di uno scalino verso destra per il controllo
    elif (
        pawn_position[0] == kingAdv_position[0] + 3
        and pawn_position[1] > kingAdv_position[1] + 1
    ):
        checkObj_list.append((pawn_position[0] - 1, pawn_position[1] - 1))
        checkObj_list.append((pawn_position[0] - 2, pawn_position[1]))
        checkType1 = True

    # Siamo saliti di un altro scalino verso destra
    elif (
        pawn_position[0] == kingAdv_position[0] + 2
        and pawn_position[1] == kingAdv_position[1] + 2
    ):
        checkObj_list.append((pawn_position[0], pawn_position[1] - 2))
        checkObj_list.append((pawn_position[0] - 1, pawn_position[1] - 1))
        checkType1 = True

    # Ci spostiamo verso sinistra
    elif (
        pawn_position[0] == kingAdv_position[0] + 3
        and pawn_position[1] == kingAdv_position[1] - 1
    ):
        checkObj_list.append((pawn_position[0] - 1, pawn_position[1] + 1))
        checkObj_list.append((pawn_position[0] - 2, pawn_position[1]))
        checkType1 = True

    # Siamo saliti di un altro scalino verso sinistra
    elif (
        pawn_position[0] == kingAdv_position[0] + 2
        and pawn_position[1] == kingAdv_position[1] - 2
    ):
        checkObj_list.append((pawn_position[0], pawn_position[1] + 2))
        checkObj_list.append((pawn_position[0] - 1, pawn_position[1] + 1))
        checkType1 = True


def updateEncirclementList():
    global kingAdv_position
    # point1 = (kingAdv_position[0],kingAdv_position[1]-4)
    #point2 = (kingAdv_position[0] - 1, kingAdv_position[1] - 3)
    point3 = (kingAdv_position[0] + 2, kingAdv_position[1] - 2)
    point4 = (kingAdv_position[0] + 3, kingAdv_position[1] - 1)
    point5 = (kingAdv_position[0] + 4, kingAdv_position[1])
    point6 = (kingAdv_position[0] + 3, kingAdv_position[1] + 1)
    point7 = (kingAdv_position[0] + 2, kingAdv_position[1] + 2)

    encirclement_list.append(point3)
    encirclement_list.append(point4)
    encirclement_list.append(point5)
    encirclement_list.append(point6)
    encirclement_list.append(point7)


def testCheck(move, state):
    global kingAdv_position
    global check
    global checkType1
    global checkObj_list

    start = move[0]
    arrival = move[1]

    # Si controlla se entrambe le pedine richieste sono in check
    if checkType1:
        pawn_control1 = False
        pawn_control2 = False
        for element in check_list:
            if state[(element[0], element[1])] == "o":
                pawn_control1 = True
        for element in checkObj_list:
            if state[(element[0], element[1])] == "o":
                pawn_control2 = True
                break
        if pawn_control1 and pawn_control2:
            check = True


# ------------------------------------------------------------------------------------#

dynamic_c = 0
captures = 0
initial_adv_piece_count = 28
current_pieces_adv=28
flag = False  #la flag serve se con il cutoff alto puo mangiare il re ma non lo fa, riportando di fatto il cutoff a 0 

def h_alphabeta_search(game, state, cutoff=cutoff_depth(dynamic_c)):
    """Search game to determine best action; use alpha-beta pruning.

    As in [Figure 5.7], this version searches all the way to the leaves.

    Tracks considered moves and their utilities for printing.
    Prints considered moves in ascending order of utility.
    Always chooses the move with the highest utility.
    """
    
    player = state.to_move
   
    global captures
    global initial_adv_piece_count
    global current_pieces_adv
    global kingAdv_position
    global check
    global checkType1
    global possibleCheck
    global king_in_danger
    global dynamic_c
    considered_moves = []  #A list to store (move, utility) tuples, essentially a list of considered moves. 
    updateEncirclementList()
   
    
    current_pieces_adv = initial_adv_piece_count-captures
  
    dynamic_c = dynamic_cutoff(current_pieces_adv)
    

    @cache1
    def max_value(state, player, alpha, beta, depth, action, defensive_line):
        global possibleCheck
        v2 = -infinity
        if game.is_terminal(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            return h(state, action), None
        v, move = -infinity, None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a), player, alpha, beta, depth + 1, a, defensive_line)
            if v2 > v:
                v, move = v2, a
                alpha = max(alpha, v)

            if v >= beta:
                return v, move
            if state.to_move == "O":
                considered_moves.append((a, v2))  # Add the move to the list with its respective utility.
        updatePawn4line(move)
        defensive_line = updateDefensiveLine(state, move, defensive_line)

        testCheck(move, state)

        return v, move

    @cache1
    def min_value(state, player, alpha, beta, depth, action, defensive_line):
        v2 = -infinity
        if game.is_terminal(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            return h(state, action), None
        v, move = +infinity, None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a), player, alpha, beta, depth + 1, a, defensive_line)
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, move
            if state.to_move == "O":
                considered_moves.append((a, v2))  # Add the move to the list with its respective utility.
        return v, move

    if isAPossibleCheck(state):
        possibleCheck=True

    if checkType1:
        for position in check_list:
            if state[position] != "o":
                checkType1 = False
                check_list.clear()
                checkObj_list.clear()

    if check or checkType1:
        if (state[kingAdv_position[0] + 1, kingAdv_position[1] + 1] == "x"
            or state[kingAdv_position[0] + 2, kingAdv_position[1]] == "x"
            or state[kingAdv_position[0] + 1, kingAdv_position[1] - 1] == "x"):
            checkType1 = False
            possibleCheck = False
            check = False
            encirclement_list.clear()
            check_list.clear()
            checkObj_list.clear()
        else:
            for element in check_list:
                if state[element] != "o":
                    checkType1 = False
                    possibleCheck = False
                    check = False
                    encirclement_list.clear()
                    check_list.clear()
                    checkObj_list.clear()
                    checkObj_list.clear()

    # Update Adv King position
    if state[kingAdv_position] != "K":
        checkType1 = False
        possibleCheck = False
        check = False
        encirclement_list.clear()
        check_list.clear()
        checkObj_list.clear()

        possible_position1 = (
            kingAdv_position[0] + 2,
            kingAdv_position[1],
        )  # Forward movement of the King
        possible_position2 = (
            kingAdv_position[0] + 1,
            kingAdv_position[1] + 1,
        )  # Right movement of the King
        possible_position3 = (
            kingAdv_position[0] + 1,
            kingAdv_position[1] - 1,
        )  # Left movement of the King
        possible_position4 = (kingAdv_position[0], kingAdv_position[1] - 2)
        possible_position5 = (kingAdv_position[0], kingAdv_position[1] + 2)
        possible_position6 = (kingAdv_position[0] - 1, kingAdv_position[1] - 1)
        possible_position7 = (kingAdv_position[0] - 1, kingAdv_position[1] + 1)
        possible_position8 = (kingAdv_position[0] - 2, kingAdv_position[1])

        if state[possible_position1] == "K":
            kingAdv_position = possible_position1
        elif state[possible_position2] == "K":
            kingAdv_position = possible_position2
        elif state[possible_position3] == "K":
            kingAdv_position = possible_position3
        elif state[possible_position4] == "K":
            kingAdv_position = possible_position4
        elif state[possible_position5] == "K":
            kingAdv_position = possible_position5
        elif state[possible_position6] == "K":
            kingAdv_position = possible_position6
        elif state[possible_position7] == "K":
            kingAdv_position = possible_position7
        elif state[possible_position8] == "K":
            kingAdv_position = possible_position8

        updateEncirclementList()

    if (
        state[king_position[0] - 2, king_position[1]] == "x"
        or state[king_position[0] - 1, king_position[1] + 1] == "x"
        or state[king_position[0], king_position[1] + 2] == "x"
        or state[king_position[0] + 1, king_position[1] + 1] == "x"
        or state[king_position[0] + 2, king_position[1]] == "x"
        or state[king_position[0] + 1, king_position[1] - 1] == "x"
        or state[king_position[0], king_position[1] - 2] == "x"
        or state[king_position[0] - 1, king_position[1] - 1] == "x"
    ):
        king_in_danger = True
    else:
        king_in_danger = False

    utility, chosen_move = max_value(state, player, -infinity, +infinity, 0, None, defensive_line) 

        
    sorted_moves = sorted(considered_moves, key=lambda x: x[1])   

    # Print considered moves and utilities
    """print("Considered Moves and Utilities [Sorted by utility]:")
    for move, utility in sorted_moves:
        print(f"Move: {move}, Utility: {utility}")"""

    print("Number of considered moves: ", len(considered_moves))
    considered_moves = []
    # Print chosen move and utility
    print(f"\nChosen Move: {chosen_move}, Utility: {utility}") 
    
    if 'capturing' in chosen_move: 
        captures+=1
        print('capture completed -> captures: ', captures) 
        
    print("\nCUTOFF: " , dynamic_c )  
    
    print("current adv pieces : ", current_pieces_adv)

    return utility, chosen_move


def suicide(state,arriving_r,arriving_c):
    adv_pawns = ['x','K']
    if state[(arriving_r -2, arriving_c)] in adv_pawns or state[(arriving_r-1, arriving_c-1)]  in adv_pawns or state[(arriving_r-1, arriving_c+1)]  in adv_pawns or state[(arriving_r,arriving_c+2)] in adv_pawns or state[(arriving_r,arriving_c-2)] in adv_pawns: 
        return True
    return False

def playerStrategy(game, state):
    global current_pieces_adv
    global flag
    value, move = h_alphabeta_search(game,state,cutoff_depth(dynamic_cutoff(current_pieces_adv)))
    if value >0.85 and 'capturing' not in move:
        flag = True
        print("\n MOSSA FLAGGATA LESGOSKI LESSGO...")
        value, move = h_alphabeta_search(game,state,cutoff_depth(dynamic_cutoff(current_pieces_adv)))

    return move

    

def dynamic_cutoff(current_pieces_adv):
    global initial_adv_piece_count
    global flag
    if flag:
        flag = False
        return 0
    else:
        if current_pieces_adv <= initial_adv_piece_count and current_pieces_adv > initial_adv_piece_count // 3 :  
            return 0
        elif current_pieces_adv <= initial_adv_piece_count // 3 and current_pieces_adv > initial_adv_piece_count//4:
            return 2
        elif current_pieces_adv <= initial_adv_piece_count // 4:
            return 4
    return 1 
        

#______________________________HEURISTIC________________________________________________________________


def h(state, action):
    start = action[1]
    arrival = action[2]

    global kingAdv_position
    global king_in_danger
    global check
    global possibleCheck
    global checkType1
    global current_pieces_adv


    advKingDistance = abs(arrival[0] - kingAdv_position[0]) + abs(
        arrival[1] - kingAdv_position[1]
    )
    kingDistance = abs(arrival[0] - king_position[0]) + abs(
        arrival[1] - king_position[1]
    )

    if advKingDistance == 0:
        return 1

    #Handling the movement of pawns that are already in a check position (if they move, check would be lost)
    if start in check_list:
        return 0

    if checkType1:
        if start in checkObj_list:
            return 0

    if "capturing" in action:  # Capturing attacking zone

        if king_in_danger:
            return 0.98
                

        #Favor a move that guarantees a type 1 check / Having this move implies that you are in a checkmate situation        
        if checkType1:
            if arrival in checkObj_list:
                for element in check_list:
                    if state[element]=='o':
                        return 0.95
                return 0

        #Check for a possible check
        if arrival[0] <= defensive_line - 3:
            if arrival[0] > start[0]:
                return 0.9 / advKingDistance
            elif arrival[0] == start[0]:
                return 0.95 / advKingDistance
            else:
                return 0.7 / advKingDistance  #forward
            
        else:  # Capturing in defensive zone
            if arrival[0] > start[0]:  # Back capture
                return 0.91
            elif arrival[0] == start[0]:  # Horizontal capture
                return 0.90
            elif (start[0] == arrival[0] + 1 and arrival[1] - 1 == start[1]) or (
                start[0] == arrival[0] + 1 and arrival[1] + 1 == start[1]
            ):
                return 0.85  # Capture forward if the opponent's pawn is in front, in the upper right or upper left position
            else:
                return 0.45 / advKingDistance  # To capture two squares forward

    elif "nonCapturing" in action:
    
        #Favor a move that guarantees a type 1 check / Having this move implies that you are in a checkmate situation        
        if checkType1:
            if arrival in checkObj_list:
                for element in check_list:
                    if state[element]=='o':
                        return 0.92//advKingDistance
                return 0

        minimumDistance = math.inf
        if not possibleCheck:
            minimumDistance = advKingDistance
        else:
            if start in checkObj_list:
                return 0

            for element in checkObj_list:
                tmp = abs(start[0] - element[0]) + abs(start[1] - element[1])
                if minimumDistance > tmp:
                    minimumDistance = tmp

            if minimumDistance == math.inf:
                for element in encirclement_list:
                    tmp = abs(start[0] - element[0]) + abs(start[1] - element[1])
                    if minimumDistance > tmp:
                        minimumDistance = tmp

        if suicide(state, arrival[0], arrival[1]):  
            return -0.91
        elif arrival[0]>=defensive_line:
            return 0.01/advKingDistance
        elif arrival[0]<defensive_line: 
            return 0.02/advKingDistance  #It is weighted to 'force' the encirclement of the opponent's king
         
        
    #2nd GOAL 
    elif ("exchange" in action) and (current_pieces_adv <= initial_adv_piece_count//6):
        if (arrival[0]<defensive_line):
            return 0.1/advKingDistance 
        elif(arrival[0]>=defensive_line):
            #king to his pawns
            if state[(arrival[0] -2, arrival[1])] == 'o' or state[(arrival[0]-1, arrival[1]-1)] =='o' or state[(arrival[0]-1, arrival[1]+1)]=='o' or state[(arrival[0], arrival[1]+2)]=='o' or state[(arrival[0],arrival[1]-2)]=='o': 
                return 0.15
            else:
                return 0.01/advKingDistance
        
    return 0


#----------------------------------------------------------------AVVERSARIO 

def h_alphabeta_search_adv(game, state, cutoff=cutoff_depth(2)):
    """Search game to determine best action; use alpha-beta pruning.
    As in [Figure 5.7], this version searches all the way to the leaves."""

    player = state.to_move

    @cache1
    def max_value(state, alpha, beta, depth):
        if game.is_terminal(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            return h_adv(state, player), None
        v, move = -infinity, None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a), alpha, beta, depth + 1)
            if v2 > v:
                v, move = v2, a
                alpha = max(alpha, v)
            if v >= beta:
                return v, move
        return v, move

    @cache1
    def min_value(state, alpha, beta, depth):
        if game.is_terminal(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            return h_adv(state, player), None
        v, move = +infinity, None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a), alpha, beta, depth + 1)
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, move
        return v, move

    return max_value(state, -infinity, +infinity, 0)


def h_adv(board, player):
    return 0