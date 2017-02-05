'''
 * Copyright (c) 2014, 2015 Entertainment Intelligence Lab, Georgia Institute of Technology.
 * Originally developed by Mark Riedl.
 * Last edited by Mark Riedl 05/2015
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
'''

import sys, pygame, math, numpy, random, time, copy, operator
from pygame.locals import *

from constants import *
from utils import *
from core import *

# Creates a pathnode network that connects the midpoints of each navmesh together
def myCreatePathNetwork(world, agent = None):
    nodes = []
    edges = []
    polys = []
    ### YOUR CODE GOES BELOW HERE ###
    points = world.getPoints()
    obstacles = world.getObstacles()
    temp = []
    for p1 in points:
        for p2 in points:
            for p3 in points:
                if p1 == p2 or p1 == p3 or p2 == p3:
                    continue
                if not checkCollision1(world, temp, p1, p2, p3) and not checkCollision2(world, obstacles, temp, p1, p2, p3):
                    temp.append(list((p1, p2, p3)))

    # Get rid of duplicates
    for t in temp:
        t.sort()
        if t not in polys:
            polys.append(t)

    for p1 in polys:
        for p2 in polys:
            if p1 == p2:
                continue
            if polygonsAdjacent(p1, p2):
                print p1, p2
                merged = merge(p1, p2)
                print 'merged: ', merged
                if isConvex(merged):
                    # drawPolygon(merged, world.debug, (0,0,0), 10, False)
                    polys.remove(p1)
                    polys.remove(p2)
                    polys.append(merged)

    print len(polys)
    for p in polys:
        print p
        # if (457, 422) not in p:
        #     continue
        # drawPolygon(p, world.debug, color=(0, 0, 0), width=10, center=False)


    # Get rid of polys with obstacles connected pt. 1
    # Problematic for runrandomnavigator2.py
    # temp = []
    # for p in polys:
    #     if not validPoly(obstacles, p[0], p[1], p):
    #         continue
    #     elif not validPoly(obstacles, p[0], p[2], p):
    #         continue
    #     elif not validPoly(obstacles, p[1], p[2], p):
    #         continue
    #     temp.append(p)

    # Reassign polys correct values
    # polys = temp

    # print len(polys)
    # rem_list = []
    # for p in polys:
    #     print '\npoly: ---> ', p
    #     for obstacle in obstacles:
    #         print '\n', obstacle.getPoints()
    #         count = 0
    #         for pt in obstacle.getPoints():
    #             print pointInsidePolygonPoints(pt, p)
    #             if not pointInsidePolygonPoints(pt, p):
    #                 continue
    #             else:
    #                 count += 1
    #         if count == len(obstacle.getPoints()):
    #             rem_list.append(p)

        # if (0, 0) not in p:
        #     continue
        # if (921, 300) not in p:
        #     continue
        # if (1224, 900) not in p:
        #     continue
        # drawPolygon(p, world.debug, color=(0,0,0), width=5, center=False)

    # print len(rem_list)
    # for rem in rem_list:
        # print rem
        # if (0, 0) not in rem:
        #     continue
        # if (300, 515) not in rem:
        #     continue
        # drawPolygon(rem, world.debug, color=(0,0,0), width=5, center=False)
        # polys.remove(rem)

    return nodes, edges, polys


def checkCollision1(world, polys, p1, p2, p3):
    lines = world.getLines()
    for p in polys:
        lines.append((p[0], p[1]))
        lines.append((p[0], p[2]))
        lines.append((p[1], p[2]))

    if rayTraceWorldNoEndPoints(p2, p3, lines) is not None and (p2, p3) not in lines and (p3, p2) not in lines:
        return True
    elif rayTraceWorldNoEndPoints(p1, p2, lines) is not None and (p1, p2) not in lines and (p2, p1) not in lines:
        return True
    elif rayTraceWorldNoEndPoints(p1, p3, lines) is not None and (p1, p3) not in lines and (p3, p1) not in lines:
        return True

    return False


def checkCollision2(world, obstacles, polys, p1, p2, p3):
    lines = world.getLines()
    for p in polys:
        lines.append((p[0], p[1]))
        lines.append((p[0], p[2]))
        lines.append((p[1], p[2]))

    for obstacle in obstacles:
        mid1 = midpt(p2, p3)
        mid2 = midpt(p1, p2)
        mid3 = midpt(p1, p3)
        # Check our triangle inside any of the pre-made obstacles
        if pointInsidePolygonLines(mid1, obstacle.getLines()) and (p2, p3) not in lines and (p3, p2) not in lines:
            return True
        elif pointInsidePolygonLines(mid2, obstacle.getLines()) and (p1, p2) not in lines and (p2, p1) not in lines:
            return True
        elif pointInsidePolygonLines(mid3, obstacle.getLines()) and (p1, p3) not in lines and (p3, p1) not in lines:
            return True

        # Check pre-made obstacles inside our triangle
        # midpoint = [0,0]
        # for point in obstacle.getPoints():
        #     midpoint[0] += point[0]
        #     midpoint[1] += point[1]
        #
        # midpoint[0] /= len(obstacle.getPoints())
        # midpoint[1] /= len(obstacle.getPoints())
        # if pointInsidePolygonPoints(midpoint, (p1, p2, p3)):
        #     return True

        # Check pre-made obstacles inside our triangle
        for x in range(len(obstacle.getPoints())):
            pt1 = obstacle.getPoints()[x]
            if x == len(obstacle.getPoints()) - 1:
                pt2 = obstacle.getPoints()[0]
            else:
                pt2 = obstacle.getPoints()[x + 1]
            mid4 = midpt(pt1, pt2)
            if (pointInsidePolygonPoints(mid4, (p1, p2, p3))):
                return True

    return False


def midpt(p1, p2):
    midX = ((p1[0] + p2[0]) / 2)
    midY = ((p1[1] + p2[1]) / 2)
    return (midX, midY)


def merge(poly1, poly2):
    pts = []
    for pt in poly1:
        pts.append(pt)
    for pt in poly2:
        if pt not in pts:
            pts.append(pt)
    return pts
