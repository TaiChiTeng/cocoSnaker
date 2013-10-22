# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# stdlib
import copy
import random

# pyglet related
import pyglet
from pyglet.window import key

# cocos2d related
from cocos.layer import Layer
from cocos.scene import Scene
from cocos.euclid import Point2

# tetrico related
from constants import *
from status import status

__all__ = ['GameCtrl']

#
# Controller ( MVC )
#

class GameCtrl( Layer ):

    is_event_handler = True #: enable pyglet's events

    def __init__(self, model):
        super(GameCtrl,self).__init__()

        self.used_key = False
        self.paused = True

        self.model = model
        self.elapsed = 0

    def on_key_press(self, k, m ):
        if self.paused:
            return False

        if self.used_key:
            return False

        if k in (key.LEFT, key.RIGHT, key.DOWN, key.UP):
            if k == key.LEFT:
                self.model.TurnTo(DIR_LEFT)
                #self.model.snake_left()
            elif k == key.RIGHT:
                self.model.TurnTo(DIR_RIGHT)
                #self.model.snake_right()
            elif k == key.DOWN:
                self.model.TurnTo(DIR_DOWN)
                #self.model.snake_down()
            elif k == key.UP:
                self.model.TurnTo(DIR_UP)
                #self.model.snake_up()
            self.used_key = True
            return True
        return False

    def pause_controller( self ):
        '''removes the schedule timer and doesn't handler the keys'''
        self.paused = True
        self.unschedule( self.step )

    def resume_controller( self ):
        '''schedules  the timer and handles the keys'''
        self.paused = False
        self.schedule( self.step )

    def step( self, dt ):
        '''updates the engine'''
        self.elapsed += dt
        if self.elapsed > status.level.speed:
            self.elapsed = 0
            if self.used_key == False:
                self.model.snake_move()
        #print "speed:",status.level.speed
        self.model.food_to_wall( dt )

    def draw( self ):
        '''draw the map and the block'''
        self.used_key = False
