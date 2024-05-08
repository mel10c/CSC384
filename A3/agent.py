"""
An AI player for Othello. 
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

# define cache
cache = {}

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    # get score
    scores = get_score(board)

    # compute utility value
    if color == 1:
        score = scores[0] - scores[1]
    else:
        score = scores[1] - scores[0]

    return score

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT
    return 0 #change this!


# helper function for odering
def ordering_max(board, moves, color, player):
    '''Helper function for ordering for max heuristic'''
    move_dic = dict()
    ordered = []
    for move in moves:
        column, row = move
        update_board = play_move(board, player, column, row)
        util = compute_utility(update_board, color)
        if util in move_dic and move_dic[util] != [move]:
            move_dic[util].append(move)
        else:
            move_dic[util] = [move]

    ordered_util = sorted(list(move_dic.keys()), reverse = True)

    for util in ordered_util:
        ordered += move_dic[util]

    return ordered


# helper function for ordering
def ordering_min(board, moves, color, player):
    '''Helper function for ordering for min heuristic'''
    move_dic = dict()
    ordered = []
    for move in moves:
        column, row = move
        update_board = play_move(board, player, column, row)
        util = compute_utility(update_board, color)
        if util in move_dic and move_dic[util] != [move]:
            move_dic[util].append(move)
        else:
            move_dic[util] = [move]

    ordered_util = sorted(list(move_dic.keys()), reverse = False)

    for util in ordered_util:
        ordered += move_dic[util]

    return ordered


############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    # define variables
    min_move = None
    min_uti = float("inf")

    # check cache
    if caching != 0 and board in cache:
        return cache[str(board)]

    # get opponent info
    if color == 1: 
        opp_color = 2
    else:
        opp_color = 1
    
    # get legal moves
    moves = get_possible_moves(board, opp_color)
    if len(moves) == 0 or limit == 0:
        min_uti = compute_utility(board, color)
        cache[str(board)] = (min_move, min_uti)
        return None, min_uti

    # find best move
    for move in moves:
        # apply moves
        column, row = move
        update_board = play_move(board, opp_color, column, row)
        # compute util
        _, util = minimax_max_node(update_board, color, limit - 1, caching)
        # cache new board
        if caching:
            cache[str(update_board)] = (move, util)
        # update
        if util < min_uti:
            min_move = move
            min_uti = util

    return min_move, min_uti

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    # define variables
    max_move = None
    max_util = -float("inf")

    # check cache
    if caching != 0 and board in cache:
        return cache[str(board)]

    # get legal moves
    moves = get_possible_moves(board, color)
    if len(moves) == 0 or limit == 0:
        max_util = compute_utility(board, color)
        cache[str(board)] = (max_move, max_util)
        return None, max_util

    # find best move
    for move in moves:
        # apply moves
        column, row = move
        update_board = play_move(board, color, column, row)
        # compute util
        _, util = minimax_min_node(update_board, color, limit - 1, caching)
        # cache new board
        if caching:
            cache[str(update_board)] = (move, util)
        # update
        # if util > max_uti:
        if max_util < util:
            max_move = move
            max_util = util

    return max_move, max_util

def select_move_minimax(board, color, limit, caching = 0):
    """
    Given a board and a player color, decide on a move. 
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.  

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
    """
    move, _ = minimax_max_node(board, color, limit, caching)
    return move

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    # define variables
    min_move = None
    min_uti = float("inf")

    # check cache
    if caching != 0 and board in cache:
        return cache[str(board)]

    # get opponent info
    # color: dark = 1; light = 2
    if color == 1: 
        opp_color = 2
    else:
        opp_color = 1
    
    # get legal moves
    moves = get_possible_moves(board, opp_color)
    if len(moves) == 0 or limit == 0:
        min_uti = compute_utility(board, color)
        cache[str(board)] = (min_move, min_uti)
        return min_move, min_uti

    # odering
    if ordering != 0:
        moves = ordering_min(board, moves, color, color)

    # find best move
    for move in moves:
        # apply moves
        column, row = move
        update_board = play_move(board, opp_color, column, row)
        # compute util
        _, util = alphabeta_max_node(update_board, color, alpha, beta, limit - 1, caching, ordering)
        # cache new board
        if caching:
            cache[str(update_board)] = (move, util)
        # update
        if util < min_uti:
            min_move = move
            min_uti = util

        # conduct pruning
        beta = min(beta, util)
        if beta <= alpha:
            break # prune

    return min_move, min_uti

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    # define variables
    max_move = None
    max_util = -float("inf")

    # check cache
    if caching != 0 and board in cache:
        return cache[str(board)]

    # get legal moves
    moves = get_possible_moves(board, color)
    if len(moves) == 0 or limit == 0:
        max_util = compute_utility(board, color)
        cache[str(board)] = (max_move, max_util)
        return max_move, max_util

    # odering
    if ordering != 0:
        moves = ordering_max(board, moves, color, color)

    # find best move
    for move in moves:
        # apply moves
        column, row = move
        update_board = play_move(board, color, column, row)
        # compute util
        _, util = alphabeta_min_node(update_board, color, alpha, beta, limit -1, caching, ordering)
        # cache new board
        if caching:
            cache[str(update_board)] = (move, util)
        # update
        if util > max_util:
            max_move = move
            max_util = util

        # conduct pruning
        alpha = max(alpha, util)
        if beta <= alpha:
            break # prune

    return max_move, max_util

def select_move_alphabeta(board, color, limit, caching = 0, ordering = 0):
    """
    Given a board and a player color, decide on a move. 
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.  

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
    If ordering is ON (i.e. 1), use node ordering to expedite pruning and reduce the number of state evaluations. 
    If ordering is OFF (i.e. 0), do NOT use node ordering to expedite pruning and reduce the number of state evaluations. 
    """
    move, _ = alphabeta_max_node(board, color, -float("inf"), float("inf"), limit, caching, ordering)
    return move

####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Othello AI") # First line is the name of this AI
    arguments = input().split(",")
    
    color = int(arguments[0]) #Player color: 1 for dark (goes first), 2 for light. 
    limit = int(arguments[1]) #Depth limit
    minimax = int(arguments[2]) #Minimax or alpha beta
    caching = int(arguments[3]) #Caching 
    ordering = int(arguments[4]) #Node-ordering (for alpha-beta only)

    if (minimax == 1): eprint("Running MINIMAX")
    else: eprint("Running ALPHA-BETA")

    if (caching == 1): eprint("State Caching is ON")
    else: eprint("State Caching is OFF")

    if (ordering == 1): eprint("Node Ordering is ON")
    else: eprint("Node Ordering is OFF")

    if (limit == -1): eprint("Depth Limit is OFF")
    else: eprint("Depth Limit is ", limit)

    if (minimax == 1 and ordering == 1): eprint("Node Ordering should have no impact on Minimax")

    while True: # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status == "FINAL": # Game is over.
            print
        else:
            board = eval(input()) # Read in the input and turn it into a Python
                                  # object. The format is a list of rows. The
                                  # squares in each row are represented by
                                  # 0 : empty square
                                  # 1 : dark disk (player 1)
                                  # 2 : light disk (player 2)

            # Select the move and send it to the manager
            if (minimax == 1): #run this if the minimax flag is given
                movei, movej = select_move_minimax(board, color, limit, caching)
            else: #else run alphabeta
                movei, movej = select_move_alphabeta(board, color, limit, caching, ordering)
            
            print("{} {}".format(movei, movej))

if __name__ == "__main__":
    run_ai()
