import itertools
from collections.abc import Iterable
from typing import NewType

import networkx as nx

SPECIAL_GRAPHS_ADJACENCY_LISTS = {
    'Buckyball - Truncated Icosahedral Graph': {
        1: [2, 3, 4],
        2: [1, 55, 56],
        3: [1, 58, 60],
        4: [1, 57, 59],
        5: [8, 13, 14],
        6: [8, 12, 15],
        7: [8, 11, 16],
        8: [5, 6, 7],
        9: [13, 15, 25],
        10: [14, 16, 26],
        11: [7, 12, 24],
        12: [6, 11, 23],
        13: [5, 9, 18],
        14: [5, 10, 17],
        15: [6, 9, 19],
        16: [7, 10, 20],
        17: [14, 18, 30],
        18: [13, 17, 29],
        19: [15, 28, 32],
        20: [16, 27, 31],
        21: [26, 30, 46],
        22: [25, 29, 45],
        23: [12, 28, 38],
        24: [11, 27, 37],
        25: [9, 22, 32],
        26: [10, 21, 31],
        27: [20, 24, 35],
        28: [19, 23, 36],
        29: [18, 22, 43],
        30: [17, 21, 44],
        31: [20, 26, 42],
        32: [19, 25, 41],
        33: [35, 42, 53],
        34: [36, 41, 54],
        35: [27, 33, 40],
        36: [28, 34, 39],
        37: [24, 38, 40],
        38: [23, 37, 39],
        39: [36, 38, 52],
        40: [35, 37, 51],
        41: [32, 34, 50],
        42: [31, 33, 49],
        43: [29, 44, 48],
        44: [30, 43, 47],
        45: [22, 48, 50],
        46: [21, 47, 49],
        47: [44, 46, 60],
        48: [43, 45, 59],
        49: [42, 46, 58],
        50: [41, 45, 57],
        51: [40, 52, 56],
        52: [39, 51, 55],
        53: [33, 56, 58],
        54: [34, 55, 57],
        55: [2, 52, 54],
        56: [2, 51, 53],
        57: [4, 50, 54],
        58: [3, 49, 53],
        59: [4, 48, 60],
        60: [3, 47, 59]
    },
    'D30 - Rhombic Triacontahedral Graph': {
        1: [21, 22, 23],
        2: [24, 27, 30],
        3: [24, 29, 30],
        4: [26, 29, 32],
        5: [26, 28, 32],
        6: [25, 27, 31],
        7: [25, 28, 31],
        8: [24, 26, 29],
        9: [24, 25, 27],
        10: [25, 26, 28],
        11: [24, 25, 26],
        12: [22, 29, 30],
        13: [21, 27, 30],
        14: [23, 28, 32],
        15: [23, 28, 31],
        16: [22, 29, 32],
        17: [21, 27, 31],
        18: [21, 22, 30],
        19: [22, 23, 32],
        20: [21, 23, 31],
        21: [1, 13, 17, 18, 20],
        22: [1, 12, 16, 18, 19],
        23: [1, 14, 15, 19, 20],
        24: [2, 3, 8, 9, 11],
        25: [6, 7, 9, 10, 11],
        26: [4, 5, 8, 10, 11],
        27: [2, 6, 9, 13, 17],
        28: [5, 7, 10, 14, 15],
        29: [3, 4, 8, 12, 16],
        30: [2, 3, 12, 13, 18],
        31: [6, 7, 15, 17, 20],
        32: [4, 5, 14, 16, 19]
    },
    'Small Rhombicosidodecahedral Graph': {
        1: [2, 3, 4, 5],
        2: [1, 54, 55, 59],
        3: [1, 53, 56, 60],
        4: [1, 5, 58, 60],
        5: [1, 4, 57, 59],
        6: [24, 25, 57, 58],
        7: [12, 13, 16, 17],
        8: [9, 11, 19, 25],
        9: [8, 10, 18, 24],
        10: [9, 11, 12, 18],
        11: [8, 10, 13, 19],
        12: [7, 10, 14, 20],
        13: [7, 11, 15, 21],
        14: [12, 18, 20, 37],
        15: [13, 19, 21, 38],
        16: [7, 17, 21, 23],
        17: [7, 16, 20, 22],
        18: [9, 10, 14, 28],
        19: [8, 11, 15, 29],
        20: [12, 14, 17, 33],
        21: [13, 15, 16, 32],
        22: [17, 23, 31, 34],
        23: [16, 22, 30, 34],
        24: [6, 9, 27, 28],
        25: [6, 8, 26, 29],
        26: [25, 29, 46, 58],
        27: [24, 28, 45, 57],
        28: [18, 24, 27, 44],
        29: [19, 25, 26, 43],
        30: [23, 32, 36, 42],
        31: [22, 33, 35, 41],
        32: [21, 30, 38, 39],
        33: [20, 31, 37, 40],
        34: [22, 23, 41, 42],
        35: [31, 40, 41, 51],
        36: [30, 39, 42, 52],
        37: [14, 33, 40, 44],
        38: [15, 32, 39, 43],
        39: [32, 36, 38, 48],
        40: [33, 35, 37, 47],
        41: [31, 34, 35, 50],
        42: [30, 34, 36, 49],
        43: [29, 38, 46, 48],
        44: [28, 37, 45, 47],
        45: [27, 44, 47, 59],
        46: [26, 43, 48, 60],
        47: [40, 44, 45, 54],
        48: [39, 43, 46, 53],
        49: [42, 50, 52, 56],
        50: [41, 49, 51, 55],
        51: [35, 50, 54, 55],
        52: [36, 49, 53, 56],
        53: [3, 48, 52, 60],
        54: [2, 47, 51, 59],
        55: [2, 50, 51, 56],
        56: [3, 49, 52, 55],
        57: [5, 6, 27, 58],
        58: [4, 6, 26, 57],
        59: [2, 5, 45, 54],
        60: [3, 4, 46, 53]
    },
    'Small Rhombicuboctahedral Graph': {
        1: [2, 3, 4, 5],
        2: [1, 18, 22, 24],
        3: [1, 19, 22, 23],
        4: [1, 5, 21, 24],
        5: [1, 4, 20, 23],
        6: [10, 11, 20, 21],
        7: [10, 11, 12, 13],
        8: [10, 14, 20, 23],
        9: [11, 15, 21, 24],
        10: [6, 7, 8, 14],
        11: [6, 7, 9, 15],
        12: [7, 13, 15, 17],
        13: [7, 12, 14, 16],
        14: [8, 10, 13, 19],
        15: [9, 11, 12, 18],
        16: [13, 17, 19, 22],
        17: [12, 16, 18, 22],
        18: [2, 15, 17, 24],
        19: [3, 14, 16, 23],
        20: [5, 6, 8, 21],
        21: [4, 6, 9, 20],
        22: [2, 3, 16, 17],
        23: [3, 5, 8, 19],
        24: [2, 4, 9, 18]
    },
    'Great Rhombicosidodecahedral Graph': {
        1: [2, 3, 4],
        2: [1, 119, 120],
        3: [1, 118, 120],
        4: [1, 116, 117],
        5: [6, 7, 120],
        6: [5, 114, 115],
        7: [5, 113, 115],
        8: [9, 10, 115],
        9: [8, 111, 112],
        10: [8, 110, 112],
        11: [12, 13, 112],
        12: [11, 108, 109],
        13: [11, 107, 109],
        14: [15, 16, 109],
        15: [14, 105, 106],
        16: [14, 104, 106],
        17: [18, 19, 106],
        18: [17, 102, 103],
        19: [17, 101, 103],
        20: [21, 22, 103],
        21: [20, 99, 100],
        22: [20, 98, 100],
        23: [24, 25, 100],
        24: [23, 96, 97],
        25: [23, 95, 97],
        26: [27, 28, 97],
        27: [26, 93, 94],
        28: [26, 92, 94],
        29: [94, 116, 117],
        30: [63, 91, 96],
        31: [32, 33, 91],
        32: [31, 87, 88],
        33: [31, 86, 88],
        34: [35, 36, 88],
        35: [34, 84, 85],
        36: [34, 83, 85],
        37: [38, 85, 113],
        38: [37, 41, 110],
        39: [58, 73, 114],
        40: [86, 117, 119],
        41: [38, 64, 84],
        42: [64, 69, 84],
        43: [53, 55, 111],
        44: [64, 67, 108],
        45: [52, 77, 105],
        46: [65, 70, 102],
        47: [48, 49, 99],
        48: [47, 82, 95],
        49: [47, 80, 81],
        50: [51, 52, 79],
        51: [50, 74, 75],
        52: [45, 50, 75],
        53: [43, 75, 107],
        54: [72, 73, 74],
        55: [43, 73, 74],
        56: [61, 76, 78],
        57: [60, 89, 90],
        58: [39, 59, 118],
        59: [58, 60, 72],
        60: [57, 59, 61],
        61: [56, 60, 72],
        62: [66, 71, 87],
        63: [30, 66, 87],
        64: [41, 42, 44],
        65: [46, 66, 98],
        66: [62, 63, 65],
        67: [44, 68, 104],
        68: [67, 69, 70],
        69: [42, 68, 71],
        70: [46, 68, 71],
        71: [62, 69, 70],
        72: [54, 59, 61],
        73: [39, 54, 55],
        74: [51, 54, 55],
        75: [51, 52, 53],
        76: [56, 82, 89],
        77: [45, 80, 101],
        78: [56, 81, 82],
        79: [50, 80, 81],
        80: [49, 77, 79],
        81: [49, 78, 79],
        82: [48, 76, 78],
        83: [36, 86, 119],
        84: [35, 41, 42],
        85: [35, 36, 37],
        86: [33, 40, 83],
        87: [32, 62, 63],
        88: [32, 33, 34],
        89: [57, 76, 93],
        90: [57, 93, 116],
        91: [30, 31, 92],
        92: [28, 91, 96],
        93: [27, 89, 90],
        94: [27, 28, 29],
        95: [25, 48, 99],
        96: [24, 30, 92],
        97: [24, 25, 26],
        98: [22, 65, 102],
        99: [21, 47, 95],
        100: [21, 22, 23],
        101: [19, 77, 105],
        102: [18, 46, 98],
        103: [18, 19, 20],
        104: [16, 67, 108],
        105: [15, 45, 101],
        106: [15, 16, 17],
        107: [13, 53, 111],
        108: [12, 44, 104],
        109: [12, 13, 14],
        110: [10, 38, 113],
        111: [9, 43, 107],
        112: [9, 10, 11],
        113: [7, 37, 110],
        114: [6, 39, 118],
        115: [6, 7, 8],
        116: [4, 29, 90],
        117: [4, 29, 40],
        118: [3, 58, 114],
        119: [2, 40, 83],
        120: [2, 3, 5]
    },
    'Disdyakis Dodecahedral Graph': {
        1: [13, 14, 21, 22],
        2: [17, 19, 21, 23],
        3: [18, 20, 22, 24],
        4: [16, 17, 23, 25],
        5: [15, 19, 23, 26],
        6: [15, 18, 24, 26],
        7: [16, 20, 24, 25],
        8: [15, 16, 23, 24],
        9: [14, 17, 21, 25],
        10: [13, 18, 22, 26],
        11: [13, 19, 21, 26],
        12: [14, 20, 22, 25],
        13: [1, 10, 11, 21, 22, 26],
        14: [1, 9, 12, 21, 22, 25],
        15: [5, 6, 8, 23, 24, 26],
        16: [4, 7, 8, 23, 24, 25],
        17: [2, 4, 9, 21, 23, 25],
        18: [3, 6, 10, 22, 24, 26],
        19: [2, 5, 11, 21, 23, 26],
        20: [3, 7, 12, 22, 24, 25],
        21: [1, 2, 9, 11, 13, 14, 17, 19],
        22: [1, 3, 10, 12, 13, 14, 18, 20],
        23: [2, 4, 5, 8, 15, 16, 17, 19],
        24: [3, 6, 7, 8, 15, 16, 18, 20],
        25: [4, 7, 9, 12, 14, 16, 17, 20],
        26: [5, 6, 10, 11, 13, 15, 18, 19]
    },
    'Deltoidal Icositetrahedral Graph': {
        1: [15, 24, 26],
        2: [15, 23, 25],
        3: [16, 18, 20],
        4: [17, 19, 20],
        5: [16, 22, 26],
        6: [19, 22, 25],
        7: [18, 21, 24],
        8: [17, 21, 23],
        9: [15, 22, 25, 26],
        10: [15, 21, 23, 24],
        11: [16, 18, 24, 26],
        12: [17, 19, 23, 25],
        13: [16, 19, 20, 22],
        14: [17, 18, 20, 21],
        15: [1, 2, 9, 10],
        16: [3, 5, 11, 13],
        17: [4, 8, 12, 14],
        18: [3, 7, 11, 14],
        19: [4, 6, 12, 13],
        20: [3, 4, 13, 14],
        21: [7, 8, 10, 14],
        22: [5, 6, 9, 13],
        23: [2, 8, 10, 12],
        24: [1, 7, 10, 11],
        25: [2, 6, 9, 12],
        26: [1, 5, 9, 11]
    },
    'Icosidodecahedral Graph': {
        1: [2, 3, 4, 5],
        2: [1, 4, 23, 27],
        3: [1, 5, 24, 28],
        4: [1, 2, 26, 29],
        5: [1, 3, 25, 30],
        6: [7, 8, 9, 10],
        7: [6, 9, 11, 15],
        8: [6, 10, 12, 16],
        9: [6, 7, 14, 18],
        10: [6, 8, 13, 17],
        11: [7, 12, 15, 19],
        12: [8, 11, 16, 19],
        13: [10, 14, 17, 20],
        14: [9, 13, 18, 20],
        15: [7, 11, 21, 23],
        16: [8, 12, 22, 24],
        17: [10, 13, 22, 25],
        18: [9, 14, 21, 26],
        19: [11, 12, 27, 28],
        20: [13, 14, 29, 30],
        21: [15, 18, 23, 26],
        22: [16, 17, 24, 25],
        23: [2, 15, 21, 27],
        24: [3, 16, 22, 28],
        25: [5, 17, 22, 30],
        26: [4, 18, 21, 29],
        27: [2, 19, 23, 28],
        28: [3, 19, 24, 27],
        29: [4, 20, 26, 30],
        30: [5, 20, 25, 29]
    },
    'Deltoidal Hexecontahedral Graph': {
        1: [21, 49, 50],
        2: [21, 47, 48],
        3: [23, 25, 26],
        4: [22, 24, 26],
        5: [25, 27, 33],
        6: [24, 30, 36],
        7: [23, 28, 34],
        8: [22, 29, 35],
        9: [27, 30, 31],
        10: [28, 29, 32],
        11: [33, 38, 43],
        12: [34, 38, 46],
        13: [36, 37, 45],
        14: [35, 37, 44],
        15: [32, 40, 42],
        16: [31, 39, 41],
        17: [39, 43, 49],
        18: [40, 46, 50],
        19: [41, 45, 47],
        20: [42, 44, 48],
        21: [1, 2, 51, 52],
        22: [4, 8, 54, 56],
        23: [3, 7, 53, 56],
        24: [4, 6, 54, 55],
        25: [3, 5, 53, 55],
        26: [3, 4, 55, 56],
        27: [5, 9, 55, 57],
        28: [7, 10, 56, 58],
        29: [8, 10, 56, 60],
        30: [6, 9, 55, 59],
        31: [9, 16, 57, 59],
        32: [10, 15, 58, 60],
        33: [5, 11, 53, 57],
        34: [7, 12, 53, 58],
        35: [8, 14, 54, 60],
        36: [6, 13, 54, 59],
        37: [13, 14, 54, 62],
        38: [11, 12, 53, 61],
        39: [16, 17, 52, 57],
        40: [15, 18, 51, 58],
        41: [16, 19, 52, 59],
        42: [15, 20, 51, 60],
        43: [11, 17, 57, 61],
        44: [14, 20, 60, 62],
        45: [13, 19, 59, 62],
        46: [12, 18, 58, 61],
        47: [2, 19, 52, 62],
        48: [2, 20, 51, 62],
        49: [1, 17, 52, 61],
        50: [1, 18, 51, 61],
        51: [21, 40, 42, 48, 50],
        52: [21, 39, 41, 47, 49],
        53: [23, 25, 33, 34, 38],
        54: [22, 24, 35, 36, 37],
        55: [24, 25, 26, 27, 30],
        56: [22, 23, 26, 28, 29],
        57: [27, 31, 33, 39, 43],
        58: [28, 32, 34, 40, 46],
        59: [30, 31, 36, 41, 45],
        60: [29, 32, 35, 42, 44],
        61: [38, 43, 46, 49, 50],
        62: [37, 44, 45, 47, 48]
    },
    'Kocohl74': {
        1: [2, 3, 4],
        2: [1, 71, 74],
        3: [1, 72, 73],
        4: [1, 69, 70],
        5: [6, 43, 60],
        6: [5, 7, 50],
        7: [6, 8, 9],
        8: [7, 39, 40],
        9: [7, 41, 42],
        10: [11, 12, 31],
        11: [10, 21, 25],
        12: [10, 20, 22],
        13: [15, 18, 24],
        14: [15, 44, 47],
        15: [13, 14, 45],
        16: [17, 46, 47],
        17: [16, 18, 21],
        18: [13, 17, 22],
        19: [20, 21, 23],
        20: [12, 19, 24],
        21: [11, 17, 19],
        22: [12, 18, 23],
        23: [19, 22, 28],
        24: [13, 20, 26],
        25: [11, 26, 27],
        26: [24, 25, 35],
        27: [25, 30, 37],
        28: [23, 29, 35],
        29: [28, 30, 34],
        30: [27, 29, 33],
        31: [10, 33, 34],
        32: [40, 46, 48],
        33: [30, 31, 42],
        34: [29, 31, 41],
        35: [26, 28, 42],
        36: [38, 39, 43],
        37: [27, 38, 41],
        38: [36, 37, 40],
        39: [8, 36, 49],
        40: [8, 32, 38],
        41: [9, 34, 37],
        42: [9, 33, 35],
        43: [5, 36, 54],
        44: [14, 49, 52],
        45: [15, 48, 52],
        46: [16, 32, 56],
        47: [14, 16, 51],
        48: [32, 45, 57],
        49: [39, 44, 51],
        50: [6, 55, 58],
        51: [47, 49, 66],
        52: [44, 45, 65],
        53: [58, 63, 67],
        54: [43, 59, 63],
        55: [50, 59, 62],
        56: [46, 57, 66],
        57: [48, 56, 65],
        58: [50, 53, 61],
        59: [54, 55, 64],
        60: [5, 62, 64],
        61: [58, 68, 71],
        62: [55, 60, 72],
        63: [53, 54, 72],
        64: [59, 60, 71],
        65: [52, 57, 70],
        66: [51, 56, 69],
        67: [53, 70, 74],
        68: [61, 69, 73],
        69: [4, 66, 68],
        70: [4, 65, 67],
        71: [2, 61, 64],
        72: [3, 62, 63],
        73: [3, 68, 74],
        74: [2, 67, 73]
    },
    'https://houseofgraphs.org/graphs/3312': {
        1: [2, 3, 4],
        2: [1, 87, 88],
        3: [1, 85, 88],
        4: [1, 84, 86],
        5: [6, 7, 88],
        6: [5, 83, 87],
        7: [5, 81, 82],
        8: [83, 84, 86],
        9: [10, 11, 83],
        10: [9, 80, 86],
        11: [9, 79, 82],
        12: [28, 29, 80],
        13: [28, 45, 80],
        14: [16, 19, 81],
        15: [19, 78, 81],
        16: [14, 17, 82],
        17: [16, 18, 79],
        18: [17, 19, 20],
        19: [14, 15, 18],
        20: [18, 77, 78],
        21: [22, 23, 76],
        22: [21, 72, 75],
        23: [21, 73, 74],
        24: [25, 34, 85],
        25: [24, 26, 27],
        26: [25, 33, 38],
        27: [25, 32, 34],
        28: [12, 13, 31],
        29: [12, 30, 37],
        30: [29, 31, 36],
        31: [28, 30, 39],
        32: [27, 33, 40],
        33: [26, 32, 35],
        34: [24, 27, 43],
        35: [33, 38, 44],
        36: [30, 37, 42],
        37: [29, 36, 41],
        38: [26, 35, 41],
        39: [31, 42, 45],
        40: [32, 43, 44],
        41: [37, 38, 47],
        42: [36, 39, 47],
        43: [34, 40, 46],
        44: [35, 40, 50],
        45: [13, 39, 51],
        46: [43, 65, 85],
        47: [41, 42, 64],
        48: [53, 57, 63],
        49: [52, 56, 60],
        50: [44, 52, 61],
        51: [45, 53, 62],
        52: [49, 50, 65],
        53: [48, 51, 64],
        54: [59, 63, 71],
        55: [58, 60, 70],
        56: [49, 58, 61],
        57: [48, 59, 62],
        58: [55, 56, 67],
        59: [54, 57, 69],
        60: [49, 55, 66],
        61: [50, 56, 67],
        62: [51, 57, 69],
        63: [48, 54, 68],
        64: [47, 53, 68],
        65: [46, 52, 66],
        66: [60, 65, 72],
        67: [58, 61, 75],
        68: [63, 64, 74],
        69: [59, 62, 73],
        70: [55, 72, 75],
        71: [54, 73, 74],
        72: [22, 66, 70],
        73: [23, 69, 71],
        74: [23, 68, 71],
        75: [22, 67, 70],
        76: [21, 77, 78],
        77: [20, 76, 79],
        78: [15, 20, 76],
        79: [11, 17, 77],
        80: [10, 12, 13],
        81: [7, 14, 15],
        82: [7, 11, 16],
        83: [6, 8, 9],
        84: [4, 8, 87],
        85: [3, 24, 46],
        86: [4, 8, 10],
        87: [2, 6, 84],
        88: [2, 3, 5]
    },
    'https://houseofgraphs.org/graphs/31104': {
        1: [2, 3, 4, 5],
        2: [1, 4, 9, 10],
        3: [1, 5, 8, 10],
        4: [1, 2, 6, 8],
        5: [1, 3, 7, 9],
        6: [4, 7, 8, 10],
        7: [5, 6, 9, 10],
        8: [3, 4, 6, 9],
        9: [2, 5, 7, 8],
        10: [2, 3, 6, 7]
    },
    'Utility Graph': {
        1: [2, 3, 4],
        2: [1, 5, 6],
        3: [1, 5, 6],
        4: [1, 5, 6],
        5: [2, 3, 4],
        6: [2, 3, 4]
    },
    'Errara Graph': {
        1: [3, 4, 5, 11, 12],
        2: [6, 7, 8, 9, 10],
        3: [1, 4, 5, 13, 14],
        4: [1, 3, 11, 13, 16],
        5: [1, 3, 12, 14, 17],
        6: [2, 7, 8, 15, 16],
        7: [2, 6, 9, 15, 17],
        8: [2, 6, 10, 13, 16],
        9: [2, 7, 10, 14, 17],
        10: [2, 8, 9, 13, 14],
        11: [1, 4, 12, 15, 16],
        12: [1, 5, 11, 15, 17],
        13: [3, 4, 8, 10, 14, 16],
        14: [3, 5, 9, 10, 13, 17],
        15: [6, 7, 11, 12, 16, 17],
        16: [4, 6, 8, 11, 13, 15],
        17: [5, 7, 9, 12, 14, 15]
    },
    'Dragon Curve Blob 6': {
        1: [4, 15],
        2: [8, 17],
        3: [8, 17],
        4: [1, 14],
        5: [7, 14],
        6: [7, 14],
        7: [5, 6],
        8: [2, 3],
        9: [11, 16],
        10: [13, 15],
        11: [9, 12],
        12: [11, 16, 17],
        13: [10, 16, 17],
        14: [4, 5, 6, 15],
        15: [1, 10, 14, 16],
        16: [9, 12, 13, 15],
        17: [2, 3, 12, 13]
    }
}

