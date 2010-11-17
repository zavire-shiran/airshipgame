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

def drawtext(pos, text, level = 0.0):
    text = texture.Text(str(text))
    size = (text.horizsize(0.1), 0.1)
    orig = (pos[0] - size[0]/2.0, pos[1] - size[1]/2.0)
    text()
    glBegin(GL_QUADS)
    glTexCoord(0.0, 0.0)
    glVertex(orig[0], orig[1], level)
    glTexCoord(text.bounds[0], 0.0)
    glVertex(orig[0] + size[0], orig[1], level)
    glTexCoord(text.bounds[0], text.bounds[1])
    glVertex(orig[0] + size[0], orig[1] + size[1], level)
    glTexCoord(0.0, text.bounds[1])
    glVertex(orig[0], orig[1] + size[1], level)
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

def world2game(pos, size):
    return (int(pos[0] * size[0] / worldsize[0]), int(pos[1] * size[1] / worldsize[1]))

class Game(World):
    def __init__(self, previous = None):
        self.size = (24,18)
        self.gridsize = (1.0 / self.size[0] * worldsize[0], 1.0 / self.size[1] * worldsize[1])
        self.grid = make_grid(self.size)
        self.buildings = []
        self.money = 100
        self.addbuilding(Hangar((11,8)))
        self.dir = 'left'
        self.currentbuild = None
    def keydown(self, key):
        if key == pygame.K_w:
            self.dir = 'up'
        if key == pygame.K_s:
            self.dir = 'down'
        if key == pygame.K_a:
            self.dir = 'left'
        if key == pygame.K_d:
            self.dir = 'right'
        if key == pygame.K_x:
            self.currentbuild = None
        if key == pygame.K_c:
            self.currentbuild = Conveyor
        if key == pygame.K_e:
            self.currentbuild = Extractor
        if key == pygame.K_f:
            self.currentbuild = Factory
    def keyup(self,key):
        pass
    def click(self, pos):
        gpos = world2game(pos, self.size)
        x, y = gpos
        if self.currentbuild:
            if self.grid[x][y]['building'] == None:
                self.addbuilding(self.currentbuild(gpos, self.dir))
        else:
            if self.grid[x][y]['building'] != None and self.grid[x][y]['building'].type != 'Hangar':
                self.removebuilding(self.grid[x][y]['building'])
    def addbuilding(self, building):
        self.buildings.append(building)
        for x in xrange(building.size[0]):
            for y in xrange(building.size[1]):
                self.grid[building.pos[0] + x][building.pos[1] + y]['building'] = building
    def removebuilding(self, building):
        self.buildings.remove(building)
        for x in xrange(building.size[0]):
            for y in xrange(building.size[1]):
                self.grid[building.pos[0] + x][building.pos[1] + y]['building'] = None
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
        glColor(0.1, 0.8, 0.1)
        drawtext(game2world((12.5,9.5), self.size), '$'+str(self.money), 2.0)
    def step(self, dt):
        for x in xrange(self.size[0]):
            for y in xrange(self.size[1]):
                building = self.grid[x][y]['building']
                if building and building.type == 'Conveyor' and self.grid[x][y]['item'] != None:
                    building.timer += dt
                    if building.timer > building.time_limit:
                        adj = adjacent((x,y), building.dir)
                        if self.grid[adj[0]][adj[1]]['item'] == None:
                            self.grid[adj[0]][adj[1]]['item'] = self.grid[x][y]['item']
                            self.grid[x][y]['item'] = None
                            building.timer = 0.0
                if building and building.type == 'Factory' and self.grid[x][y]['item'] != None:
                    if building.materials < building.materialsneeded:
                        building.materials += 1
                        self.grid[x][y]['item'] = None
                    if not building.running and building.materials >= building.materialsneeded:
                        building.startproduction()
                if building and building.type == 'Hangar' and self.grid[x][y]['item'] != None:
                    self.money += self.grid[x][y]['item'].value
                    self.grid[x][y]['item'] = None
                if building and building.type == 'Extractor':
                    building.timer -= dt
                    adj = adjacent((x,y), building.dir)
                    if building.timer <= 0.0 and self.grid[adj[0]][adj[1]]['item'] == None:
                        self.additem(adj, ItemA())
                        building.reset_timer()
        for building in self.buildings:
            if building.type == 'Factory':
                if building.running:
                    building.prodtime -= dt
                    if building.prodtime <= 0.0 and self.grid[building.output[0]][building.output[1]]['item'] == None:
                        building.running = False
                        self.additem(building.output, ItemB())


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
        self.value = 1
    def draw(self):
        return (0.1, 0.1, 0.8, 1.0)

class ItemB:
    def __init__(self):
        self.value = 5
    def draw(self):
        return (0.1, 0.8, 0.1, 1.0)

class Extractor:
    def __init__(self, pos, dir):
        self.pos = pos
        self.size = (1, 1)
        self.type = 'Extractor'
        self.dir = dir
        if dir == 'left':
            self.texture = media.loadtexture('leftextractor.png')
        if dir == 'right':
            self.texture = media.loadtexture('rightextractor.png')
        if dir == 'up':
            self.texture = media.loadtexture('upextractor.png')
        if dir == 'down':
            self.texture = media.loadtexture('downextractor.png')
        self.reset_timer()
    def reset_timer(self):
        self.timer = random.random() * 10 + 10
    def draw(self):
        return self.pos, self.size, (0.3, 0.3, 0.3, 1.0), self.texture

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
        self.time_limit = 1.0
        self.type = 'Conveyor'
    def draw(self):
        return self.pos, self.size, (1.0, 1.0, 1.0, 1.0), self.texture

class Factory:
    def __init__(self, pos, dir):
        self.dir = dir
        self.pos = pos
        self.size = (3,3)
        if dir == 'left':
            self.texture = media.loadtexture('leftextractor.png')
            self.output = (pos[0]-1, pos[1]+1)
        if dir == 'right':
            self.texture = media.loadtexture('rightextractor.png')
            self.output = (pos[0]+3, pos[1]+1)
        if dir == 'up':
            self.texture = media.loadtexture('upextractor.png')
            self.output = (pos[0]+1, pos[1]-1)
        if dir == 'down':
            self.texture = media.loadtexture('downextractor.png')
            self.output = (pos[0]+1, pos[1]+3)
        self.type = 'Factory'
        self.materials = 0
        self.materialsneeded = 2
        self.running = False
        self.prodtime = 0.0
        self.runtime = 1.0
    def startproduction(self):
        self.materials -= self.materialsneeded
        self.running = True
        self.prodtime = self.runtime
    def draw(self):
        return self.pos, self.size, (0.5, 0.5, 1.0, 1.0), self.texture
