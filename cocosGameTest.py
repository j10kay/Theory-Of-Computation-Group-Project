from __future__ import division, print_function, unicode_literals
import six

import sys
import os
import time
import random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pyglet
from pyglet.gl import *

from cocos.cocosnode import *
from cocos.director import *
from cocos.menu import *
from cocos.scene import *
from cocos.layer import *
from cocos.actions import *
from cocos.sprite import Sprite

import random

rr = random.randrange


class Fire:

    def __init__(self, x, y, vy, frame, size):
        self.x, self.y, self.vy, self.frame, self.size = x, y, vy, frame, size


class FireManager(Layer):

    def __init__(self, view_width, num):
        super(FireManager, self).__init__()

        self.view_width = view_width
        self.goodies = []
        self.batch = pyglet.graphics.Batch()
        self.fimg = pyglet.resource.image('blackscreen.jpg')
        self.group = pyglet.sprite.SpriteGroup(self.fimg,
                                               blend_src=GL_SRC_ALPHA, blend_dest=GL_ONE)
        self.vertex_list = self.batch.add(4 * num, GL_QUADS, self.group,
                                          'v2i', 'c4B', ('t3f', self.fimg.tex_coords * num))
        for n in range(0, num):
            f = Fire(0, 0, 0, 0, 0)
            self.goodies.append(f)
            self.vertex_list.vertices[n * 8:(n + 1) * 8] = [0, 0, 0, 0, 0, 0, 0, 0]
            self.vertex_list.colors[n * 16:(n + 1) * 16] = [0, 0, 0, 0, ] * 4

        self.schedule(self.step)

    def step(self, dt):
        w, h = self.fimg.width, self.fimg.height
        fires = self.goodies
        verts, clrs = self.vertex_list.vertices, self.vertex_list.colors
        for n, f in enumerate(fires):
            if not f.frame:
                f.x = rr(0, self.view_width)
                f.y = rr(-120, -80)
                f.vy = rr(40, 70) / 100.0
                f.frame = rr(50, 250)
                f.size = 8 + pow(rr(0.0, 100) / 100.0, 2.0) * 32
                f.scale = f.size / 32.0

            x = f.x = f.x + rr(-50, 50) / 100.0
            y = f.y = f.y + f.vy * 4
            c = 3 * f.frame / 255.0
            r, g, b = (min(255, int(c * 0xc2)), min(255, int(c * 0x41)), min(255, int(c * 0x21)))
            f.frame -= 1
            ww, hh = w * f.scale, h * f.scale
            x -= ww / 2
            if six.PY2:
                vs = map(int, [x, y, x + ww, y, x + ww, y + hh, x, y + hh])
            else:
                vs = list(map(int, [x, y, x + ww, y, x + ww, y + hh, x, y + hh]))
            verts[n * 8:(n + 1) * 8] = vs
            clrs[n * 16:(n + 1) * 16] = [r, g, b, 255] * 4

    def draw(self):
        glPushMatrix()
        self.transform()

        self.batch.draw()

        glPopMatrix()


class SpriteLayer(Layer):

    def __init__(self):
        super(SpriteLayer, self).__init__()

        sprite2 = Sprite('snake.jpg')
        sprite3 = Sprite('snake.jpg')

        sprite2.position = (620, 100)
        sprite3.position = (20, 100)

        self.add(sprite2)
        self.add(sprite3)

        ju_right = JumpBy((600, 0), height=100, jumps=4, duration=5)
        ju_left = JumpBy((-600, 0), height=100, jumps=4, duration=5)
        rot1 = Rotate(180 * 4, duration=5)

        sc = ScaleBy(9, 5)
        rot = Rotate(180, 5)

        sprite2.do(Repeat(ju_left + Reverse(ju_left)))
        sprite2.do(Repeat(Reverse(rot1) + rot1))
        sprite3.do(Repeat(ju_right + Reverse(ju_right)))
        sprite3.do(Repeat(rot1 + Reverse(rot1)))

