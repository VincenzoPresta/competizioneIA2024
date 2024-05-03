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
    7: 0,  # Linea Centrale
    8: 7,
    9: 6,
    10: 5,
    11: 3,
    12: 2,
    13: 2,
    14: 1,
}

"""adversaryPawnSection={
    "UpRight":  
    "UpLeft":
    "DownLeft":
    "DownRight":
}"""

# Sono le posizioni obiettivo che desideriamo raggiungere per lo scacco, dunque si aggiorna se abbiamo una pedina nell'intorno esterno del re
checkObj_list = []

# Sono le posizioni delle pedine che sono già nell'intorno esterno del re che ci potrebbero garantire uno scacco
check_list = []

possibleCheck = False
checkType1 = False
checkType2 = False
check = False

king_in_danger = False


# è la lista delle posizioni dell'intorno grande del re in modo che non si debbano calcolare ad ogni verifica di check ma si genera la lista
# ogni volta che il re viene spostato
encirclement_list = []

defensive_line = 9
kingAdv_position = (0, 7)
kingOur_position = (14, 7)

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
# Uno sta per arrivo 2 per partenza
def isAPossibleCheck(state):

    global kingAdv_position
    global check
    global checkType1

    # Controllo se l'intorno del re avversario è vuoto garantendo la sua impossibilità di fare una exchange
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
                
        
        
        """if (
            state[arrivo[0] + 2, arrivo[1]] != "x"
            and state[arrivo[0] + 1, arrivo[1] - 1] != "x"
            and state[arrivo[0] + 1, arrivo[1] + 1] != "x"
            and state[arrivo[0] + 1, arrivo[1] - 1] != "x"
            and state[arrivo[0], arrivo[1] - 2] != "x"
            and state[arrivo[0], arrivo[1] + 2] != "x"
            and state[arrivo[0] + 1, arrivo[1] - 1] != "x"
            and state[arrivo[0] + 1, arrivo[1] + 1] != "x"
        ):
            print("secondopasso1")
            return 1
        elif (
            state[partenza[0] + 2, partenza[1]] != "x"
            and state[partenza[0] + 1, partenza[1] - 1] != "x"
            and state[partenza[0] + 1, partenza[1] + 1] != "x"
            and state[partenza[0] + 1, partenza[1] - 1] != "x"
            and state[partenza[0], partenza[1] - 2] != "x"
            and state[partenza[0], partenza[1] + 2] != "x"
            and state[partenza[0] + 1, partenza[1] - 1] != "x"
            and state[partenza[0] + 1, partenza[1] + 1] != "x"
        ):
            print("secondopasso2")
            return 2"""
    return False


