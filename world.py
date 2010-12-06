import math
import media
import pygame
import texture
import numpy
import random
import itertools
from collections import defaultdict
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

def maketile():
    return {'buildable':False, 'building':None, 'item':None}

def make_grid(size):
    return defaultdict(maketile)

def game2world(pos, size):
    return ((pos[0] / size[0]) * worldsize[0], (pos[1] / size[1]) * worldsize[1])

def world2game(pos, size):
    return (int(pos[0] * size[0] / worldsize[0]), int(pos[1] * size[1] / worldsize[1]))

class Game(World):
    def __init__(self, previous = None):
        self.size = (24,18)
        self.gridsize = (1.0 / self.size[0] * worldsize[0], 1.0 / self.size[1] * worldsize[1])
        self.buildings = []
        self.dir = 'left'
        self.currentbuild = None
        self.defaultlayout()
        self.campos = [0,0]
        self.cammove =[False, False, False, False] #up, down, left, right
    def defaultlayout(self):
        self.currenttime = 0
        self.money = 0
        self.incomehist = []
        self.expenditurehist = []
        self.grid = make_grid(self.size)
        self.removeallbuildings()
        self.addbuilding(Hangar((11,8)))
        self.recalcbuildable()
    def recalcbuildable(self):
        for x,y in self.grid.keys():
            self.grid[x, y]['buildable'] = False
        for building in self.buildings:
            if building.type == 'Hangar':
                for x in xrange(-3, 6):
                    for y in xrange(-3, 6):
                        self.grid[building.pos[0] + x, building.pos[1] + y]['buildable'] = True
            if building.type == 'Balloon':
                for x in xrange(-3, 4):
                    for y in xrange(-3, 4):
                        self.grid[building.pos[0] + x, building.pos[1] + y]['buildable'] = True
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
        if key == pygame.K_q:
            self.currentbuild = MultiExtractor
        if key == pygame.K_f:
            self.currentbuild = Factory
        if key == pygame.K_r:
            self.currentbuild = Overflow
        if key == pygame.K_b:
            self.currentbuild = Balloon
        if key == pygame.K_z:
            self.currentbuild = 'select'
        if key == pygame.K_l:
            self.dumpbuildings()
        if key == pygame.K_F9:
            self.defaultlayout()
        if key == pygame.K_UP:
            self.cammove[0] = True
        if key == pygame.K_DOWN:
            self.cammove[1] = True
        if key == pygame.K_LEFT:
            self.cammove[2] = True
        if key == pygame.K_RIGHT:
            self.cammove[3] = True
    def keyup(self,key):
        if key == pygame.K_UP:
            self.cammove[0] = False
        if key == pygame.K_DOWN:
            self.cammove[1] = False
        if key == pygame.K_LEFT:
            self.cammove[2] = False
        if key == pygame.K_RIGHT:
            self.cammove[3] = False
    def click(self, pos):
        pos = (pos[0] + self.campos[0], pos[1] + self.campos[1])
        gpos = world2game(pos, self.size)
        x, y = gpos
        if self.currentbuild == 'select':
            if self.grid[x, y]['building']:
                self.grid[x, y]['building'].select()
        elif self.currentbuild:
            if self.grid[x, y]['buildable'] and self.grid[x, y]['building'] == None:
                self.addbuilding(self.currentbuild(gpos, self.dir))
                self.recalcbuildable()
        else:
            if self.grid[x, y]['building'] != None and self.grid[x, y]['building'].type != 'Hangar':
                self.removebuilding(self.grid[x, y]['building'])
                self.recalcbuildable()
    def addbuilding(self, building):
        if not self.buildingfitp(building):
            return
        self.buildings.append(building)
        for x in xrange(building.size[0]):
            for y in xrange(building.size[1]):
                self.grid[building.pos[0] + x, building.pos[1] + y]['building'] = building
    def buildingfitp(self, building):
        for x in xrange(building.size[0]):
            for y in xrange(building.size[1]):
                if self.grid[building.pos[0] + x, building.pos[1] + y]['building'] != None:
                    return False
        return True
    def removebuilding(self, building):
        self.buildings.remove(building)
        for x in xrange(building.size[0]):
            for y in xrange(building.size[1]):
                self.grid[building.pos[0] + x, building.pos[1] + y]['building'] = None
    def removeallbuildings(self):
        for building in self.buildings[:]:
            self.removebuilding(building)
    def dumpbuildings(self):
        for building in self.buildings:
            print building.type, building.pos
    def additem(self, pos, item):
        self.grid[pos[0], pos[1]]['item'] = item
    def addincome(self, amount):
        self.money += amount
        self.incomehist.append((amount, self.currenttime))
    def addexpenditure(self, amount):
        self.money -= amount
        self.expenditurehist.append((amount, self.currenttime))
    def draw(self):
        glLoadIdentity()
        glTranslate(-self.campos[0], -self.campos[1], 0.0)
        glColor(1.0, 1.0, 1.0, 1.0)
        for x,y in self.grid.keys():
            drawsquare(game2world((float(x),float(y)), self.size), (self.gridsize[0] * 0.98, self.gridsize[1] * 0.98))
        for building in self.buildings:
            building.draw(self)
        for x,y in self.grid.keys():
            if self.grid[x, y]['item']:
                glColor(*self.grid[x, y]['item'].draw())
                drawsquare(game2world((x + 0.25, y + 0.25), self.size), (self.gridsize[0] * 0.5, self.gridsize[1] * 0.5), None, 2.0)
        glColor(0.1, 0.8, 0.1)
        drawtext(game2world((12.5,8.5), self.size), '$'+str(self.money), 2.0)
        income = 0
        expenditure = 0
        for amount, time in self.incomehist:
            income += amount
        for amount, time in self.expenditurehist:
            expenditure += amount
        drawtext(game2world((12.5,9.5), self.size), '$%.2f/sec' % (income / 30.0), 2.0)
        glColor(0.8, 0.1, 0.1)
        drawtext(game2world((12.5,10.5), self.size), '$%.2f/sec' % (expenditure / 30.0), 2.0)
    def step(self, dt):
        self.currenttime += dt
        while len(self.incomehist) > 0 and self.incomehist[0][1] < self.currenttime - 30:
            del self.incomehist[0]
        while len(self.expenditurehist) > 0 and self.expenditurehist[0][1] < self.currenttime - 30:
            del self.expenditurehist[0]
        if self.cammove[0]:
            self.campos[1] -= dt
        if self.cammove[1]:
            self.campos[1] += dt
        if self.cammove[2]:
            self.campos[0] -= dt
        if self.cammove[3]:
            self.campos[0] += dt
        li = self.grid.keys()[:]
        random.shuffle(li)
        for x, y in li:
                building = self.grid[x, y]['building']
                if building and building.type == 'Conveyor' and self.grid[x, y]['item'] != None:
                    building.timer += dt
                    if building.timer > building.time_limit:
                        adj = adjacent((x,y), building.dir)
                        if self.grid[adj[0], adj[1]]['item'] == None:
                            self.grid[x, y]['item'].resetdecay()
                            self.grid[adj[0], adj[1]]['item'] = self.grid[x, y]['item']
                            self.grid[x, y]['item'] = None
                            building.timer = 0.0
                if building and building.type == 'Overflow' and self.grid[x, y]['item'] != None:
                    building.timer += dt
                    if building.timer > building.time_limit:
                        adj = adjacent((x,y), building.dir)
                        oadj = adjacentrel((x,y), building.dir, building.overflowdir)
                        if self.grid[adj[0], adj[1]]['item'] == None:
                            self.grid[x, y]['item'].resetdecay()
                            self.grid[adj[0], adj[1]]['item'] = self.grid[x, y]['item']
                            self.grid[x, y]['item'] = None
                            building.timer = 0.0
                        elif self.grid[oadj[0], oadj[1]]['item'] == None:
                            self.grid[x, y]['item'].resetdecay()
                            self.grid[oadj[0], oadj[1]]['item'] = self.grid[x, y]['item']
                            self.grid[x, y]['item'] = None
                            building.timer = 0.0
                if building and building.type == 'Factory' and self.grid[x, y]['item'] != None:
                    if building.materials < building.materialsneeded and self.grid[x, y]['item'].__class__ not in building.lastinput:
                        building.materials += 1
                        building.lastinput.append(self.grid[x, y]['item'].__class__)
                        self.grid[x, y]['item'] = None
                    if not building.running and building.materials >= building.materialsneeded:
                        building.startproduction()
                if building and building.type == 'Hangar' and self.grid[x, y]['item'] != None:
                    self.addincome(self.grid[x, y]['item'].value)
                    self.grid[x, y]['item'] = None
                if building and (building.type == 'Extractor' or building.type == 'MultiExtractor'):
                    building.timer -= dt
                    adj = adjacent((x,y), building.dir)
                    if building.timer <= 0.0 and self.grid[adj[0], adj[1]]['item'] == None:
                        self.additem(adj, building.nextproduce())
                        building.reset_timer()
                if self.grid[x, y]['item']:
                    self.grid[x, y]['item'].step(dt)
                    if self.grid[x, y]['item'].decay <= 0.0:
                        self.grid[x, y]['item'] = None
                if not self.grid[x, y]['buildable']:
                    del self.grid[x, y]
        for building in self.buildings[:]:
            if not self.grid[building.pos]['buildable']:
                self.buildings.remove(building)
                continue
            if building.type == 'Factory':
                if building.running:
                    building.prodtime -= dt
                    if building.prodtime <= 0.0 and self.grid[building.output[0], building.output[1]]['item'] == None:
                        building.running = False
                        self.additem(building.output, building.production())
            if building.type == 'Balloon':
                building.timer += dt
                if building.timer > building.timetocost:
                    self.addexpenditure(building.cost)
                    building.resettimer()


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

