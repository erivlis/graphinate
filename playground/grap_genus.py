# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 09:04:01 2020

@author: saipr
"""
import math

import networkx as nx


def genus(G: nx.Graph):
    # get number of vertexes, edges, max number of edges
    v = G.number_of_edges()
    e = G.number_of_edges()
    maxf = math.floor((2 / 3) * e)

    # upper bound of the genus
    upper = ((v - 3) * (v - 4)) / 12
    lower = (1 / 16) * e - (1 / 2) * (v - 2)

    # check if upper or lower are incidental or the same, if so, return answer
    if upper - lower < 1:
        return f"Genus is {upper} or {lower}"

    # else: make the array of possible face and genus values
    grray = [i for i in range(math.floor(lower), math.ceil(upper))]
    frray = [i for i in range(0, maxf)]

    # now, find the first face value that fits the equation
    start = 1  # index of first face that fits
    for f in range(1, len(frray)):
        left = v - e + frray[f]
        right = 2 - 2 * grray[0]
        if left == right:
            start = f
            break
    # next find the last genus that fits the max face value
    end = len(grray)
    for g in range(0, len(grray)):
        left = v - e + maxf
        right = 2 - 2 * grray[g]
        if left == right:
            end = g
            break
            # now print out the possible face/genus combinations for the graph
    cases = []
    for f in range(start, len(frray)):
        for g in range(0, end):
            left = v - e + frray[f]
            right = 2 - 2 * grray[g]
            if left == right:
                cases.append((frray[f], grray[g]))

    # results
    print("Upper Equals:", upper)
    print("Lower Equals:", lower)
    print("Genus at face = 0:", end)
    print("Face at lower bound genus:", start)
    print("Number of possible genus situations:", len(cases))
    print("Cases of (face, genus) that fit this graph:", cases)
    return None


if __name__ == '__main__':
    # --------------------------------Tests----------------------------------------#
    three = nx.erdos_renyi_graph(50, .7, seed=999)
    genus(three)
