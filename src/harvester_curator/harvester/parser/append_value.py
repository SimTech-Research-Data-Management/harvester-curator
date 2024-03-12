def append_value(dict_: dict, key_: str, value_: str) -> dict:
    """
    This function appends a given value to a dictionary if it is not none.

    Args:
        dict_ (dict): A dictionary for appending a given value
        key_ (str): A string representing the key
        value_ (str): A sring value to be added

    Returns:
        dict_ (dict): A dictionary with appended value
    """
    if value_:
        if key_ in dict_:
            dict_[key_].append(value_)
        else:
            dict_[key_] = [value_]
    
    return dict_