def adjacentrel(pos, dir, rel):
    if dir == 'up':
        if rel == 'left':
            return adjacent(pos, 'left')
        if rel == 'right':
            return adjacent(pos, 'right')
    if dir == 'down':
        if rel == 'left':
            return adjacent(pos, 'right')
        if rel == 'right':
            return adjacent(pos, 'left')
    if dir == 'left':
        if rel == 'left':
            return adjacent(pos, 'down')
        if rel == 'right':
            return adjacent(pos, 'up')
    if dir == 'right':
        if rel == 'left':
            return adjacent(pos, 'up')
        if rel == 'right':
            return adjacent(pos, 'down')

class Item:
    def resetdecay(self):
        self.decay = min(1.0, self.decay + 0.2)

class ItemA(Item):
    def __init__(self):
        self.value = 1
        self.decay = 1.0
        self.decaytime = 10.0
    def step(self, dt):
        self.decay -= dt/self.decaytime
    def draw(self):
        return (0.1, 0.1, 0.8, self.decay + 0.1)

class ItemB(Item):
    def __init__(self):
        self.value = 1
        self.decay = 1.0
        self.decaytime = 10.0
    def step(self, dt):
        self.decay -= dt/self.decaytime
    def draw(self):
        return (0.1, 0.8, 0.1, self.decay + 0.1)