AdjacencyList = NewType('AdjacencyList', dict[int, list[int]])


def ladder_ring_graph(size: int):
    ring = nx.ladder_graph(size)
    ring.add_edge(size, size * 2 - 1)
    ring.add_edge(0, size - 1)
    return ladder_ring_graph


def ladder_mobius_graph(size: int):
    mobius = nx.ladder_graph(size)
    mobius.add_edge(size, size - 1)
    mobius.add_edge(0, size * 2 - 1)
    return mobius


def _cylinder_edges(circumference: int, length: int) -> Iterable[tuple[int, int]]:
    for k in range(length):
        start = k * circumference
        stop = (k + 1) * circumference - 1
        if k > 0:
            yield start, start - circumference
            yield stop, stop - circumference
        for i in range(start, stop):
            yield i, i + 1
            if k > 0:
                yield i, i - circumference
        yield stop, start


def cylinder_graph(circumference: int, length: int) -> nx.Graph:
    return nx.Graph(_cylinder_edges(circumference, length))


def _spiral_edges(n, k) -> Iterable[tuple[int, int]]:
    for i in range(n):
        yield i, i + 1
        if i - k >= 0:
            yield i, i - k
    yield n, n - k


def spiral_graph(n, k) -> nx.Graph:
    return nx.Graph(_spiral_edges(n, k))


