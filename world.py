import math
import media
import pygame
import texture
import numpy
import random
from OpenGL.GL import *
from OpenGL.arrays import ArrayDatatype as ADT

currentworld = None
worldsize = (1,1)

def drawsquare(pos, size, texture = None, level=0.0):
    if texture:
        texture()
    else:
        glDisable(GL_TEXTURE_2D)
    glPushMatrix()
    glTranslate(pos[0], pos[1], 0)
    glBegin(GL_QUADS)
    glTexCoord(0.0, 0.0)
    glVertex(0.0, 0.0, level)
    glTexCoord(0.0, 1.0)
    glVertex(0.0, size[1], level)
    glTexCoord(1.0, 1.0)
    glVertex(size[0], size[1], level)
    glTexCoord(1.0, 0.0)
    glVertex(size[0], 0.0, level)
    glEnd()
    glPopMatrix()

def getworld():
    global currentworld
    return currentworld

def setworldsize(ws):
    global worldsize
    worldsize = ws

def transitionto(world):
    global currentworld
    currentworld = world(currentworld)

class buffer:
    def __init__(self, vertbuffer, indexbuffer):
        self.buffer = glGenBuffers(1)
        self.indexbuffer = indexbuffer
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
        self.numverts = len(vertbuffer)
        vertbuffer = convertbuffer(vertbuffer)
        glBufferData(GL_ARRAY_BUFFER, ADT.arrayByteCount(vertbuffer), ADT.voidDataPointer(vertbuffer), GL_STATIC_DRAW)
    def __del__(self):
        if glDeleteBuffers:
            glDeleteBuffers(1, [self.buffer])
    def draw(self):
        glEnableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
        glVertexPointer(3, GL_FLOAT, 0, None)
        glDrawElementsui(GL_TRIANGLES, self.indexbuffer)
        glDisableClientState(GL_VERTEX_ARRAY)

def drawtext(pos, text):
    text = texture.Text(str(text), 60)
    size = (text.horizsize(0.2), 0.2)
    orig = (pos[0] - size[0]/2.0, pos[1] - size[1]/2.0)
    text()
    glBegin(GL_QUADS)
    glTexCoord(0.0, 0.0)
    glVertex(orig[0], orig[1])
    glTexCoord(text.bounds[0], 0.0)
    glVertex(orig[0] + size[0], orig[1])
    glTexCoord(text.bounds[0], text.bounds[1])
    glVertex(orig[0] + size[0], orig[1] + size[1])
    glTexCoord(0.0, text.bounds[1])
    glVertex(orig[0], orig[1] + size[1])
    glEnd()

class World:
    def __init__(self, previous = None):
        pass
    def keydown(self, key):
        pass
    def keyup(self, key):
        pass
    def click(self, pos):
        pass
    def draw(self):
        pass
    def step(self, dt):
        pass

class Opening(World):
    def __init__(self, previous = None):
        self.splash = media.loadtexture('splash.png')
    def keydown(self, key):
        if key == pygame.K_RETURN:
            transitionto(Game)
    def draw(self):
        drawsquare((0,0), (4,3), self.splash)

def make_grid(size):
    return [[{'walkable':False, 'building':None, 'item':None} for y in xrange(size[1])] for x in xrange(size[0])]

def game2world(pos, size):
    return ((pos[0] / size[0]) * worldsize[0], (pos[1] / size[1]) * worldsize[1])

class Game(World):
    def __init__(self, previous = None):
        self.size = (12,9)
        self.gridsize = (1.0 / self.size[0] * worldsize[0], 1.0 / self.size[1] * worldsize[1])
        self.grid = make_grid(self.size)
        self.buildings = []
        self.addbuilding(Hangar((0,0)))
        for x in xrange(3, 11):
            self.addbuilding(Conveyor((x,1), 'left'))
        self.addbuilding(Conveyor((10,2), 'up'))
        self.addbuilding(Conveyor((10,3), 'up'))
        self.addbuilding(Conveyor((9, 3), 'right'))
        self.addbuilding(Conveyor((9, 2), 'down'))
        self.additem((9, 2), ItemA())
    def keydown(self, key):
        pass
    def keyup(self,key):
        pass
    def addbuilding(self, building):
        self.buildings.append(building)
        for x in xrange(building.size[0]):
            for y in xrange(building.size[1]):
                self.grid[building.pos[0] + x][building.pos[1] + y]['building'] = building
    def additem(self, pos, item):
        self.grid[pos[0]][pos[1]]['item'] = item
    def draw(self):
        glColor(1.0, 1.0, 1.0, 1.0)
        for x in xrange(self.size[0]):
            for y in xrange(self.size[1]):
                drawsquare(game2world((float(x),float(y)), self.size), (self.gridsize[0] * 0.98, self.gridsize[1] * 0.98))
        for building in self.buildings:
            pos, size, color, texture = building.draw()
            pos = pos[0] + 0.1, pos[1] + 0.1
            size = size[0] - 0.2, size[1] - 0.2
            glColor(*color)
            drawsquare(game2world(pos, self.size), 
                       (size[0] * self.gridsize[0], size[1] * self.gridsize[1]), texture, 1.0)
        for x in xrange(self.size[0]):
            for y in xrange(self.size[1]):
                if self.grid[x][y]['item']:
                    glColor(*self.grid[x][y]['item'].draw())
                    drawsquare(game2world((x + 0.25, y + 0.25), self.size), (self.gridsize[0] * 0.5, self.gridsize[1] * 0.5), None, 2.0)
    def step(self, dt):
        for x in xrange(self.size[0]):
            for y in xrange(self.size[1]):
                building = self.grid[x][y]['building']
                if building and building.type == 'Conveyor' and self.grid[x][y]['item'] != None:
                    building.timer += dt
                    if building.timer > 1.0:
                        adj = adjacent((x,y), building.dir)
                        print building.dir
                        if self.grid[adj[0]][adj[1]]['item'] == None:
                            self.grid[adj[0]][adj[1]]['item'] = self.grid[x][y]['item']
                            self.grid[x][y]['item'] = None
                            building.timer = 0.0
def adjacent((x, y), dir):
    if dir == 'up':
        return (x, y-1)
    if dir == 'down':
        return (x, y+1)
    if dir == 'left':
        return (x-1, y)
    if dir == 'right':
        return (x+1, y)
    return (x, y)

class ItemA:
    def __init__(self):
        pass
    def draw(self):
        return (0.1, 0.1, 0.8, 1.0)

class Hangar:
    def __init__(self, pos):
        self.pos = pos
        self.size = (3, 3)
        self.type = 'Hangar'
    def draw(self):
        return self.pos, self.size, (0.6, 0.3, 0.0, 1.0), None

class Conveyor:
    def __init__(self, pos, dir):
        self.dir = dir
        self.pos = pos
        self.size = (1,1)
        if dir == 'left':
            self.texture = media.loadtexture('leftconvey.png')
        if dir == 'right':
            self.texture = media.loadtexture('rightconvey.png')
        if dir == 'up':
            self.texture = media.loadtexture('upconvey.png')
        if dir == 'down':
            self.texture = media.loadtexture('downconvey.png')
        self.timer = 0.0
        self.type = 'Conveyor'
    def draw(self):
        return self.pos, self.size, (1.0, 1.0, 1.0, 1.0), self.texture
