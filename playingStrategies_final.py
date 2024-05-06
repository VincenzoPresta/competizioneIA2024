import math

infinity = math.inf

#falco - fortugno - fusto - gigliotti

# ---------------------------------GLOBAL VARIABLES---------------------------------#
pawn4line_O = {
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
    11: 4,
    12: 3,
    13: 2,
    14: 1,
}

pawn4line_X = {
    0: 1,
    1: 2,
    2: 3,
    3: 4,
    4: 5,
    5: 5,
    6: 7,
    7: 0, 
    8: 0,
    9: 0,
    10: 0,
    11: 0,
    12: 0,
    13: 0, 
    14: 0
}


#These are the target positions we want to reach for check. Updated if we have a pawn near the opponent's king's outer circle.
checkObj_list = []

# These are the positions of pawns that are already in the opponent's king's outer circle that could potentially check.
check_list = []

possibleCheck = False
checkType1 = False
check = False

king_in_danger = False

convergent_cutoff = True
dynamic_c = 0
captures = 0

initial_adv_piece_count = 28
current_pieces_adv=28


encirclement_list = []

defensive_line_O = 9
defensive_line_X = 5

pos_kingO = (14, 7)
pos_kingX = (0, 7) 

# ---------------------------------------------------------------------------------#

# ---------------------------------AUXILIAR FUNCTIONS---------------------------------#

def king_suicide(player, state, starting_r, starting_c, arriving_r, arriving_c):
    if player =='O':
        adv_pawns = ['x','K']
        if state [(starting_r, starting_c)] =='Q' and (state[(arriving_r -2, arriving_c)] in adv_pawns or state[(arriving_r-1, arriving_c-1)]  in adv_pawns or state[(arriving_r-1, arriving_c+1)]  in adv_pawns or state[(arriving_r,arriving_c+2)] in adv_pawns or state[(arriving_r,arriving_c-2)] in adv_pawns): 
          
            return True
        return False
    else:
        adv_pawns = ['o','Q']
        if state [(starting_r, starting_c)] =='K' and (state[(arriving_r +2, arriving_c)] in adv_pawns or state[(arriving_r+1, arriving_c-1)]  in adv_pawns or state[(arriving_r+1, arriving_c+1)]  in adv_pawns or state[(arriving_r,arriving_c+2)] in adv_pawns or state[(arriving_r,arriving_c-2)] in adv_pawns): 
            return True
        return False

def suicide(player, state, arriving_r, arriving_c): 
    global checkType1
    if checkType1:
        return False
    if player == "O":
        adv_pawns = ['x','K']
        if state[(arriving_r -2, arriving_c)] in adv_pawns or state[(arriving_r-1, arriving_c-1)]  in adv_pawns or state[(arriving_r-1, arriving_c+1)]  in adv_pawns or state[(arriving_r, arriving_c+2)] in adv_pawns or state[(arriving_r, arriving_c-2)] in adv_pawns: 
            return True
    else:
        adv_pawns = ['o','Q']
        if state[(arriving_r + 2, arriving_c)] in adv_pawns or state[(arriving_r + 1, arriving_c-1)]  in adv_pawns or state[(arriving_r + 1, arriving_c+1)]  in adv_pawns or state[(arriving_r, arriving_c+2)] in adv_pawns or state[(arriving_r, arriving_c-2)] in adv_pawns:
            return True
    return False

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


def updatePawn4line(move,player):
    if "exchange" not in move:
        if player == "O":
            pawn4line_O[move[2][0]] += 1
            pawn4line_O[move[1][0]] -= 1
        else:
            pawn4line_X[move[2][0]] += 1
            pawn4line_X[move[1][0]] -= 1

def updateDefensiveLine(player, state, defensive_line):
    attacking_pawn_alive = 0
    if player == 'O':
        for r in range(0, defensive_line):
            for c in range(0,14):
                if state[(r, c)] == "o":
                    attacking_pawn_alive += 1
        if attacking_pawn_alive == 0 or pawn4line_O[defensive_line] == 0:
            defensive_line += 1
        return defensive_line
    else:
        for r in range(defensive_line, 14):
            for c in range(0,14):
                if state[(r, c)] == "o":
                    attacking_pawn_alive += 1
        if attacking_pawn_alive == 0 or pawn4line_X[defensive_line] == 0:
            defensive_line += 1
        return defensive_line

