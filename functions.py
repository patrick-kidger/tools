"""Helper functions"""

def deep_locate_variable(top_object, variable_name):
    """Used to extend getattr etc. to finding subattributes."""
    variable_descent = variable_name.split('.')
    prev_variable = top_object
    while len(variable_descent) > 1:
        next_variable_name = variable_descent.pop(0)
        prev_variable = deepgetattr(prev_variable, next_variable_name)
    return prev_variable, variable_descent[0]
        
def deepgetattr(top_object, variable_name):
    """Use as getattr, but can find subattributes separated by a '.', e.g. deepgetattr(a, 'b.c')"""
    penultimate_variable, last_variable_name = deep_locate_variable(top_object, variable_name)
    return getattr(penultimate_variable, last_variable_name)

    
def deepsetattr(top_object, variable_name, value):
    """Use as setattr, but can find subattributes separated by a '.', e.g. deepsetattr(a, 'b.c')"""
    penultimate_variable, last_variable_name = deep_locate_variable(top_object, variable_name)
    setattr(penultimate_variable, last_variable_name, value)