def updateCheck(pawn_position):
    global kingAdv_position
    global check
    global checkType1
    global checkType2
    global checkObj_list
    # Verifichiamo se siamo nell'intorno
    # Se l'intorno del re è vuoto (verificato nella chiamata isAPossibleCheck) e non siamo in posizione di rischio di mangiata allora abbiamo 3 possibili posizioni
    # che ci permetterebbero di raggiungere lo scacco
    check_list.append(pawn_position)

    if (
        pawn_position[0] == kingAdv_position[0] + 4
        and pawn_position[1] == kingAdv_position[1]
        ):
        print("CASO1")
        checkObj_list.append((pawn_position[0] - 2, pawn_position[1]))
        checkType1 = True

    # Stiamo salendo di uno scalino verso destra per il controllo
    elif (
        pawn_position[0] == kingAdv_position[0] + 3
        and pawn_position[1] > kingAdv_position[1] + 1
    ):
        print("CASO2")
        checkObj_list.append((pawn_position[0] - 1, pawn_position[1] - 1))
        checkObj_list.append((pawn_position[0] - 2, pawn_position[1]))
        checkType1 = True

    # Siamo saliti di un altro scalino verso destra
    elif (
        pawn_position[0] == kingAdv_position[0] + 2
        and pawn_position[1] == kingAdv_position[1] + 2
    ):
        print("CASO3")
        checkObj_list.append((pawn_position[0], pawn_position[1] - 2))
        checkObj_list.append((pawn_position[0] - 1, pawn_position[1] - 1))
        checkType1 = True

    # Ci spostiamo verso sinistra
    elif (
        pawn_position[0] == kingAdv_position[0] + 3
        and pawn_position[1] == kingAdv_position[1] - 1
    ):
        print("CASO4")
        checkObj_list.append((pawn_position[0] - 1, pawn_position[1] + 1))
        checkObj_list.append((pawn_position[0] - 2, pawn_position[1]))
        checkType1 = True

    # Siamo saliti di un altro scalino verso sinistra
    elif (
        pawn_position[0] == kingAdv_position[0] + 2
        and pawn_position[1] == kingAdv_position[1] - 2
    ):
        print("CASO5")
        checkObj_list.append((pawn_position[0], pawn_position[1] + 2))
        checkObj_list.append((pawn_position[0] - 1, pawn_position[1] + 1))
        checkType1 = True


    
    print("VEDERE POSIZIONI")
    print(checkType1)
    print(pawn_position)
    print(kingAdv_position)
    print(encirclement_list)
    print(check_list)
    print(checkObj_list)
    """if len(check_list)==0 or len(checkObj_list)==0:
        return 0
    else:
        return 1"""


def updateEncirclementList():
    global kingAdv_position
    # point1 = (kingAdv_position[0],kingAdv_position[1]-4)
    #point2 = (kingAdv_position[0] - 1, kingAdv_position[1] - 3)
    point3 = (kingAdv_position[0] + 2, kingAdv_position[1] - 2)
    point4 = (kingAdv_position[0] + 3, kingAdv_position[1] - 1)
    point5 = (kingAdv_position[0] + 4, kingAdv_position[1])
    point6 = (kingAdv_position[0] + 3, kingAdv_position[1] + 1)
    point7 = (kingAdv_position[0] + 2, kingAdv_position[1] + 2)
    #point8 = (kingAdv_position[0] + 1, kingAdv_position[1] + 3)
    # point9 = (kingAdv_position[0],kingAdv_position[1]+4)

    # encirclement_list.append(point1)
    #encirclement_list.append(point2)
    encirclement_list.append(point3)
    encirclement_list.append(point4)
    encirclement_list.append(point5)
    encirclement_list.append(point6)
    encirclement_list.append(point7)
    #encirclement_list.append(point8)
    # encirclement_list.append(point9)


def testCheck(move, state):
    global kingAdv_position
    global check
    global checkType1
    global checkType2
    global checkObj_list

    partenza = move[0]
    arrivo = move[1]

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


