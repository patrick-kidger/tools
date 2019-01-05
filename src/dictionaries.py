_sentinel = object()


def extract_keys(dict, keys, no_key_val=_sentinel):
    """Removes the specified keys from the given dictionary, and returns a dictionary containing those key:value
    pairs. Default behaviour is to ignore those keys which can't be found in the original dictionary. The optional
    argument :no_key_val: can be set to what value missing keys should take in the returned dictionary."""

    return_dict = {}
    for key in keys:
        val = dict.pop(key, no_key_val)
        if val is not _sentinel:
            return_dict[key] = val
    return return_dict


def update_without_overwrite(dict1, dict2):
    """As dict.update, except that existing keys in :dict1: are not overwritten with matching keys in :dict2:."""
    for k, v in dict2.items():
        if k not in dict1:
            dict1[k] = v
