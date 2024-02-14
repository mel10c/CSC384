#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specificclasses and problems


# SOKOBAN HEURISTICS
def manh_dist(x, y):
    '''A helper function for calculating manhattan distances'''
    manhattan_distance = abs(x[0] - y[0]) + abs(x[1] - y[1])
    return manhattan_distance


def deadlock(box, state):
    '''A helper function for detecting deadlock'''

    # if wall count > 2, then it is a deadlock (corner)
    wall_count = 0

    # define obstacles as walls, other around boxes
    # (1) define walls
    x, y = box                              # get box coordinates
    boundary_walls = set()
    for x in range(state.width):            # top & bottom edge
        boundary_walls.add((x, 0))
        boundary_walls.add((x, state.height - 1))
    for y in range(state.height):           # left & right edge
        boundary_walls.add((0, y))
        if y != 0 and y != state.height - 1:  # avoid duplicating
            boundary_walls.add((state.width - 1, y))
    # (2) combine obstacles
    walls = state.obstacles.union(boundary_walls)
    # (3) define other boxes
    other_boxes = state.boxes - {box}
    # (4) finally define all obstacles
    obstacles = walls.union(other_boxes)

    # define possible directions movements
    directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]

    # deadlock detection
    for dx, dy in directions:
        adj_x, adj_y = x + dx, y + dy       # define adjacent step
        if (adj_x, adj_y) in obstacles:     # check if it is an obstacle
            wall_count += 1
            continue

        # check if move a box in a direction would place it in an obstacle position
        next_x, next_y = adj_x + dx, adj_y + dy
        if (next_x, next_y) in obstacles or (next_x + dx, next_y + dy) in obstacles:
            wall_count += 1

    # return corner detection
    return wall_count >= 2


def tunnel(box, state):
    '''A helper function for detecting tunnel'''

    x, y = box                              # get box coordinates
    obstacles = state.obstacles.union(state.boxes - {box})  # define obstacles

    # check horizontal tunnel: walls on the top and bottom
    if (x, y - 1) in obstacles and (x, y + 1) in obstacles:
        return True
    # check vertical tunnel: walls on the left and right
    if (x - 1, y) in obstacles and (x + 1, y) in obstacles:
        return True

    return False


def heur_alternate(state):
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_manhattan_distance has flaws.
    # Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.

    # --- Improvements: add arbitrary penalty for deadlocks & tunneling ---
    # The penalty attempts to account for the potential additional steps in situations:
    # 1. Deadlocks: where boxes can no longer be moved
    #     (1) simple deadlock: box at or about to encounter corner (check adjacent space)
    #     (2) frozen box: adjacent to wall or another box (check around box)
    # 2. Tunneling: movement is restricted by wall (check around box)

    sum_dist = 0                            # set initial distance
    for box in state.boxes:                 # loop for all box in current state
        min_dist = float('inf')             # initial infinite value

        for storage in state.storage:       # loop for all storage unit
            dist = manh_dist(box, storage)  # manhattan distance
            if dist < min_dist:             # update if is the smallest distance so far
                min_dist = dist

        sum_dist += min_dist                # add to total

        # Improvements from heur_manhattan_distance()
        if tunnel(box, state):              # if it is a tunnel
            sum_dist += 10
        if deadlock(box, state):            # if a deadlock corner
            sum_dist += 20

    return sum_dist


def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0


def heur_manhattan_distance(state):
    '''admissible sokoban puzzle heuristic: manhattan distance'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # We want an admissible heuristic, which is an optimistic heuristic.
    # It must never overestimate the cost to get from the current state to the goal.
    # The sum of the Manhattan distances between each box that has yet to be stored and the storage point nearest to it is such a heuristic.
    # When calculating distances, assume there are no obstacles on the grid.
    # You should implement this heuristic function exactly, even if it is tempting to improve it.
    # Your function should return a numeric value; this is the estimate of the distance to the goal.

    sum_dist = 0                            # set initial distance
    for box in state.boxes:                 # loop for all box in current state
        min_dist = float('inf')             # initial infinite value

        for storage in state.storage:       # loop for all storage unit
            dist = manh_dist(box, storage)  # manhattan distance
            if dist < min_dist:             # update if is the smallest distance so far
                min_dist = dist

        sum_dist += min_dist                # add to total

    return sum_dist


def fval_function(sN, weight):
    '''f = g + weight * h'''
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    fval = sN.gval + (weight * sN.hval)  # f = g + weight * h
    return fval


# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    # initial time
    start_time = os.times()[0]
    remain_time = timebound

    # instantiate custom search engine
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))  # wrap fval_function
    search_eng = SearchEngine("custom", "full")
    search_eng.init_search(initial_state, sokoban_goal_state,
                           heur_fn, wrapped_fval_function)

    # initiate variables
    goal_state = False          # default return value as false
    cost = float("inf")         # initial cost
    stats_object = None         # initial SearchStats object

    # iterate search for better goal state until time runs out
    # while timebound - (os.times()[0] - start_time) > 0:
    while remain_time > 0:
        # update remaining time
        remain_time = timebound - (os.times()[0] - start_time)

        # weighted a-star search
        costbound = (cost, float("inf"), cost)
        temp_state, temp_stats = search_eng.search(remain_time, costbound)

        # update if a result is found and it's better than the current
        if temp_state and (not goal_state or temp_state.gval < cost):
            goal_state = temp_state         # update goal_state
            cost = temp_state.gval          # keep track of the g-value
            stats_object = temp_stats       # update SearchStats object

    return goal_state, stats_object


def iterative_astar(initial_state, heur_fn, weight=1,
                    timebound=5):  # uses f(n), see how autograder initializes a search line 88
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    # initial time
    start_time = os.times()[0]
    remain_time = timebound

    # initiate variables
    goal_state = False          # default return value as false
    cost = float("inf")         # initial cost
    stats_object = None         # initial SearchStats object
    current_weight = weight     # initial weight

    while remain_time > 0:
        # adjust the weight for each a-star search iteration
        temp_state, temp_stats = weighted_astar(initial_state, heur_fn,
                                                current_weight, remain_time)

        # update remaining time
        remain_time = timebound - (os.times()[0] - start_time)

        # update if a result is found and it's better than the current
        if temp_state and (not goal_state or temp_state.gval < cost):
            goal_state = temp_state         # update goal_state
            cost = temp_state.gval          # keep track of the g-value
            stats_object = temp_stats       # update SearchStats object

        # key: adjust the weight
        current_weight = max(1, current_weight - 0.5)

    return goal_state, stats_object


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    # initial time
    start_time = os.times()[0]
    remain_time = timebound

    # initiate variables
    goal_state = False          # default return value as false
    cost = float("inf")         # initial cost
    stats_object = None         # initial SearchStats object

    # instantiate greedy best-first search engine
    search_eng = SearchEngine("best_first", "full")
    search_eng.init_search(initial_state, sokoban_goal_state, heur_fn)

    # search until the time runs out
    while remain_time > 0:
        # update remaining time
        remain_time = timebound - (os.times()[0] - start_time)

        # conduct the search with h(n)
        temp_result = search_eng.search(remain_time, costbound=(cost, float('inf'), float('inf')))

        # update if a result is found and it's better than the current
        if temp_result:
            temp_state, temp_stats = temp_result  # break tuple
            if temp_state and temp_state.gval < cost:
                goal_state = temp_state         # update goal_state
                cost = temp_state.gval          # keep track of the g-value
                stats_object = temp_stats       # update SearchStats object

    return goal_state, stats_object
