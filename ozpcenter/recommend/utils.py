"""
Static Util File
Contains Math Functions for recommendations
"""


def map_numbers(input_num, old_min, old_max, new_min, new_max):
    """
    Linear Conversion between ranges used for normalization

    http://stackoverflow.com/questions/929103/convert-a-number-range-to-another-range-maintaining-ratio
    """
    old_value = float(input_num)
    old_min = float(old_min)
    old_max = float(old_max)
    new_min = float(new_min)
    new_max = float(new_max)

    old_range = (old_max - old_min)

    new_value = None

    if new_min == new_max:
        new_value = new_min
    elif old_range == 0:
        new_value = new_min
    else:
        new_range = (new_max - new_min)
        new_value = (((old_value - old_min) * new_range) / old_range) + new_min

    return new_value