def isAPossibleCheck(state,player):

    global pos_kingX
    global check
    global checkType1

    if player=='O':
        if (
            state[pos_kingX[0] + 1, pos_kingX[1] - 1] != "x"
            and state[pos_kingX[0] + 1, pos_kingX[1] + 1] != "x"
            and state[pos_kingX[0] + 2, pos_kingX[1]] != "x"
        ):

            # Controllo eventuale riguardo la propria mossa, se spostando la pedina siamo a rischio mangiata allora la mossa non è di scacco
            for element in encirclement_list:
                if state[element] == 'o':
                    updateCheck(element, player)
                    return True
        return False
    
    else:
        if (
            state[pos_kingO[0] - 1, pos_kingO[1] - 1] != "o"
            and state[pos_kingO[0] - 1, pos_kingO[1] + 1] != "o"
            and state[pos_kingO[0] - 2, pos_kingO[1]] != "o"
        ):

            # Controllo eventuale riguardo la propria mossa, se spostando la pedina siamo a rischio mangiata allora la mossa non è di scacco
            for element in encirclement_list:
                if state[element] == 'x':
                    updateCheck(element,player)
                    return True
        return False


def updateCheck(pawn_position,player):
    global pos_kingX
    global check
    global checkType1
    global checkObj_list
    # Verifichiamo se siamo nell'intorno
    # Se l'intorno del re è vuoto (verificato nella chiamata isAPossibleCheck) e non siamo in posizione di rischio di mangiata allora abbiamo 3 possibili posizioni
    # che ci permetterebbero di raggiungere lo scacco
    
    
    check_list.append(pawn_position)

    if player=='O':

        if (
            pawn_position[0] == pos_kingX[0] + 4
            and pawn_position[1] == pos_kingX[1]
            ):
            checkObj_list.append((pawn_position[0] - 2, pawn_position[1]))
            checkType1 = True

        # Stiamo salendo di uno scalino verso destra per il controllo
        elif (
            pawn_position[0] == pos_kingX[0] + 3
            and pawn_position[1] == pos_kingX[1] + 1
        ):
            checkObj_list.append((pawn_position[0] - 1, pawn_position[1] - 1))
            checkObj_list.append((pawn_position[0] - 2, pawn_position[1]))
            checkType1 = True

        # Siamo saliti di un altro scalino verso destra
        elif (
            pawn_position[0] == pos_kingX[0] + 2
            and pawn_position[1] == pos_kingX[1] + 2
        ):
            checkObj_list.append((pawn_position[0], pawn_position[1] - 2))
            checkObj_list.append((pawn_position[0] - 1, pawn_position[1] - 1))
            checkType1 = True

        # Ci spostiamo verso sinistra
        elif (
            pawn_position[0] == pos_kingX[0] + 3
            and pawn_position[1] == pos_kingX[1] - 1
        ):
            checkObj_list.append((pawn_position[0] - 1, pawn_position[1] + 1))
            checkObj_list.append((pawn_position[0] - 2, pawn_position[1]))
            checkType1 = True

        # Siamo saliti di un altro scalino verso sinistra
        elif (
            pawn_position[0] == pos_kingX[0] + 2
            and pawn_position[1] == pos_kingX[1] - 2
        ):
            checkObj_list.append((pawn_position[0], pawn_position[1] + 2))
            checkObj_list.append((pawn_position[0] - 1, pawn_position[1] + 1))
            checkType1 = True
    
    else:

        if (
            pawn_position[0] == pos_kingO[0] - 4
            and pawn_position[1] == pos_kingO[1]
            ):
            checkObj_list.append((pawn_position[0] + 2, pawn_position[1]))
            checkType1 = True

        # Stiamo salendo di uno scalino verso destra per il controllo
        elif (
            pawn_position[0] == pos_kingO[0] - 3
            and pawn_position[1] == pos_kingO[1] + 1
        ):
            checkObj_list.append((pawn_position[0] + 1, pawn_position[1] - 1))
            checkObj_list.append((pawn_position[0] + 2, pawn_position[1]))
            checkType1 = True

        # Siamo saliti di un altro scalino verso destra
        elif (
            pawn_position[0] == pos_kingO[0] - 2
            and pawn_position[1] == pos_kingO[1] + 2
        ):
            checkObj_list.append((pawn_position[0], pawn_position[1] - 2))
            checkObj_list.append((pawn_position[0] + 1, pawn_position[1] - 1))
            checkType1 = True

        # Ci spostiamo verso sinistra
        elif (
            pawn_position[0] == pos_kingO[0] - 3
            and pawn_position[1] == pos_kingO[1] - 1
        ):
            checkObj_list.append((pawn_position[0] + 1, pawn_position[1] + 1))
            checkObj_list.append((pawn_position[0] + 2, pawn_position[1]))
            checkType1 = True

        # Siamo saliti di un altro scalino verso sinistra
        elif (
            pawn_position[0] == pos_kingO[0] - 2
            and pawn_position[1] == pos_kingO[1] - 2
        ):
            checkObj_list.append((pawn_position[0], pawn_position[1] + 2))
            checkObj_list.append((pawn_position[0] - 1, pawn_position[1] + 1))
            checkType1 = True
    