def _spiral_torus_edges(n, k) -> Iterable[tuple[int, int]]:
    yield from _spiral_edges(n - 1, k)
    yield n - 1, 0
    for i in range(k):
        yield i, n - k + i


def spiral_torus_graph(n, k) -> nx.Graph:
    return nx.Graph(_spiral_torus_edges(n, k))


def adjacency_edges(adjacency_list: AdjacencyList) -> Iterable[tuple[int, int]]:
    yield from itertools.chain.from_iterable(
        ((k, t) for t in v)
        for k, v
        in adjacency_list.items()
    )


def from_adjacency_lists(adjacency_lists: dict[str, AdjacencyList]) -> dict[str, nx.Graph]:
    items = (
        (name, adjacency_edges(adjacency_list))
        for name, adjacency_list
        in adjacency_lists.items()
    )

    return {n: nx.Graph(list(e)) for n, e in items}


def special_graphs():
    return from_adjacency_lists(SPECIAL_GRAPHS_ADJACENCY_LISTS)


def atlas():
    """
    Generate a dictionary of various graph structures and models based on the provided atlas.
    The function creates different types of graphs and models using NetworkX library.
    The generated graphs include Tetrahedron, Cube, Octahedron, Dodecahedron, Icosahedron, Tesseract, Truncated Cube,
    Truncated Tetrahedron, Ladder, Ring, Möbius, Cylinder, Spiral, Spiral Torus, and Circulant[10,[2]].
    Additionally, the function includes adjacency mappings for specific named graphs like
    Buckyball - Truncated Icosahedral Graph, D30 - Rhombic Triacontahedral Graph, Small Rhombicosidodecahedral Graph,
    Small Rhombicuboctahedral Graph, Great Rhombicosidodecahedral Graph, Disdyakis Dodecahedral Graph,
    Deltoidal Icositetrahedral Graph, Icosidodecahedral Graph, Deltoidal Hexecontahedral Graph, Kocohl74,
    Utility Graph, Errara Graph, and Dragon Curve Blob 6.
    The adjacency mappings define the connections between nodes in each named graph.
    The function returns a dictionary
    containing the named graphs as keys and their corresponding NetworkX graph objects as values.
    """

    graph_atlas = {
        'Tetrahedron': nx.tetrahedral_graph(),
        'Cube': nx.hypercube_graph(3),
        'Octahedron': nx.octahedral_graph(),
        'Dodecahedron': nx.dodecahedral_graph(),
        'Icosahedron': nx.icosahedral_graph(),
        'Tesseract': nx.hypercube_graph(4),
        'Truncated Cube': nx.truncated_cube_graph(),
        'Truncated Tetrahedron': nx.truncated_tetrahedron_graph(),
        'Ladder': nx.ladder_graph(16),
        'Ring': ladder_ring_graph(16),
        'Möbius': ladder_mobius_graph(16),
        'Cylinder': cylinder_graph(6, 8),
        'Spiral': spiral_graph(18, 8),
        'Spiral Torus': spiral_torus_graph(128, 8),
        'Circulant[10,[2]]': nx.circulant_graph(10, [2])
    }

    graph_atlas.update(special_graphs())

    return graph_atlas
