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
        self.fimg = pyglet.resource.image('resources\\grasspatch.jpg')
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

        sprite2 = Sprite('resources\\snake_start.png')
        sprite3 = Sprite('resources\\snake_start.png')

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
		
		self.dfa = {'1': [('1010', True), ('010', True), ('10000', False),
						  ('0', False), ('01', False), ('000', True), ('1111', True),
						  ('11', True), ('10', False), ('01111', False), ('100', False),
						  ('011001', True), ('01010101', True), ('1000010', True)],
					'2': [('b', True), ('a', False), ('aa', False), ('aba', True), 
						  ('baa', False), ('bbbaa', False), ('bbbaaa', True), ('ba', True), 
						  ('aabb', True), ('bbabab', True), ('baaabb', True)],
					'3': [('1', False), ('10', False), ('101', True), ('11', False), 
					      ('0', False), ('100', False), ('1101010', False), ('101000', True), 
					      ('1010', True), ('1010101', True), ('10001', False)],
                    '4': [('abb', True), ('babbaabb', True), ('a', False), ('ab', False), 
					      ('aa', False), ('abba', False), ('aaa', False), ('ababb', True), 
					      ('abab', False), ('aabaaab', True), ('aabb', True), ('bbbababb', True), ('abbaabb', True)],
                    '5': [('ab', False), ('abaa', False), ('abba', False), ('abaaaba', False), 
					      ('aabaa', False), ('ababbb', True), ('babbbabb', True), ('abab', True), 
					      ('babbabb', True), ('abbabb', True)],
                    '6': [('01', True), ('0011', True), ('11', True), ('10', False), 
					      ('101', False), ('10100', False), ('100110', False), ('1101001', False), 
					      ('1010', False), ('01010', False), ('100101', True), ('0010001', True), ('10110011', True)],
                    '7': [('aaa', False), ('baba', True), ('abaa', False), ('bbaa', True), 
					      ('ababa', False), ('ab', False), ('bbb', False), ('bbbbbaa', True), 
					      ('aaababab', False), ('aabb', True), ('bbbabab', True), ('abbbab', True)],
                    '8': [('a', True), ('bb', True), ('ab', False), ('aab', True), 
					      ('abab', False), ('bba', True), ('abbb', False), ('bbab', False), 
					      ('aaabb', True), ('babbaba', False), ('aaabba', True), ('bbbabbbb', True), ('aababbaa', True)],
                    '9': [('1', False), ('00', False), ('01', True), ('10', True), 
					      ('0001', False), ('1000', False), ('11011', False), ('10001', True), 
					      ('101001', True), ('110100110', True), ('000101001', True)]
					}
		
		self.new_problem()
		
	def new_problem(self):
		current_dfa = random.randint(1, len(self.dfa))
		current_problem = self.dfa[str(current_dfa)][random.randint(0,len(self.dfa[str(current_dfa)]) - 1)]
		
		dfa_sprite = Sprite('resources\\' + str(current_dfa) + '.png')
		input_str = Sprite('resources\\' + str(current_dfa) + '_' + str(current_problem[0]) + '.png')
		question_str = Sprite('resources\\question_for_user.png')
		self.accepted = current_problem[1]
		# resize and scale sprites accordingly (also position)
		
		dfa_sprite.position = 160 // 2, 240 + 240 // 2
		# create sprite to ask the user a question
		# "Will the DFA accept or reject the input string?"
        #question_str.position = 160 //2, 120 // 2
		question_str.position = 160 // 2, (120 + 240) // 2
		input_str.position = 160 // 2, 120 // 2
		
		self.add(dfa_sprite)
		self.add(input_str)
		self.add(question_str)

class Sound():
	def __init__(self):
		self.player = pyglet.media.Player()
		bgm = pyglet.media.load('bgm.mp3')
		bgmlooper = pyglet.media.SourceGroup(bgm.audio_format, None)
		bgmlooper.loop = True
		bgmlooper.queue(bgm)
		self.player.queue(bgmlooper)

class GameLayer(Layer):
	# this is for taking in keyboard input on press
	is_event_handler = True

	def __init__(self):
		# add background layer
		super(GameLayer, self).__init__()
		size = director.get_window_size()
		backgroundSprite = Sprite('resources\\background.jpg')
		backgroundSprite.position = (size[0] / 2, size[1] / 2)
		sc = ScaleBy(2, 0)
		backgroundSprite.do(sc)
		self.add(backgroundSprite)
		
		# add snake sprite
		self.snake = Snake()
		self.add(self.snake)
	
	def on_key_press(self, key, modifiers):
		self.snake.key_pressed(key)
		
class Snake(Layer):
	def __init__(self):
		super(Snake, self).__init__()
		self.size = (640, 480)
		# to keep track of whether snake is dead or not
		# self.game_over = False
		# initialize here for difficulty
		self.head = Sprite('resources\\head.png')
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
		self.add(self.problem)
		
		# do food
		self.yes_apple = Sprite('resources\\resized_accept_apple.png')
		self.no_apple = Sprite('resources\\resized_reject_apple.png')
		
		self.yes_apple.scale = 0.035
		self.no_apple.scale = 0.035
		
		self.add(self.yes_apple)
		self.add(self.no_apple)
		
		self.generate_apples()
		
		# do music
		
		# do score
		self.score = 0
		# show score board at the bottom left
		
		self.schedule_interval(self.update, 0.15)
		
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
		new_snake_body = Sprite('resources\\resized_body.png')
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
