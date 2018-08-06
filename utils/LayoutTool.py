import sys
import numpy as np
import math

from .GeometryTool import *

def pointsAlignAxis(p1, p2):

    dist = pointsDirectionPow(p1, p2, 2)
    axis = 0 if dist[0] >= dist[2] else 1
    return axis

def vectorAlignAxis(v1):

    vec = [abs(e) for e in list(v1)]
    axis = vec.index(max(vec))
    return axis

def alignManhattan(gps):

    class Edge:
        def __init__(self, axis, p1):
            self.axis = axis
            self.points = [p1]
            self.center = (0, 0, 0)

    n = len(gps)
    if n < 2:
        print('cant align manh world')
        return
    
    #create edges, calculate axis type and contain points
    edges = []
    for i in range(n):
        #dist = pointsDirectionPow(gps[i].xyz, gps[(i+1)%n].xyz, 2)
        #axis = 0 if dist[0] >= dist[2] else 1
        axis = pointsAlignAxis(gps[i].xyz, gps[(i+1)%n].xyz)

        if len(edges) == 0:
            edges.append(Edge(axis, gps[i]))
        elif not edges[-1].axis == axis:
            edges[-1].points.append(gps[i])
            edges.append(Edge(axis, gps[i]))
        elif edges[-1].axis == axis:
            edges[-1].points.append(gps[i])

    #merge last edge to first if they have same axis
    if edges[0].axis == edges[-1].axis:
        edges[0].points += edges[-1].points
        edges.pop()

    #calculate each edge's center position
    for edge in edges:
        pList = [p.xyz for p in edge.points]
        edge.center = pointsMean(pList)

    #calculate manhattan corner points
    manhPoints = []
    for i in range(len(edges)):
        if edges[i].axis == 0:
            manhPoints.append((edges[i-1].center[0], 0, edges[i].center[2]))
        elif edges[i].axis == 1:
            manhPoints.append((edges[i].center[0], 0, edges[i-1].center[2]))

    return manhPoints