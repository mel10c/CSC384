#Look for #IMPLEMENT tags in this file. These tags indicate what has
#to be implemented to complete problem solution.  

'''This file will contain different constraint propagators to be used within 
   bt_search.

   propagator == a function with the following template
      propagator(csp, newly_instantiated_variable=None)
           ==> returns (True/False, [(Variable, Value), (Variable, Value) ...]

      csp is a CSP object---the propagator can use this to get access
      to the variables and constraints of the problem. The assigned variables
      can be accessed via methods, the values assigned can also be accessed.

      newly_instaniated_variable is an optional argument.
      if newly_instantiated_variable is not None:
          then newly_instantiated_variable is the most
           recently assigned variable of the search.
      else:
          progator is called before any assignments are made
          in which case it must decide what processing to do
           prior to any variables being assigned. SEE BELOW

       The propagator returns True/False and a list of (Variable, Value) pairs.
       Return is False if a deadend has been detected by the propagator.
       in this case bt_search will backtrack
       return is true if we can continue.

      The list of variable values pairs are all of the values
      the propagator pruned (using the variable's prune_value method). 
      bt_search NEEDS to know this in order to correctly restore these 
      values when it undoes a variable assignment.

      NOTE propagator SHOULD NOT prune a value that has already been 
      pruned! Nor should it prune a value twice

      PROPAGATOR called with newly_instantiated_variable = None
      PROCESSING REQUIRED:
        for plain backtracking (where we only check fully instantiated 
        constraints) 
        we do nothing...return true, []

        for forward checking (where we only check constraints with one
        remaining variable)
        we look for unary constraints of the csp (constraints whose scope 
        contains only one variable) and we forward_check these constraints.


      PROPAGATOR called with newly_instantiated_variable = a variable V
      PROCESSING REQUIRED:
         for plain backtracking we check all constraints with V (see csp method
         get_cons_with_var) that are fully assigned.

         for forward checking we forward check all constraints with V
         that have one unassigned variable left

   '''

def prop_BT(csp, newVar=None):
    '''Do plain backtracking propagation. That is, do no 
    propagation at all. Just check fully instantiated constraints'''

    if not newVar:
        return True, []
    for c in csp.get_cons_with_var(newVar):
        if c.get_n_unasgn() == 0:
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())
            if not c.check(vals):
                return False, []
    return True, []

def prop_FC(csp, newVar=None):
    '''Do forward checking. That is check constraints with 
       only one uninstantiated variable. Remember to keep 
       track of all pruned variable,value pairs and return '''
    # Variables initialization
    pruned = []

    # Determining constrains (list) to check
    if not newVar:
        constraints = csp.get_all_cons()
    else:
        constraints = csp.get_cons_with_var(newVar)   # restricts attention

    # Perform forward checking on the selected constraints
    for con in constraints:
        # If has exactly one unassgined var, iterates over each variable in scope
        if con.get_n_unasgn() == 1:

            # vars = con.get_scope()
            # for var in vars:
            #     if not var.is_assigned():
            #         domain = var.cur_domain()
            #
            #         for val in domain:
            #             var.assign(val)
            #             vals = [v.get_assigned_value() for v in vars]
            #                 
            #             if not con.check(vals):
            #                 cur_domain = var.in_cur_domain(val)
            #                 if cur_domain:
            #                     var.prune_value(val)
            #                     pruned.append((var, val))
            #
            #             var.unassign()
            #             if var.cur_domain_size() == 0:
            #                 return False, pruned

            # Get unassigned variable and its domain
            unassigned_vars = con.get_unasgn_vars()[0]
            domain = unassigned_vars.cur_domain()

            # Prune domain values of the unassigned variable that don't have support
            for value in domain:
                # Assign the value to check for support
                unassigned_vars.assign(value)
                if not con.has_support(unassigned_vars, value):
                    # If no support, and add to pruned list
                    unassigned_vars.prune_value(value)
                    pruned.append((unassigned_vars, value))
                unassigned_vars.unassign()  # Undo assignment

                # DWO case, deadend
                if unassigned_vars.cur_domain_size() == 0:
                    return False, pruned 

    return True, pruned 


def prop_FI(csp, newVar=None):
    '''Do full inference. If newVar is None we initialize the queue
       with all variables.'''
    # Variables initialization
    pruned = []

    # Determining constrains (queue) to check
    if newVar == None:
        con_queue = csp.get_all_cons()
    else:
        con_queue = csp.get_cons_with_var(newVar)

    # While queue is not empty
    while con_queue:
        con = con_queue.pop(0)              # Get the constain with index 0 in queue
        vars = con.get_scope()              # Get all varibles assoc. with constain
        for var in vars:
            cur_domain = var.cur_domain()   # Get variables's domain
            # Iterate over all current domain values of the unassigned variable
            for value in cur_domain:
                if not con.has_support(var, value):
                    # If there's no support for this value, prune the value
                    var.prune_value(value)
                    pruned.append((var, value))
                    # DWO case, deadend
                    if var.cur_domain_size() == 0:
                        return False, pruned
                    # If not DWO, add relevant constraints 
                    else:
                        for c in csp.get_cons_with_var(var):
                            if c not in con_queue:
                                con_queue.append(c)

    return True, pruned