def updateEncirclementList(player):
    global pos_kingX

    if player=='O':
        point3 = (pos_kingX[0] + 2, pos_kingX[1] - 2)
        point4 = (pos_kingX[0] + 3, pos_kingX[1] - 1)
        point5 = (pos_kingX[0] + 4, pos_kingX[1])
        point6 = (pos_kingX[0] + 3, pos_kingX[1] + 1)
        point7 = (pos_kingX[0] + 2, pos_kingX[1] + 2)

        encirclement_list.append(point3)
        encirclement_list.append(point4)
        encirclement_list.append(point5)
        encirclement_list.append(point6)
        encirclement_list.append(point7)
    
    else:
        point3 = (pos_kingO[0] - 2, pos_kingO[1] - 2)
        point4 = (pos_kingO[0] - 3, pos_kingO[1] - 1)
        point5 = (pos_kingO[0] - 4, pos_kingO[1])
        point6 = (pos_kingO[0] - 3, pos_kingO[1] + 1)
        point7 = (pos_kingO[0] - 2, pos_kingO[1] + 2)

        encirclement_list.append(point3)
        encirclement_list.append(point4)
        encirclement_list.append(point5)
        encirclement_list.append(point6)
        encirclement_list.append(point7)


def testCheck(player, state):
    global pos_kingX
    global check
    global checkType1
    global checkObj_list

    # Si controlla se entrambe le pedine richieste sono in check
    if player == 'O':
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
    else:
        if checkType1:
            pawn_control1 = False
            pawn_control2 = False
            for element in check_list:
                if state[(element[0], element[1])] == "x":
                    pawn_control1 = True
            for element in checkObj_list:
                if state[(element[0], element[1])] == "x":
                    pawn_control2 = True
                    break
            if pawn_control1 and pawn_control2:
                check = True

def updateKingPosition(state,player):
    global pos_kingO
    global pos_kingX
    global checkType1
    global possibleCheck
    global check
    #variable list doesnt't need to be declared global, arent them?
    
    if player == "O":
        if state[pos_kingX] != "K":
            checkType1 = False
            possibleCheck = False
            check = False
            encirclement_list.clear()
            check_list.clear()
            checkObj_list.clear()

            possible_position1 = (pos_kingX[0] + 2, pos_kingX[1])      # Forward movement of the King
            possible_position2 = (pos_kingX[0] + 1, pos_kingX[1] + 1)  # Right movement of the King
            possible_position3 = (pos_kingX[0] + 1, pos_kingX[1] - 1)  # Left movement of the King
            possible_position4 = (pos_kingX[0], pos_kingX[1] - 2)
            possible_position5 = (pos_kingX[0], pos_kingX[1] + 2)
            possible_position6 = (pos_kingX[0] - 1, pos_kingX[1] - 1)
            possible_position7 = (pos_kingX[0] - 1, pos_kingX[1] + 1)
            possible_position8 = (pos_kingX[0] - 2, pos_kingX[1])

            if state[possible_position1] == "K":
                pos_kingX = possible_position1
            elif state[possible_position2] == "K":
                pos_kingX = possible_position2
            elif state[possible_position3] == "K":
                pos_kingX = possible_position3
            elif state[possible_position4] == "K":
                pos_kingX = possible_position4
            elif state[possible_position5] == "K":
                pos_kingX = possible_position5
            elif state[possible_position6] == "K":
                pos_kingX = possible_position6
            elif state[possible_position7] == "K":
                pos_kingX = possible_position7
            elif state[possible_position8] == "K":
                pos_kingX = possible_position8
            updateEncirclementList(state.to_move)

    else: #X
        if state[pos_kingO] != "Q":
            checkType1 = False
            possibleCheck = False
            check = False
            encirclement_list.clear()
            check_list.clear()
            checkObj_list.clear()
            possible_position1 = (pos_kingO[0] + 2, pos_kingO[1])      # Forward movement of the King
            possible_position2 = (pos_kingO[0] + 1, pos_kingO[1] + 1)  # Right movement of the King
            possible_position3 = (pos_kingO[0] + 1, pos_kingO[1] - 1)  # Left movement of the King
            possible_position4 = (pos_kingO[0], pos_kingO[1] - 2)
            possible_position5 = (pos_kingO[0], pos_kingO[1] + 2)
            possible_position6 = (pos_kingO[0] - 1, pos_kingO[1] - 1)
            possible_position7 = (pos_kingO[0] - 1, pos_kingO[1] + 1)
            possible_position8 = (pos_kingO[0] - 2, pos_kingO[1])

            if state[possible_position1] == "Q":
                pos_kingO = possible_position1
            elif state[possible_position2] == "Q":
                pos_kingO = possible_position2
            elif state[possible_position3] == "Q":
                pos_kingO = possible_position3
            elif state[possible_position4] == "Q":
                pos_kingO = possible_position4
            elif state[possible_position5] == "Q":
                pos_kingO = possible_position5
            elif state[possible_position6] == "Q":
                pos_kingO = possible_position6
            elif state[possible_position7] == "Q":
                pos_kingO = possible_position7
            elif state[possible_position8] == "Q":
                pos_kingO = possible_position8
            updateEncirclementList(state.to_move)

