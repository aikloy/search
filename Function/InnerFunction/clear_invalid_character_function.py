from Variable.invalid_character_variable import INVALID_CHARACTER


def clear_invalid_character(x):
    for invalid_character in INVALID_CHARACTER:
        x = x.replace(invalid_character, "")

    return x
