import math

infinity = math.inf


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

defensive_line = 9
attacking_line = 8
last_line = 14


def h_alphabeta_search(game, state, cutoff=cutoff_depth(2)):
    """Search game to determine best action; use alpha-beta pruning.
    As in [Figure 5.7], this version searches all the way to the leaves."""

    player = state.to_move

    @cache1
    def max_value(state, alpha, beta, depth, action_considerata, defensive_line):
        if game.is_terminal(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            return h(state, player, action_considerata, game), None
        v, move = -infinity, None
        for a in game.actions(state):
            v2, _ = min_value(
                game.result(state, a), alpha, beta, depth + 1, a, defensive_line
            )
            if v2 > v:
                v, move = v2, a
                alpha = max(alpha, v)
            if v >= beta:
                return v, move

        if "exchange" not in move:
            pawn4line[move[2][0]] += 1
            pawn4line[move[1][0]] -= 1

        attacking_pawn_alive = 0
        for i in range(0, defensive_line):
            attacking_pawn_alive += pawn4line[i]
        if attacking_pawn_alive == 0:
            defensive_line += 1
            print("defensive line:" + str(defensive_line))
        return v, move

    @cache1
    def min_value(state, alpha, beta, depth, action_considerata, defensive_line):
        if game.is_terminal(state):
            return game.utility(state, player), None
        if cutoff(game, state, depth):
            return h(state, player, action_considerata), None
        v, move = +infinity, None
        for a in game.actions(state):
            v2, _ = max_value(
                game.result(state, a), alpha, beta, depth + 1, a, defensive_line
            )
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, move
        return v, move

    return max_value(state, -infinity, +infinity, 0, None, defensive_line)


def h(board, player, action_considerata):
    partenza = action_considerata[1]
    arrivo = action_considerata[2]
    if "capturing" in action_considerata:
        if partenza[0] <= 3:
            return 0.85
        if partenza[0] < defensive_line:
            if arrivo[0] > partenza[0]:
                return 0.8
            elif arrivo[0] == partenza[0]:
                return 0.6
            else:
                return 0.4
        else:
            if arrivo[0] > partenza[0]:
                return 0.7
            elif arrivo[0] == partenza[0]:
                return 0.9  # prediligi il mangiare orizzontalmente
            else:
                return 0.3

    """gestire l'exchange con la divisione in 4"""
    return 0  # Se non puo' catturare tutte ugual peso //TODO