def h_alphabeta_search(game, state, cutoff=cutoff_depth(0)):
    """Search game to determine best action; use alpha-beta pruning.

    As in [Figure 5.7], this version searches all the way to the leaves.

    Tracks considered moves and their utilities for printing.
    Prints considered moves in ascending order of utility.
    Always chooses the move with the highest utility.
    """
    
    player = state.to_move
    global kingAdv_position
    global check
    global checkType1
    global checkType2
    global possibleCheck
    global king_in_danger
    considered_moves = []  # Lista per conservare le tuple (move, utility), in pratica una lista di mosse considerate 
    updateEncirclementList()

    @cache1
    def max_value(
        state, player, alpha, beta, depth, action_considerata, defensive_line
    ):
        global possibleCheck
        v2 = -infinity
        if game.is_terminal(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            return h(state, action_considerata), None
        v, move = -infinity, None
        for a in game.actions(state):
            v2, _ = min_value(
                game.result(state, a),
                player,
                alpha,
                beta,
                depth + 1,
                a,
                defensive_line,
            )
            if v2 > v:
                v, move = v2, a
                alpha = max(alpha, v)

            if v >= beta:
                return v, move
            if state.to_move == "O":
                considered_moves.append((a, v2))  # Aggiungi la mossa alla lista con la rispettiva utility

        updatePawn4line(move)
        defensive_line = updateDefensiveLine(state, move, defensive_line)

        testCheck(move, state)

        return v, move

    @cache1
    def min_value(
        state, player, alpha, beta, depth, action_considerata, defensive_line
    ):
        v2 = -infinity
        if game.is_terminal(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            return h(state, action_considerata), None
        v, move = +infinity, None
        for a in game.actions(state):
            v2, _ = max_value(
                game.result(state, a),
                player,
                alpha,
                beta,
                depth + 1,
                a,
                defensive_line,
            )
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)

            if v <= alpha:
                return v, move
            if state.to_move == "O":
                considered_moves.append((a, v2))  # Aggiungi la mossa alla lista con la rispettiva utility
        return v, move

    if isAPossibleCheck(state):
        print("prova")
        possibleCheck=True

    if checkType1:
        for position in check_list:
            if state[position] != "o":
                checkType1 = False
                check_list.clear()
                checkObj_list.clear()

    if check or checkType1:
        if (
            state[kingAdv_position[0] + 1, kingAdv_position[1] + 1] == "x"
            or state[kingAdv_position[0] + 2, kingAdv_position[1]] == "x"
            or state[kingAdv_position[0] + 1, kingAdv_position[1] - 1] == "x"
        ):
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
                    checkType2 = False
                    possibleCheck = False
                    check = False
                    encirclement_list.clear()
                    check_list.clear()
                    checkObj_list.clear()
                    checkObj_list.clear()

    # Aggiornamento Posizione Re Avversario
    if state[kingAdv_position] != "K":
        print("AGGIORNAMENTO RE")
        checkType1 = False
        possibleCheck = False
        check = False
        encirclement_list.clear()
        check_list.clear()
        checkObj_list.clear()

        possible_position1 = (
            kingAdv_position[0] + 2,
            kingAdv_position[1],
        )  # Spostamento in avanti del Re
        possible_position2 = (
            kingAdv_position[0] + 1,
            kingAdv_position[1] + 1,
        )  # Spostamento verso destra del Re
        possible_position3 = (
            kingAdv_position[0] + 1,
            kingAdv_position[1] - 1,
        )  # Spostamento verso sinsitra del Re
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
        state[kingOur_position[0] - 2, kingOur_position[1]] == "x"
        or state[kingOur_position[0] - 1, kingOur_position[1] + 1] == "x"
        or state[kingOur_position[0], kingOur_position[1] + 2] == "x"
        or state[kingOur_position[0] + 1, kingOur_position[1] + 1] == "x"
        or state[kingOur_position[0] + 2, kingOur_position[1]] == "x"
        or state[kingOur_position[0] + 1, kingOur_position[1] - 1] == "x"
        or state[kingOur_position[0], kingOur_position[1] - 2] == "x"
        or state[kingOur_position[0] - 1, kingOur_position[1] - 1] == "x"
    ):
        king_in_danger = True
    else:
        king_in_danger = False

    utility, chosen_move = max_value(
        state, player, -infinity, +infinity, 0, None, defensive_line
    )  # Sostituito il return per stampare le mosse considerate

    sorted_moves = sorted(considered_moves, key=lambda x: x[1])

    # Print considered moves and utilities
    """print("Considered Moves and Utilities [Sorted by utility]:")
    for move, utility in sorted_moves:
        print(f"Move: {move}, Utility: {utility}")

    print("Number of considered moves: ", len(considered_moves))
    considered_moves = []
    # Print chosen move and utility
    print(f"\nChosen Move: {chosen_move}, Utility: {utility}")"""

    return utility, chosen_move


#______________________________EURISTICA________________________________________________________________