class ItemC(Item):
    def __init__(self):
        self.value = 1
        self.decay = 1.0
        self.decaytime = 10.0
    def step(self, dt):
        self.decay -= dt/self.decaytime
    def draw(self):
        return (0.8, 0.1, 0.1, self.decay + 0.1)

def randomitem():
    r = random.random()
    if r < 0.3333:
        return ItemA
    if r < 0.6666:
        return ItemB
    return ItemC

class ItemAB(Item):
    def __init__(self):
        self.value = 4
        self.decaytime = 10.0
        self.decay = 1.0
    def step(self, dt):
        self.decay -= dt/self.decaytime
    def draw(self):
        return (0.1, 0.8, 0.8, self.decay + 0.1)

class ItemAC(Item):
    def __init__(self):
        self.value = 4
        self.decaytime = 10.0
        self.decay = 1.0
    def step(self, dt):
        self.decay -= dt/self.decaytime
    def draw(self):
        return (0.8, 0.1, 0.8, self.decay + 0.1)

class ItemBC(Item):
    def __init__(self):
        self.value = 4
        self.decaytime = 10.0
        self.decay = 1.0
    def step(self, dt):
        self.decay -= dt/self.decaytime
    def draw(self):
        return (0.8, 0.8, 0.1, self.decay + 0.1)