def isKingInDanger(player, state): #CONTROL CORRECTNESS 
    if player == "O":
        pos_king = pos_kingO
        adv = ["x", "K"]
    else:
        pos_king = pos_kingX
        adv = ["o", "Q"]
    
    if (state[pos_king[0] - 2, pos_king[1]] in adv
    or state[pos_king[0] - 1, pos_king[1] + 1] in adv
    or state[pos_king[0], pos_king[1] + 2] in adv
    or state[pos_king[0] + 1, pos_king[1] + 1] in adv
    or state[pos_king[0] + 2, pos_king[1]] in adv
    or state[pos_king[0] + 1, pos_king[1] - 1] in adv
    or state[pos_king[0], pos_king[1] - 2] in adv
    or state[pos_king[0] - 1, pos_king[1] - 1] in adv):
           return True
    return False



# ------------------------------------------------------------------------------------#


def h_alphabeta_search(game, state, cutoff=cutoff_depth(dynamic_c)):
    player = state.to_move
   
    global captures
    global initial_adv_piece_count
    global current_pieces_adv
    global pos_kingX
    global check
    global checkType1
    global possibleCheck
    global king_in_danger
    global dynamic_c
    considered_moves = []  #A list to store (move, utility) tuples, essentially a list of considered moves. 
    updateEncirclementList(player)
   
    
    current_pieces_adv = initial_adv_piece_count-captures
    dynamic_c = dynamic_cutoff(current_pieces_adv)
    

    @cache1
    def max_value(state, player, alpha, beta, depth, action, defensive_line):
        global possibleCheck
        v2 = -infinity
        if game.is_terminal(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            return h(state, action,player), None
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
        
        updatePawn4line(move,player)

        if player=='X':
            global defensive_line_X
            defensive_line_X = updateDefensiveLine(player,state, defensive_line)

        if player=='O':
            global defensive_line_O
            defensive_line_O = updateDefensiveLine(player,state, defensive_line)
        testCheck(player, state)

        return v, move

    @cache1
    def min_value(state, player, alpha, beta, depth, action, defensive_line):
        v2 = -infinity
        if game.is_terminal(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            return h(state, action,player), None
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

    if isAPossibleCheck(state,player):
        possibleCheck=True

    if player == 'O':
        if checkType1:
            for position in check_list:
                if state[position] != "o":
                    checkType1 = False
                    check_list.clear()
                    checkObj_list.clear()
    else:
        if checkType1:
            for position in check_list:
                if state[position] != "x":
                    checkType1 = False
                    check_list.clear()
                    checkObj_list.clear()

    if player == 'O':
        if check or checkType1:
            if (state[pos_kingX[0] + 1, pos_kingX[1] + 1] == "x"
                or state[pos_kingX[0] + 2, pos_kingX[1]] == "x"
                or state[pos_kingX[0] + 1, pos_kingX[1] - 1] == "x"):
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
    else:
        if check or checkType1:
            if (state[pos_kingO[0] - 1, pos_kingO[1] + 1] == "o"
                or state[pos_kingO[0] - 2, pos_kingO[1]] == "o"
                or state[pos_kingO[0] - 1, pos_kingO[1] - 1] == "o"):
                checkType1 = False
                possibleCheck = False
                check = False
                encirclement_list.clear()
                check_list.clear()
                checkObj_list.clear()
            else:
                for element in check_list:
                    if state[element] != "x":
                        checkType1 = False
                        possibleCheck = False
                        check = False
                        encirclement_list.clear()
                        check_list.clear()
                        checkObj_list.clear()
                        checkObj_list.clear()

    updateKingPosition(state,player)
    updateEncirclementList(player)
    king_in_danger = isKingInDanger(player,state)

    if player=='O':
        utility, chosen_move = max_value(state, player, -infinity, +infinity, 0, None, defensive_line_O)
    else:
        utility, chosen_move = max_value(state, player, -infinity, +infinity, 0, None, defensive_line_X) 

        
    sorted_moves = sorted(considered_moves, key=lambda x: x[1])   
    
    if 'capturing' in chosen_move: 
        captures+=1

    return utility, chosen_move



def playerStrategy(game, state):
    global current_pieces_adv
    global checkType1
    value, move = h_alphabeta_search(game,state,cutoff_depth(dynamic_cutoff(current_pieces_adv)))
    return move

    

def dynamic_cutoff(current_pieces_adv):
    global initial_adv_piece_count
    global convergent_cutoff
    if convergent_cutoff:
        return 0
    else:
        if current_pieces_adv <= initial_adv_piece_count and current_pieces_adv > initial_adv_piece_count // 3 :  
            return 0
        elif current_pieces_adv <= initial_adv_piece_count // 3 and current_pieces_adv>= initial_adv_piece_count // 4 :
            return 2
        elif current_pieces_adv< initial_adv_piece_count // 4:
            return 4
    return 1 
        

#______________________________HEURISTIC________________________________________________________________#

def h(state, action,player):
    
    start = action[1]
    arrival = action[2]

    global pos_kingX
    global pos_kingO
    global king_in_danger
    global check
    global possibleCheck
    global checkType1
    global current_pieces_adv

    if player == "O":
        distance_kingAdv = abs(arrival[0] - pos_kingX[0]) + abs(arrival[1] - pos_kingX[1])
        #check if useful our king distance
        if distance_kingAdv == 0:
            return 1 #check why 0 
        
        #Handling the movement of pawns that are already in a check position (if they move, check would be lost)
        if start in check_list:
            return 0
        
        if checkType1:
            if start in checkObj_list:
                return 0
        
        if "capturing" in action:  # Capturing attacking zone

            if king_suicide(player,state,start[0],start[1],arrival[0],arrival[1]):
                return -0.9
            if king_in_danger:
                return 0.98 #check if useful dividing for our king distance 
        
            #Favor a move that guarantees a type 1 check / Having this move implies that you are in a checkmate situation        
            if checkType1:
                if arrival in checkObj_list:
                    for element in check_list:
                        if state[element]=='o':
                            return 0.98
                    return 0
                
        #Check for a possible check
            if arrival[0] <= defensive_line_O - 3:
                if arrival[0] > start[0]:
                    return 0.75 / distance_kingAdv
                elif arrival[0] == start[0]:
                    return 0.80 / distance_kingAdv
                else:
                    return 0.5 / distance_kingAdv  #forward
            else: #capturing in defensive zone
                if arrival[0] > start[0]: #back capture
                    return 0.91
                elif arrival[0] == start[0]:
                    return 0.90
                elif (start[0] == arrival[0] + 1 and arrival[1] -1 == start[1]) or (start[0] == arrival[0] + 1 and arrival[1] + 1 == start[1]):
                    return 0.85 # Capture forward if the opponent's pawn is in front, in the upper right or upper left position
                else:
                    return 0.45 / distance_kingAdv #To capture two squares forward
        
        elif "nonCapturing" in action:

            if king_suicide(player,state, start[0],start[1],arrival[0],arrival[1]):
                return -0.9

            #Favor a move that guarantees a type 1 check / Having this move implies that you are in a checkmate situation        
            if checkType1:
                if arrival in checkObj_list:
                    for element in check_list:
                        if state[element]=='o':
                            return 0.92
                    return 0

            #Controlling if
            minimumDistance = math.inf
            if not possibleCheck:
                minimumDistance = distance_kingAdv
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

            if suicide(player, state, arrival[0], arrival[1]):  
                return -0.91
            elif arrival[0] >= defensive_line_O:
                return 0.02/distance_kingAdv
            elif arrival[0]<defensive_line_O: 
                return 0.01/distance_kingAdv  #It is weighted in such a way that it 'forces' the encirclement of the opponent's king
        
        elif "exchange" in action and current_pieces_adv <= initial_adv_piece_count//4:
            if king_suicide(player, state, start[0],start[1],arrival[0],arrival[1]):
                return -0.9
            if arrival[0] < defensive_line_O:
                return 0.1 / distance_kingAdv
            elif arrival[0] >= defensive_line_O:
                #king to his pawns
                if state[(arrival[0] -2, arrival[1])] == 'o' or state[(arrival[0]-1, arrival[1]-1)] =='o' or state[(arrival[0]-1, arrival[1]+1)]=='o':
                    return -0.15
                else:
                    return 0.01/distance_kingAdv
        
        return 0


    else: #X LOGIC
        distance_kingAdv = abs(arrival[0] - pos_kingO[0]) + abs(arrival[1] - pos_kingO[1])
        #check if we need our king distance
        
        if distance_kingAdv == 0:
            return 1
        
          #Handling the movement of pawns that are already in a check position (if they move, check would be lost)
        if start in check_list:
            return 0

        if checkType1:
            if start in checkObj_list:
                return 0
        
        if "capturing" in action:  # Capturing attacking zone

            if king_suicide(player, state, start[0],start[1],arrival[0],arrival[1]):
                return -0.9
        
            if king_in_danger:
                return 0.98 / distance_kingAdv

            #Favor a move that guarantees a type 1 check / Having this move implies that you are in a checkmate situation        
            if checkType1:
                if arrival in checkObj_list:
                    return 0.98
            #Check for a possible check #check weights
            if arrival[0] >= defensive_line_X + 3: #check if +3 is correct
                if arrival[0] < start[0]:
                    return 0.75 / distance_kingAdv
                elif arrival[0] == start[0]:
                    return 0.80 / distance_kingAdv
                else:
                    return 0.5 / distance_kingAdv  #forward
            else: #capturing in defensive zone
                if arrival[0] < start[0]: #back capture
                    return 0.91
                elif arrival[0] == start[0]:  # Horizontal capture
                    return 0.90
                elif (start[0]+1 == arrival[0] and start[1]-1 == arrival[1]) or (start[0]+1 == arrival[0] and start[1]+1 == arrival[1]):
                    return 0.85  # Capture forward if the opponent's pawn is in front, in the upper right or upper left position
                else:
                    return 0.45 / distance_kingAdv #To capture two squares forward
        
        elif "nonCapturing" in action:

            if king_suicide(player, state, start[0],start[1],arrival[0],arrival[1]):
                return -0.9

            #Favor a move that guarantees a type 1 check / Having this move implies that you are in a checkmate situation        
            if checkType1:
                if arrival in checkObj_list:
                    return 0.98
            #Controlling if
            minimumDistance = math.inf
            if not possibleCheck:
                minimumDistance = distance_kingAdv
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
            
            if suicide(player, state, arrival[0], arrival[1]):  
                return -0.89
            elif arrival[0]<=defensive_line_X: #CHECK WEIGHTS
                return 0.02/distance_kingAdv
            elif arrival[0]>defensive_line_X: #CHECK WEIGHTS
                return 0.01/distance_kingAdv  #It is weighted in such a way that it 'forces' the encirclement of the opponent's king
            
        elif "exchange" in action and current_pieces_adv <= initial_adv_piece_count//4:
            if king_suicide(player, state, start[0],start[1],arrival[0],arrival[1]):
                return -0.9
            if arrival[0] > defensive_line_X:
                return 0.1/distance_kingAdv
            elif arrival[0] <= defensive_line_X:
                #king to his pawns
                if state[(arrival[0]+2, arrival[1])] == 'x' or state[(arrival[0]+1, arrival[1]-1)] =='x' or state[(arrival[0]+1, arrival[1]+1)]=='x': 
                    return -0.15
            else:
                return 0.01/distance_kingAdv
        return -1
