# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# stdlib
import copy
import random
import weakref

# pyglet related
import pyglet

# cocos2d related
from cocos.euclid import Point2

# tetrico related
from constants import *
from status import status
from colors import *
import levels

__all__ = ['GameModel']

#
# Model (of the MVC pattern)
#

class GameModel( pyglet.event.EventDispatcher ):

    def __init__(self):
        super(GameModel,self).__init__()
        self.food_range = [ x for x in range(MAP_WIDTH*MAP_HEIGHT)]

        self.wall = []
        self.init()
        self.init_food()
        self.overlapcount = 0
        self.detatime = 0
        status.reset()

        #status.level = levels.level[0]

    def start( self ):
        self.set_next_level()

    def del_random(self,x,y):
        txy = y * MAP_WIDTH + x
        if txy in self.food_range:
            self.food_range.remove(txy)

    def add_random(self,x,y):
        txy = y * MAP_WIDTH + x
        if txy in self.food_range:
            return
        self.food_range.append(txy)

    def set_controller(self, ctrl):
        self.ctrl = weakref.ref(ctrl)

    def init_map(self):
        '''creates a map'''
        self.map= {}
        for i in xrange( MAP_HEIGHT ):
            for j in xrange( MAP_WIDTH ):
                self.map[ (i,j) ] = 0

    def init_food(self):
        tfood = Block_Food()
        txy = random.choice( self.food_range )
        tx = txy % MAP_WIDTH
        ty = txy / MAP_WIDTH
        tfood.set_pos(tx,ty)
        self.food = tfood

    def food_to_wall(self,dt):
        self.detatime += dt
        if int(self.detatime/1) != 0:
            print "time less:",5-int(self.detatime/1)
        if self.detatime >= 5:    
            self.detatime = 0
            print "food->wall"
            tempwall = Block_TempWall()
            tempwall.pos = self.food.pos
            self.wall.append(tempwall)
            self.del_random( tempwall.pos.x,tempwall.pos.y )
            self.init_food()
        if len(self.wall) >= 3:
            self.add_random( self.wall[0].pos.x,self.wall[0].pos.y )
            del self.wall[0]

    def init_snake(self):
        self.dir = DIR_RIGHT
        self.snaker = []
        snakerhead = Block_Snake_Head()
        self.snaker.append(snakerhead)

    def init(self):
        status.lines = 0
        self.init_map()
        #self.init_food()
        self.init_snake()

    def set_next_level( self ):
        self.ctrl().resume_controller()

        if status.level_idx is None:
            status.level_idx = 0
        else:
            status.level_idx += 1


        l = levels.levels[ status.level_idx ]

        self.init()
        status.level = l()

        self.dispatch_event("on_new_level")

    def TurnTo(self,dir):
        #if dir != -self.dir and dir != self.dir:
        # without "dir != self.dir" could hurry up for food!
        if dir != -self.dir:
            self.dir = dir
            self.snake_move()
        #print "dir=",self.dir

    def add_body(self,x,y):
        tempbody = Block_Snake_Body()
        tempbody.set_pos(x,y)
        templist = [ tempbody ]
        for i in xrange(self.mLen):
            templist.append( self.snaker[i] )
        self.snaker = templist

    def add_head(self,x,y):
        tempbody = Block_Snake_Body()
        tempbody.set_pos( x,y )
        
        temphead = Block_Snake_Head()
        temphead.set_pos(self.snaker[-1].pos.x,self.snaker[-1].pos.y)
        
        self.snaker[-1] = tempbody
        self.snaker.append( temphead )
        

    def del_tail(self):
        del self.snaker[0]

    def snaker_renew(self,x,y):
        self.add_head(x,y)
        self.del_tail()

    def snake_move(self):
        x,y = self.snaker[-1].pos.x,self.snaker[-1].pos.y
        if self.dir == DIR_UP:
            self.snake_up()
        elif self.dir == DIR_DOWN:
            self.snake_down()
        elif self.dir == DIR_LEFT:
            self.snake_left()
        else:
            self.snake_right()
        self.snaker_renew(x,y)
        if self.on_collision():
            self.ctrl().pause_controller()
            self.dispatch_event("on_game_over")
        else:
            self.dispatch_event("on_move_snake")


    def snake_up( self ):
        self.snaker[-1].pos.y += 1

    def snake_down( self ):
        self.snaker[-1].pos.y -= 1

    def snake_right( self ):
        self.snaker[-1].pos.x += 1

    def snake_left( self ):
        self.snaker[-1].pos.x -= 1

    def out_of_map(self):
        tx,ty = self.snaker[-1].pos.x,self.snaker[-1].pos.y
        if tx<0 or tx>=MAP_WIDTH or ty<0 or ty>=MAP_HEIGHT:
            return True
        return False

    def eat_self(self):
        x = self.snaker[-1].pos.x
        y = self.snaker[-1].pos.y
        for tbody in self.snaker[:-1]:
            if x == tbody.pos.x:
                if y == tbody.pos.y:
                    return True

    def snake_grow_up(self):
        #new_snake_head<---food.pos
        #old_snake_head--->snake's body
        new_head = Block_Snake_Head()
        new_head.set_pos( self.food.pos.x, self.food.pos.y )
        new_body = Block_Snake_Body()
        new_body.set_pos( self.snaker[-1].pos.x, self.snaker[-1].pos.y )
        self.snaker.append( new_body )
        self.snaker[-1] = new_head

    def knock_wall(self):
        for w in self.wall:
            if w.pos == self.snaker[-1].pos:
                return True
        return False

    def food_on_collision(self):
        tx,ty = self.snaker[-1].pos.x,self.snaker[-1].pos.y
        fx,fy = self.food.pos.x,self.food.pos.y
        if tx == fx and ty == fy:
            status.score += 10
            self.detatime = 0
            self.snake_grow_up()
            self.init_food()
            self.dispatch_event("on_food_eaten")

    def on_collision(self):
        if self.out_of_map():
            return True
        if self.eat_self():
            return True
        if self.knock_wall():
            return True
        self.food_on_collision()
        return False

class Block(object):
    """docstring for Block"""
    def __init__(self):
        super(Block, self).__init__()
        self.pos = None

    def set_pos(self,x,y):
        self.pos = Point2( x,y )

    def draw( self ):
        c = self.getColor()
        if c:
            Colors.images[c].blit( self.pos.x * SQUARE_SIZE, self.pos.y * SQUARE_SIZE )

    def getColor( self ):
        return self.color

class Block_Snake_Head( Block ):
    color = Colors.RED

    def __init__(self):
        super(Block_Snake_Head,self).__init__()
        self.set_pos( MAP_HEIGHT/3, MAP_WIDTH/3 )

class Block_Snake_Body( Block ):
    color = Colors.BLUE

    def __init__(self):
        super(Block_Snake_Body,self).__init__()


class Block_Food( Block ):
    color = Colors.BLUE

    def __init__(self):
        super(Block_Food,self).__init__()
        #rx = [ x for x in range(MAP_WIDTH)]
        #ry = [ y for y in range(MAP_HEIGHT)]
        #x = random.choice( rx )
        #y = random.choice( ry )
        #self.set_pos( x, y )

class Block_TempWall( Block ):
    color = Colors.TWIRL

    def __init__(self):
        super(Block_TempWall,self).__init__()



GameModel.register_event_type('on_game_over')
GameModel.register_event_type('on_move_snake')
GameModel.register_event_type('on_new_level')
GameModel.register_event_type('on_food_eaten')