class Extractor:
    def __init__(self, pos, dir, output = ItemA):
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
        self.nextproduce = output
        self.reset_timer()
    def reset_timer(self):
        self.timer = random.random() * 10 + 10
    def select(self):
        self.reset_timer()
        if self.nextproduce == ItemA:
            self.nextproduce = ItemB
        elif self.nextproduce == ItemB:
            self.nextproduce = ItemC
        elif self.nextproduce == ItemC:
            self.nextproduce = ItemA
    def draw(self, world):
        if self.nextproduce == ItemA:
            pos, size, color, texture = self.pos, self.size, (0.3, 0.3, 0.5, 1.0), self.texture
        if self.nextproduce == ItemB:
            pos, size, color, texture = self.pos, self.size, (0.3, 0.5, 0.3, 1.0), self.texture
        if self.nextproduce == ItemC:
            pos, size, color, texture = self.pos, self.size, (0.5, 0.3, 0.3, 1.0), self.texture
        pos = pos[0] + 0.1, pos[1] + 0.1
        size = size[0] - 0.2, size[1] - 0.2
        glColor(*color)
        drawsquare(game2world(pos, world.size), 
                   (size[0] * world.gridsize[0], size[1] * world.gridsize[1]), texture, 1.0)

class MultiExtractor:
    def __init__(self, pos, dir):
        self.pos = pos
        self.size = (1,1)
        self.type = 'MultiExtractor'
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
        self.timer = random.random() * 10 + 7
        self.nextproduce = randomitem()
    def select(self):
        pass
    def draw(self, world):
        pos, size, color, texture = self.pos, self.size, (0.3, 0.3, 0.3, 1.0), self.texture
        if self.nextproduce == ItemA:
            pos, size, color, texture = self.pos, self.size, (0.1, 0.1, 0.8, 1.0), self.texture
        if self.nextproduce == ItemB:
            pos, size, color, texture = self.pos, self.size, (0.1, 0.8, 0.1, 1.0), self.texture
        if self.nextproduce == ItemC:
            pos, size, color, texture = self.pos, self.size, (0.8, 0.1, 0.1, 1.0), self.texture
        pos = pos[0] + 0.1, pos[1] + 0.1
        size = size[0] - 0.2, size[1] - 0.2
        glColor(*color)
        drawsquare(game2world(pos, world.size), 
                   (size[0] * world.gridsize[0], size[1] * world.gridsize[1]), texture, 1.0)

class Hangar:
    def __init__(self, pos):
        self.pos = pos
        self.size = (3, 3)
        self.type = 'Hangar'
    def select(self):
        pass
    def draw(self, world):
        pos, size, color, texture = self.pos, self.size, (0.6, 0.3, 0.0, 1.0), None
        pos = pos[0] + 0.1, pos[1] + 0.1
        size = size[0] - 0.2, size[1] - 0.2
        glColor(*color)
        drawsquare(game2world(pos, world.size), 
                   (size[0] * world.gridsize[0], size[1] * world.gridsize[1]), texture, 1.0)

class Balloon:
    def __init__(self, pos, dir = None):
        self.pos = pos
        self.size = (1,1)
        self.type = 'Balloon'
        self.cost = 1.0
        self.timetocost = 10.0
        self.resettimer()
    def resettimer(self):
        self.timer = 0
    def select(self):
        pass
    def draw(self, world):
        pos, size, color, texture = self.pos, self.size, (0.6, 0.3, 0.3, 1.0), None
        pos = pos[0] + 0.1, pos[1] + 0.1
        size = size[0] - 0.2, size[1] - 0.2
        glColor(*color)
        drawsquare(game2world(pos, world.size), 
                   (size[0] * world.gridsize[0], size[1] * world.gridsize[1]), texture, 1.0)

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
        self.time_limit = 0.5
        self.type = 'Conveyor'
    def select(self):
        pass
    def draw(self, world):
        pos, size, color, texture = self.pos, self.size, (1.0, 1.0, 1.0, 1.0), self.texture
        pos = pos[0] + 0.1, pos[1] + 0.1
        size = size[0] - 0.2, size[1] - 0.2
        glColor(*color)
        drawsquare(game2world(pos, world.size), 
                   (size[0] * world.gridsize[0], size[1] * world.gridsize[1]), texture, 1.0)

