#Look for #IMPLEMENT tags in this file.
'''
All encodings need to return a CSP object, and a list of lists of Variable objects 
representing the board. The returned list of lists is used to access the 
solution. 

For example, after these three lines of code

    csp, var_array = caged_csp(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the FunPuzz puzzle.

The grid-only encodings do not need to encode the cage constraints.

1. binary_ne_grid (worth 10/100 marks)
    - An enconding of a FunPuzz grid (without cage constraints) built using only 
      binary not-equal constraints for both the row and column constraints.

2. nary_ad_grid (worth 10/100 marks)
    - An enconding of a FunPuzz grid (without cage constraints) built using only n-ary 
      all-different constraints for both the row and column constraints. 

3. caged_csp (worth 25/100 marks) 
    - An enconding built using your choice of (1) binary binary not-equal, or (2) 
      n-ary all-different constraints for the grid.
    - Together with FunPuzz cage constraints.

'''
from cspbase import *
import itertools


def binary_ne_grid(fpuzz_grid):
    # Initialization based on input grid
    size = fpuzz_grid[0][0]                 # Get size of the grid
    domain = list(range(1, size + 1))       # Get domain (1, n) for possible values
    csp = CSP(f'{size}x{size}-FunPuzz Binary Solver')     # Creat CSP object, with name

    # Initialization of variables
    var_array = []
    for i in range(size):
        var_row = []
        for j in range(size):
            var = Variable(f'V{i+1}{j+1}', domain)
            csp.add_var(var)
            var_row.append(var)
        var_array.append(var_row)

    # Adding row and column constraints for binary not-equal
    for i in range(size):
        for j in range(size):
            # Row constraints
            for k in range(j+1, size):
                # Each pair of cell in same row, values are not equal
                con = Constraint(f"Row{i+1}:[{i+1},{j+1}]!=[{i+1},{k+1}]", [var_array[i][j], var_array[i][k]])

                # Pairs that satisfy the constrain is added
                sat_tuples = [(x, y) for x in domain for y in domain if x != y]
                con.add_satisfying_tuples(sat_tuples)

                # Add to csp
                csp.add_constraint(con)

            # Column constraints
            for k in range(i+1, size):
                # Each pair of cell in same column, values are not equal
                con = Constraint(f"Col{j+1}:[{i+1},{j+1}]!=[{k+1},{j+1}]", [var_array[i][j], var_array[k][j]])

                # Pairs that satisfy the constrain is added
                sat_tuples = [(x, y) for x in domain for y in domain if x != y]
                con.add_satisfying_tuples(sat_tuples)

                # Add to csp
                csp.add_constraint(con)

    return csp, var_array
    


def nary_ad_grid(fpuzz_grid):
    # Initialization based on input grid
    size = fpuzz_grid[0][0]                 # Get size of the grid
    domain = list(range(1, size + 1))       # Get domain (1, n) for possible values
    csp = CSP(f'{size}x{size}-FunPuzz N-ary Solver')     # Creat CSP object, with name

    # Initialize variables
    var_array = []
    for i in range(size):
        row_vars = []
        for j in range(size):
            var = Variable(f'V{i+1}{j+1}', domain)
            csp.add_var(var)
            row_vars.append(var)
        var_array.append(row_vars)

    # Add n-ary all-different constraints for rows
    for row in var_array:
        con = Constraint(f"Row-{row[0].name[:-1]}", row)

        # Pairs that satisfy the constrain is added
        sat_tuples = list(itertools.permutations(domain, size))
        con.add_satisfying_tuples(sat_tuples)

        # Add to csp
        csp.add_constraint(con)

    # Add n-ary all-different constraints for columns
    for col_index in range(size):
        col_vars = [var_array[row_index][col_index] for row_index in range(size)]
        con = Constraint(f"Col-{col_vars[0].name[1:]}", col_vars)

        # Pairs that satisfy the constrain is added
        sat_tuples = list(itertools.permutations(domain, size))
        con.add_satisfying_tuples(sat_tuples)

        # Add to csp
        csp.add_constraint(con)

    return csp, var_array



def caged_csp(fpuzz_grid):
    # Initialization based on input grid
    csp, var_array = binary_ne_grid(fpuzz_grid) # assume choose binary not equal constrain
    # csp, var_array = nary_ad_grid(fpuzz_grid) # assume choose all different constrain
    domain = [i for i in range(1, fpuzz_grid[0][0] + 1)]

    # Helper function: calculate product within the loop
    def calculate_product(numbers):
        product = 1
        for number in numbers:
            product *= number
        return product

    # Process each cage in the puzzle
    for cage in fpuzz_grid[1:]:
        # Determine the number of variables in the cage
        size = len(cage) - 2  
        # Generate all possible value combinations
        row_com = list(itertools.product(domain, repeat=size))  

        # Variable initialization
        col_com = []
        vars = []

        # Identify the corresponding variables for the cage
        for var_index in cage[0:size]:
            vars.append(var_array[var_index // 10 - 1][var_index % 10 - 1])

        # Determine satisfying tuples based on the cage's constraint
        for row in row_com:
            if cage[-1] == 0:  # Sum condition
                if sum(row) == cage[-2]:
                    col_com.append(row)
            elif cage[-1] == 1:  # Difference condition
                if 2 * max(row) - sum(row) == cage[-2]:
                    col_com.append(row)
            elif cage[-1] == 3:  # Product condition
                if calculate_product(row) == cage[-2]:
                    col_com.append(row)
            elif cage[-1] == 2:  # Quotient condition
                if max(row) ** 2 / calculate_product(row) == cage[-2]:
                    col_com.append(row)

        # Create and add the constraint for the current cage
        con = Constraint(f"Cage-Solver: {cage[:-2]}", vars)
        con.add_satisfying_tuples(col_com)
        csp.add_constraint(con)

    return csp, var_array

