def register(name_str, registration_dict):
    """A decorator allowing for the decorated object to be registered in a dictionary."""
    def wrapper(input_val):
        registration_dict[name_str] = input_val
        return input_val
    return wrapper

def record(registration_list):
    """A decorator allowing for the decorated object to be recorded in a list."""
    def wrapper(input_val):
        registration_list.append(input_val)
        return input_val
    return wrapper