class Overflow:
    def __init__(self, pos, dir):
        self.dir = dir
        self.pos = pos
        self.size = (1,1)
        if dir == 'left':
            self.texture = media.loadtexture('leftconvey.png')
            self.overflowleft = media.loadtexture('downextractor.png')
            self.overflowright = media.loadtexture('upextractor.png')
        if dir == 'right':
            self.texture = media.loadtexture('rightconvey.png')
            self.overflowleft = media.loadtexture('upextractor.png')
            self.overflowright = media.loadtexture('downextractor.png')
        if dir == 'up':
            self.texture = media.loadtexture('upconvey.png')
            self.overflowleft = media.loadtexture('leftextractor.png')
            self.overflowright = media.loadtexture('rightextractor.png')
        if dir == 'down':
            self.texture = media.loadtexture('downconvey.png')
            self.overflowleft = media.loadtexture('rightextractor.png')
            self.overflowright = media.loadtexture('leftextractor.png')
        self.timer = 0.0
        self.time_limit = 0.5
        self.type = 'Overflow'
        self.overflowdir = 'left'
    def select(self):
        if self.overflowdir == 'left':
            self.overflowdir = 'right'
        else:
            self.overflowdir = 'left'
    def draw(self, world):
        pos, size, color, texture = self.pos, self.size, (1.0, 1.0, 1.0, 1.0), self.texture
        pos = pos[0] + 0.1, pos[1] + 0.1
        size = size[0] - 0.2, size[1] - 0.2
        glColor(*color)
        drawsquare(game2world(pos, world.size), 
                   (size[0] * world.gridsize[0], size[1] * world.gridsize[1]), texture, 1.0)
        if self.overflowdir == 'left':
            pos, size, color, texture = self.pos, self.size, (1.0, 1.0, 1.0, 1.0), self.overflowleft
        if self.overflowdir == 'right':
            pos, size, color, texture = self.pos, self.size, (1.0, 1.0, 1.0, 1.0), self.overflowright
        if self.dir == 'left':
            pos = pos[0] + 0.5, pos[1] + 0.3
        elif self.dir == 'right':
            pos = pos[0] + 0.1, pos[1] + 0.3
        elif self.dir == 'up':
            pos = pos[0] + 0.3, pos[1] + 0.5
        elif self.dir == 'down':
            pos = pos[0] + 0.3, pos[1] + 0.1
        size = size[0] - 0.6, size[1] - 0.6
        glColor(*color)
        drawsquare(game2world(pos, world.size), 
                   (size[0] * world.gridsize[0], size[1] * world.gridsize[1]), texture, 1.1)

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
        self.lastinput = []
        self.materials = 0
        self.materialsneeded = 2
        self.running = False
        self.prodtime = 0.0
        self.runtime = 0.5
    def select(self):
        pass
    def chooseproduction(self):
        if ItemA in self.lastinput and ItemB in self.lastinput:
            self.production = ItemAB
        elif ItemA in self.lastinput and ItemC in self.lastinput:
            self.production = ItemAC
        elif ItemB in self.lastinput and ItemC in self.lastinput:
            self.production = ItemBC
    def startproduction(self):
        self.materials -= self.materialsneeded
        self.chooseproduction()
        self.running = True
        self.prodtime = random.random() + self.runtime
        self.lastinput = []
    def draw(self, world):
        pos, size, color, texture = self.pos, self.size, (0.5, 0.5, 1.0, 1.0), self.texture
        pos = pos[0] + 0.1, pos[1] + 0.1
        size = size[0] - 0.2, size[1] - 0.2
        glColor(*color)
        drawsquare(game2world(pos, world.size), 
                   (size[0] * world.gridsize[0], size[1] * world.gridsize[1]), texture, 1.0)
