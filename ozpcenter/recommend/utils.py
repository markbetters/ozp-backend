"""
Static Util File
Contains Math Functions for recommendations
"""


def map_numbers(input_num, in_min, in_max, out_min, out_max):
    """
    y2 - y1 / x2 - x1
    out_max - in_max / out_min - in_min + input_num
    """
    slope_top = float(out_max) - float(in_max)
    slope_bottom = float(out_min) - float(in_min)
    if slope_bottom == 0:
        slope_bottom == 1
    slope = slope_top / slope_bottom
    output = input_num * slope + input_num
    return output
