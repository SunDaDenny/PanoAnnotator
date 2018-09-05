import numpy as np
import math

def vectorAdd(v1, v2):

    ans = (v1[0]+v2[0], v1[1]+v2[1], v1[2]+v2[2])
    return ans

def vectorSum(vList):

    ans = (0, 0, 0)
    for v in vList:
        ans = vectorAdd(ans, v)
    return ans

def vectorCross(v1, v2):

    v1 = list(v1)
    v2 = list(v2)
    ans = tuple(np.cross(v1,v2))
    return ans

def vectorDot(v1, v2):

    ans = v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
    return ans

def vectorMultiplyC(v1, C):
    
    ans = (v1[0]*C, v1[1]*C, v1[2]*C)
    return ans

def vectorDividedC(v1, C):
    
    ans = (float(v1[0])/C, float(v1[1])/C, float(v1[2])/C)
    return ans

def pointsMean(pList):
    
    sum_= vectorSum(pList)
    ans = vectorDividedC(sum_, len(pList))
    return ans

def pointsDistance(p1, p2):

    vec = [p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]]
    dis = math.sqrt(math.pow(vec[0], 2) + 
                    math.pow(vec[1], 2) + 
                    math.pow(vec[2], 2) )
    return dis

def pointsDirection(p1, p2):

    vec = [p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]]
    scalar = np.linalg.norm(vec)
    ans = (vec[0]/scalar, vec[1]/scalar, vec[2]/scalar)
    return ans

def pointsDirectionPow(p1, p2, pow_):
    vec = [p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]]
    ans = (math.pow(vec[0],pow_), math.pow(vec[1],pow_), 
            math.pow(vec[2],pow_))
    return ans

def pointsNormal(c, p1, p2):

    vec1 = pointsDirection(c, p1)
    vec2 = pointsDirection(c, p2)
    normal = vectorCross(vec1, vec2)
    return normal

def pointsSample(p1, p2, rate):

    ans = [p1]
    vec = pointsDirectionPow(p1, p2, 1)
    step = vectorDividedC(vec, rate)

    for i in range(1, rate):
        xyz = vectorAdd(p1, vectorMultiplyC(step, i))
        ans.append(xyz)
    ans.append(p2)
    return ans

def planeEquation(normal, p):
    
    d = -vectorDot(normal, p)
    equation = normal + (d,)
    return equation

def normal2color(normal):

    vec = vectorMultiplyC(normal, -0.5)
    color = vectorAdd(vec, (0.5,0.5,0.5))

    return color