class Problem(Layer):
	def __init__(self):
		super(Problem, self).__init__()
		
		self.dfa = {'1': [('1010', True), ('010', True), ('10000', False)],
					'2': [('b', True), ('a', False), ('aa', False)],
					'3': [('1', False), ('10', False), ('101', True)]
					}
		
		self.current_dfa = random.randint(1, len(self.dfa))
		self.current_problem = self.dfa[str(self.current_dfa)][random.randint(0,len(self.dfa[str(self.current_dfa)]) - 1)]
		
		self.dfa_sprite = Sprite(str(self.current_dfa) + '.jpg')
		self.input_str = Sprite(str(self.current_dfa) + '_' + str(self.current_problem[0]) + '.jpg')
		self.accepted = self.current_problem[1]
		# resize and scale sprites accordingly (also position)
		
	def new_problem(self):
		self.current_dfa = random.randint(1, len(self.dfa))
		self.current_problem = self.dfa[str(self.current_dfa)][random.randint(0,len(self.dfa[str(self.current_dfa)]) - 1)]
		
		self.dfa_sprite = Sprite(str(self.current_dfa) + '.jpg')
		self.input_str = Sprite(str(self.current_dfa) + '_' + str(self.current_problem[0]) + '.jpg')
		self.accepted = self.current_problem[1]

class Sound():
	def __init__(self):
		self.player = pyglet.media.Player()
		bgm = pyglet.media.load('bgm.mp3')
		bgmlooper = pyglet.media.SourceGroup(bgm.audio_format, None)
		bgmlooper.loop = True
		bgmlooper.queue(bgm)
		self.player.queue(bgmlooper)
		
	def BGM_play(self, play=False):
		if play:
			self.player.play()
		else:
			self.player.pause()
	
	def gameover(self):
		self.player.pause()
		pyglet.media.load('gameover.mp3').play()
	
	def consume(self):
		pyglet.media.load('consume.mp3').play()

class GameLayer(Layer):
	# this is for taking in keyboard input on press
	is_event_handler = True

	def __init__(self):
		# add background layer
		super(GameLayer, self).__init__()
		size = director.get_window_size()
		backgroundSprite = Sprite('grasspatch.jpg')
		backgroundSprite.position = (size[0] / 2, size[1] / 2)
		sc = ScaleBy(2, 0)
		backgroundSprite.do(sc)
		self.add(backgroundSprite)
		
		# add snake sprite
		self.snake = Snake()
		self.add(self.snake)
	
	def on_key_press(self, key, modifiers):
		self.snake.key_pressed(key)
		
