import sys
import numpy as np
import math

def vectorAdd(vec1, vec2):

    vec = (vec1[0]+vec2[0], vec1[1]+vec2[1], vec1[2]+vec2[2])
    return vec

def calcPointsDirection(p1, p2):
    
    vec = [p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]]
    scalar = np.linalg.norm(vec)

    return (vec[0]/scalar, vec[1]/scalar, vec[2]/scalar)

def calcPointsDistance(p1, p2):

    vec = [p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]]
    dis = math.sqrt(math.pow(vec[0], 2) + 
                    math.pow(vec[1], 2) + 
                    math.pow(vec[2], 2) )
    return dis
    

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
        dist = gps[i].getDistance(gps[(i+1)%n])
        axis = 0 if dist[0] >= dist[2] else 1

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
        edge.center = getPointsAvg(edge.points)

    #calculate manhattan corner points
    manhPoints = []
    for i in range(len(edges)):
        if edges[i].axis == 0:
            manhPoints.append((edges[i-1].center[0], 0, edges[i].center[2]))
        elif edges[i].axis == 1:
            manhPoints.append((edges[i].center[0], 0, edges[i-1].center[2]))

    return manhPoints


def calcCenterRegionAvgVal(data, centerPos, steps):
    
    lt, rb = calcCenterRegionPos(centerPos, steps, data.shape)
    region = getRegionData(data, lt, rb)
    avgVal = np.nanmean(region)

    return avgVal

def calcCenterRegionPos(centerPos, steps, size):

    lt = (centerPos[0] - steps[0], centerPos[1] - steps[1])
    rb = (centerPos[0] + steps[0], centerPos[1] + steps[1])

    lt = checkBoundary(lt, size)
    rb = checkBoundary(rb, size)

    return lt, rb

def checkBoundary(pos, size):
    
    x = pos[0]; y = pos[1]
    if pos[0] < 0:
        x = 0
    elif pos[0] > size[0]:
        x = size[0]
    if pos[1] < 0:
        y = 0
    elif pos[1] > size[1]:
        y = size[1]
    
    return (x, y)

def getRegionData(data, lt, rb):

    regionDate = data[lt[0]:rb[0], lt[1]:rb[1]]
    return regionDate

def getPointsAvg(points):
    
    avg = [0, 0, 0]
    for p in points:
        for i in range(3):
            avg[i] = avg[i] + p.xyz[i]
    for i in range(3):
        avg[i] = avg[i]/ (len(points))
    
    return tuple(avg)


