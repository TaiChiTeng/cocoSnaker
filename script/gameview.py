# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# stdlib


#pyglet
from pyglet.gl import *

# cocos2d related
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene
from cocos.director import director
from cocos.actions import *

# tetrico related
from gamectrl import *
from gamemodel import *
import levels
import gameover
from constants import *
import soundex
from HUD import *
from colors import *


__all__ = ['get_newgame']

class GameView( Layer ):

    def __init__(self, model, hud ):
        super(GameView,self).__init__()

        width, height = director.get_window_size()

        self.position = ( width/2 - MAP_WIDTH * SQUARE_SIZE / 2, 0 )

        # background layer to delimit the pieces visually
        cl = ColorLayer( 112,66,20,50, width = MAP_WIDTH * SQUARE_SIZE, height=MAP_HEIGHT * SQUARE_SIZE )
        self.add( cl, z=-1)

        self.model = model
        self.hud = hud

        self.model.push_handlers( self.on_game_over, \
                                    self.on_move_snake, \
                                    self.on_new_level, \
                                    self.on_food_eaten, \
                                    )

        self.hud.show_message( 'GET READY', self.model.start )

    def on_enter(self):
        super(GameView,self).on_enter()

        soundex.set_music('tetris.mp3')
        soundex.play_music()

    def on_exit(self):
        super(GameView,self).on_exit()
        soundex.stop_music()

    def on_move_snake(self ):
        soundex.play('move.mp3')
        return True

    def on_level_complete( self ):
        soundex.play('level_complete.mp3')
        self.hud.show_message('Level complete', self.model.set_next_level)
        return True

    def on_new_level( self ):
        return True

    def on_game_over( self ):
        self.parent.add( gameover.GameOver(win=False), z=10 )
        return True

    def on_food_eaten(self):
        return True

    def draw( self ):
        '''draw the map and the block'''

        glPushMatrix()
        self.transform()

        for i in xrange( MAP_HEIGHT ):
            for j in xrange( MAP_WIDTH ):
                color = self.model.map.get( (i,j) )
                if color:
                    Colors.images[color].blit( i * SQUARE_SIZE, j* SQUARE_SIZE)

        if self.model.snaker:
            for i in xrange( len(self.model.snaker) ):
                self.model.snaker[i].draw()

        if self.model.food:
            self.model.food.draw()

        if self.model.wall:
            for i in xrange( len(self.model.wall) ):
                self.model.wall[i].draw()

        glPopMatrix()

def get_newgame():
    '''returns the game scene'''
    scene = Scene()

    # model
    model = GameModel()

    # controller
    ctrl = GameCtrl( model )

    # view
    hud = HUD()
    view = GameView( model, hud )

    # set controller in model
    model.set_controller( ctrl )

    # add controller
    scene.add( ctrl, z=1, name="controller" )

    # add view
    scene.add( hud, z=3, name="hud" )
    scene.add( BackgroundLayer(), z=0, name="background" )
    scene.add( view, z=2, name="view" )

    return scene