class Snake(CocosNode):
	def __init__(self):
		super(Snake, self).__init__()
		self.size = (640, 480)
		# to keep track of whether snake is dead or not
		# self.game_over = False
		# initialize here for difficulty
		self.head = Sprite('snake.jpg')
		self.head.scale = 0.05
		self.head.new_dir = None
		self.head.old_dir = None
		# take into account the place to show the DFA's
		self.head.position = ((self.size[0] + 160) / 2, self.size[1] / 2)
		self.add(self.head)
		self.body = []
		self.body.append(self.head)
		
		# show problem
		self.problem = Problem()
		
		# do food
		self.yes_apple = Sprite('yes_apple.jpg')
		self.no_apple = Sprite('no_apple.jpg')
		
		self.yes_apple.scale = 0.05
		self.no_apple.scale = 0.05
		
		self.add(self.yes_apple)
		self.add(self.no_apple)
		
		self.generate_apples()
		
		# do music
		
		#self.music = Sound()
		#self.music.BGM_play(True)
		
		# do score
		self.score = 0
		# show score board at the bottom left
		
		self.schedule_interval(self.update, 0.1)
		
	def generate_apples(self):
		# this is for making sure the apples do not spawn inside the snake
		in_snake = True
		app_coll = True
		while in_snake:
			while app_coll:
				yes_pos = (160 + random.randint(1, 19) * 24, random.randint(1, 19) * 24)
				no_pos = (160 + random.randint(1, 19) * 24, random.randint(1, 19) * 24)
				if yes_pos != no_pos:
					app_coll = False
			if yes_pos not in [x.position for x in self.body] and no_pos not in [x.position for x in self.body]:
				in_snake = False
			app_coll = True
		self.yes_apple.position = yes_pos
		self.no_apple.position = no_pos
	
	
	def eat_apple(self):
		# create a new body and set the position to the previous last body partition
		new_snake_body = Sprite('body.jpg')
		new_snake_body.position = self.body[-1].position
		new_snake_body.scale = 0.05
		# now, we can update the positions accordingly
		self.add(new_snake_body)
		self.body.append(new_snake_body)
		
		self.problem.new_problem()
		
		self.generate_apples()
		self.score += 10
		
		#play food music
		# increase difficulty here
	
	def update(self, dt):
		new_pos = self.head.position
		if self.head.new_dir == "UP":
			if self.head.position[1] + 24 >= 480:
				self.game_over()
			new_pos = self.head.position[0], self.head.position[1] + 24
		elif self.head.new_dir == "DOWN":
			if self.head.position[1] - 24 <= 0:
				self.game_over()
			new_pos = self.head.position[0], self.head.position[1] - 24
		elif self.head.new_dir == "RIGHT":
			if self.head.position[0] + 24 >= 640:
				self.game_over()
			new_pos = self.head.position[0] + 24, self.head.position[1]
		elif self.head.new_dir == "LEFT":
			if self.head.position[0] - 24 <= 160:
				self.game_over()
			new_pos = self.head.position[0] - 24, self.head.position[1]
		

		for i in range(1, len(self.body) - 1):
			if new_pos == self.body[i].position:
				print('uh oh')
				self.game_over()

		if new_pos == self.no_apple.position:
			if self.problem.accepted:
				self.game_over()
			else:
				self.eat_apple()
		elif new_pos == self.yes_apple.position:
			if self.problem.accepted:
				self.eat_apple()
			else:
				self.game_over()
		# instead of recursively updating all body positions
		# just replace previous head position with tail
			
		self.body[-1].position = self.head.position
		self.head.position = new_pos
		
		# and update the vector of body parts accordingly again
		self.body = [self.head] + self.body[-1:] + self.body[1:-1]
	
	def key_pressed(self, key):
		if key == 65361 and self.head.old_dir != "RIGHT":
			self.head.new_dir = "LEFT"
		elif key == 65362 and self.head.old_dir != "DOWN":
			self.head.new_dir = "UP"
		elif key == 65363 and self.head.old_dir != "LEFT":
			self.head.new_dir = "RIGHT"
		elif key == 65364 and self.head.old_dir != "UP":
			self.head.new_dir = "DOWN"
		self.head.old_dir = self.head.new_dir
		
	def game_over(self):
		s = start()
		run(s)
		
def createScene():
	gameLayer = GameLayer()
	scene = Scene(gameLayer)
	director.replace(scene)
	
def gameLoop():
	gameOver = False
	createScene()
	

class MainMenu(Menu):

    def __init__(self):

        # call superclass with the title
        super(MainMenu, self).__init__("SNAKE DFA")

        pyglet.font.add_directory('.')

        # you can override the font that will be used for the title and the items
        self.font_title['font_name'] = 'Times New Roman'
        self.font_title['font_size'] = 72

        self.font_item['font_name'] = 'Times New Roman'
        self.font_item_selected['font_name'] = 'Times New Roman'

        # you can also override the font size and the colors. see menu.py for
        # more info

        # example: menus can be vertical aligned and horizontal aligned
        self.menu_valign = CENTER
        self.menu_halign = CENTER

        items = []

        items.append(MenuItem('New Game', self.on_new_game))
        items.append(MenuItem('Options', self.on_options))
        items.append(MenuItem('Scores', self.on_scores))
        items.append(MenuItem('Quit', self.on_quit))

        self.create_menu(items, zoom_in(), zoom_out())

    # Callbacks
    def on_new_game(self):
        gameLoop()
		#call game function

    def on_scores(self):
        self.parent.switch_to(2)

    def on_options(self):
        self.parent.switch_to(1)

    def on_quit(self):
        director.pop()
		