def h(state, action_considerata):
    partenza = action_considerata[1]
    arrivo = action_considerata[2]

    global kingAdv_position
    global king_in_danger
    global check
    global possibleCheck
    global checkType1
    global checkType2

    print(checkType1)
    distanzaReAvversario = abs(arrivo[0] - kingAdv_position[0]) + abs(
        arrivo[1] - kingAdv_position[1]
    )
    distanzaRePersonale = abs(arrivo[0] - kingOur_position[0]) + abs(
        arrivo[1] - kingOur_position[1]
    )

    if distanzaReAvversario == 0:
        return 0

    # Gestione degli spostamenti delle pedine che sono già in una posizione di scacco (se si muovessero si perderebbe lo scacco)

    if partenza in check_list:
        return 0

    if checkType1:
        if partenza in checkObj_list:
            return 0

    if "capturing" in action_considerata:  # Capturing in zona di attacco

        if king_in_danger:
            return 0.98 / distanzaRePersonale

        # Si predilige una mossa che garantisce il check di tipo 1/se si ha questa mossa implica che si è in una situazione di scacco
        if checkType1:
            if arrivo in checkObj_list:
                for element in check_list:
                    if state[element]=='o':
                        return 0.95
                return 0

        # Si controlla se c'è un possibile scacco

        if arrivo[0] <= defensive_line - 3:
            if arrivo[0] > partenza[0]:
                return 0.75 / distanzaReAvversario
            elif arrivo[0] == partenza[0]:
                return 0.80 / distanzaReAvversario
            else:
                return 0.5 / distanzaReAvversario  # avanti
        else:  # Capturing nella zona di difesa
            if arrivo[0] > partenza[0]:  # Mangiare verso dietro
                return 0.91
            elif arrivo[0] == partenza[0]:  # Mangiare orizzontale
                return 0.90
            elif (partenza[0] == arrivo[0] + 1 and arrivo[1] - 1 == partenza[1]) or (
                partenza[0] == arrivo[0] + 1 and arrivo[1] + 1 == partenza[1]
            ):
                return 0.85  # Mangiare in avanti se l'avv si trova davanti o in alto a destra o in alto a sinistra
            else:
                return 0.45 / distanzaReAvversario  # Mangiare due caselle verso avanti

    elif "nonCapturing" in action_considerata:
        # Si predilige una mossa che garantisce il check di tipo 1/se si ha questa mossa implica che si è in una situazione di scacco
        if checkType1:
            if arrivo in checkObj_list:
                for element in check_list:
                    if state[element]=='o':
                        return 0.92
                print("ziosmegma")
                return 0

        # Si controlla se

        distanza_minima = math.inf
        if not possibleCheck:
            distanza_minima = distanzaReAvversario
        else:
            if partenza in checkObj_list:
                return 0

            for element in checkObj_list:
                tmp = abs(partenza[0] - element[0]) + abs(partenza[1] - element[1])
                if distanza_minima > tmp:
                    distanza_minima = tmp

            if distanza_minima == math.inf:
                for element in encirclement_list:
                    tmp = abs(partenza[0] - element[0]) + abs(partenza[1] - element[1])
                    if distanza_minima > tmp:
                        distanza_minima = tmp

        if (
            state[(arrivo[0] - 2, arrivo[1])] != " "
            or state[(arrivo[0] - 1, arrivo[1] + 1)] != " "
            or state[(arrivo[0], arrivo[1] + 2)] != " "
            or state[(arrivo[0] + 1, arrivo[1] + 1)] != " "
            or state[(arrivo[0] + 2, arrivo[1])] != " "
            or state[(arrivo[0] + 1, arrivo[1] - 1)] != " "
            or state[(arrivo[0], arrivo[1] - 2)] != " "
            or state[(arrivo[0] - 1, arrivo[1] - 1)] != " "
        ):  # la pedina dovrebbe evitare di spostarsi in una casella nella quale potrebbe essere attaccata
            return 0.01

        if partenza[0] < defensive_line:
            return 0.3 / distanza_minima
        else:
            return 0.1 / distanza_minima

    """gestire l'exchange con la divisione in 4"""
    return 0  # Se non puo' catturare tutte ugual peso //TODO





#----------------------------------_AVVERSARIO ----------------------------------------------------------------
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