class OptionMenu(Menu):

    def __init__(self):
        super(OptionMenu, self).__init__("SNAKE DFA")

        self.font_title['font_name'] = 'Times New Roman'
        self.font_title['font_size'] = 72

        self.font_item['font_name'] = 'Times New Roman'
        self.font_item_selected['font_name'] = 'Times New Roman'

        self.menu_valign = BOTTOM
        self.menu_halign = RIGHT

        items = []
        items.append(MenuItem('Fullscreen', self.on_fullscreen))
        items.append(ToggleMenuItem('Show FPS: ', self.on_show_fps, True))
        items.append(MenuItem('OK', self.on_quit))
        self.create_menu(items, shake(), shake_back())

    # Callbacks
    def on_fullscreen(self):
        director.window.set_fullscreen(not director.window.fullscreen)

    def on_quit(self):
        self.parent.switch_to(0)

    def on_show_fps(self, value):
        director.show_FPS = value


class ScoreMenu(Menu):

    def __init__(self):
        super(ScoreMenu, self).__init__("SNAKE DFA")

        self.font_title['font_name'] = 'Times New Roman'
        self.font_title['font_size'] = 72
        self.font_item['font_name'] = 'Times New Roman'
        self.font_item_selected['font_name'] = 'Times New Roman'

        self.menu_valign = BOTTOM
        self.menu_halign = LEFT

        self.create_menu([MenuItem('Go Back', self.on_quit)])

    def on_quit(self):
        self.parent.switch_to(0)

def init():
    director.init(resizable=True, width=640, height=480)

def start():
    director.set_depth_test()

    firelayer = FireManager(director.get_window_size()[0], 250)
    spritelayer = SpriteLayer()
    menulayer = MultiplexLayer(MainMenu(), OptionMenu(), ScoreMenu())

    scene = Scene(firelayer, spritelayer, menulayer)

    twirl_normal = Twirl(center=(320, 240), grid=(16, 12), duration=15, twirls=6, amplitude=6)
    twirl = AccelDeccelAmplitude(twirl_normal, rate=4.0)
    lens = Lens3D(radius=240, center=(320, 240), grid=(32, 24), duration=5)
    waves3d = AccelDeccelAmplitude(
        Waves3D(waves=18, amplitude=80, grid=(32, 24), duration=15), rate=4.0)
    flipx = FlipX3D(duration=1)
    flipy = FlipY3D(duration=1)
    flip = Flip(duration=1)
    liquid = Liquid(grid=(16, 12), duration=4)
    ripple = Ripple3D(grid=(32, 24), waves=7, duration=10, amplitude=100, radius=320)
    shakyt = ShakyTiles3D(grid=(16, 12), duration=3)
    corners = CornerSwap(duration=1)
    waves = AccelAmplitude(Waves(waves=8, amplitude=50, grid=(32, 24), duration=5), rate=2.0)
    shaky = Shaky3D(randrange=10, grid=(32, 24), duration=5)
    quadmove = QuadMoveBy(
        delta0=(320, 240), delta1=(-630, 0), delta2=(-320, -240), delta3=(630, 0), duration=2)
    fadeout = FadeOutTRTiles(grid=(16, 12), duration=2)
    cornerup = MoveCornerUp(duration=1)
    cornerdown = MoveCornerDown(duration=1)
    shatter = ShatteredTiles3D(randrange=16, grid=(16, 12), duration=4)
    shuffle = ShuffleTiles(grid=(16, 12), duration=1)
    orbit = OrbitCamera(
        radius=1, delta_radius=2, angle_x=0, delta_x=-90, angle_z=0, delta_z=180, duration=4)
    jumptiles = JumpTiles3D(jumps=2, duration=4, amplitude=80, grid=(16, 12))
    wavestiles = WavesTiles3D(waves=3, amplitude=60, duration=8, grid=(16, 12))
    turnoff = TurnOffTiles(grid=(16, 12), duration=2)

#    firelayer.do(
#    spritelayer.do(
#    menulayer.do(
    scene.do(
        Delay(3) 
    )
    
    return scene
	
def run(scene):
    director.run(scene)

if __name__ == "__main__":
    init()
    s = start()
    run(s)
