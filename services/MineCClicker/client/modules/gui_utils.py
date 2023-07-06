import pygame
import pygame_textinput
from enum import Enum
from math import floor

from modules.marker import Marker

# =============================================================================== Constants

FPS = 40
SCREEN_SIZE = WIDTH = HEIGHT = 1000
CENTER = SCREEN_SIZE // 2
CELL_SIZE = 20
BOARD_MAX_DIMENSION = 40

# =============================================================================== Colors

BG_COLOR = "#CBFAB5"
TITLE_COLOR = "#0a5e21"
FLAGS_COLOR = "#cc2727"
TEXT_COLOR = "#0a5e21"
INPUT_COLOR = "#d7fcd4"
PLACEHOLDER_COLOR = "#B0BFB1"
HOVERING_COLOR = "#3bb35b"

# =============================================================================== Images

EMPTY = pygame.image.load("assets/Cell.svg")
BUTTON = pygame.image.load("assets/Button.svg")
FLAG = pygame.image.load("assets/Flag.svg")
BOMB = pygame.image.load("assets/Bomb.svg")
NUMBERS = { number: pygame.image.load(f"assets/{number}.svg") for number in range(1, 9) }
RED = pygame.image.load("assets/Red.svg")
SEED = pygame.image.load("assets/Seed.svg")
LOGO = pygame.image.load("assets/Logo.svg")

# =============================================================================== Pygame button enum

class PygameClick(Enum):

	# Mouse buttons
	LEFT = 1
	MIDDLE = 2
	RIGHT = 3

# =============================================================================== GUI Elements

class Text():
	def __init__(self, text, center=(CENTER, 100), topleft=None, font_size=50, color=TITLE_COLOR):
		self.text = get_font(font_size).render(text, True, color, BG_COLOR)
		if topleft is not None:
			self.rect = self.text.get_rect(topleft=topleft)
		else:
			self.rect = self.text.get_rect(center=center)

	def render(self, screen):
		screen.blit(self.text, self.rect)

class Button():
	def __init__(self, text_input, pos, image=None, font=35, base_color=TEXT_COLOR, hovering_color=HOVERING_COLOR):
		self.image = image
		self.x_pos = pos[0]
		self.y_pos = pos[1]
		self.font = get_font(font)
		self.base_color, self.hovering_color = base_color, hovering_color
		self.text_input = text_input
		self.text = self.font.render(self.text_input, True, self.base_color)
		if self.image is None:
			self.image = self.text
		self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
		self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

	def update(self, screen):
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)

	def checkForInput(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			return True
		return False

	def changeColor(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = self.font.render(self.text_input, True, self.hovering_color, BG_COLOR)
		else:
			self.text = self.font.render(self.text_input, True, self.base_color, BG_COLOR)

def render_buttons(SCREEN, pos, buttons):
	for button in buttons:
		button.changeColor(pos)
		button.update(SCREEN)
						
class TextInput():
	def __init__(self, placeholder, y, h=50, xoffset=90, max_len=0x20, validator=None):
		self.validator = lambda input: len(input) <= max_len and (validator is None or validator(input))
		self.manager = pygame_textinput.TextInputManager(validator = self.validator)
		self.pos = (xoffset, y, WIDTH - xoffset*2, h)
		self.visualizer = pygame_textinput.TextInputVisualizer(self.manager, get_font(25), True, PLACEHOLDER_COLOR, 400, 1, PLACEHOLDER_COLOR)
		self.rect = pygame.Rect(self.pos)
		self.isActive = False
		self.isClean = False
		self.visualizer.value = placeholder

	@property
	def value(self):
		return self.visualizer.value
	
	@property
	def isValid(self):
		return self.isClean and self.visualizer.value != ""

	def update(self, events):
		self.visualizer.update(events)

	def clean(self):
		self.visualizer.value = ""
		self.isClean = True

	def active(self, value=True):
		if value:
			self.visualizer.font_color = TEXT_COLOR
			self.visualizer.cursor_color = TEXT_COLOR
			self.isActive = True
		else:
			self.visualizer.font_color = PLACEHOLDER_COLOR
			self.visualizer.cursor_color = INPUT_COLOR
			self.isActive = False
			
	def render(self, events, screen):
		if self.isActive:
			self.update(events)
		pygame.draw.rect(screen, INPUT_COLOR, self.rect)
		screen.blit(self.visualizer.surface, (self.pos[0] + 10, self.pos[1] + 10))

	def click(self, pos):
		if self.rect.collidepoint(pos):
			if not self.isClean:
				self.clean()
			self.active()
		else:
			self.active(False)

class NumericInput(TextInput):
	def __init__(self, placeholder, y, h=50, xoffset=90, max_len=0x1f, max_value=None):

		validator = lambda input: (input.isnumeric() and int(input) > 0 and (max_value is None or int(input) <= max_value)) if len(input) > 0 else True
		super().__init__(placeholder, y, h, xoffset, max_len, validator)

	@property
	def value(self):
		return int(self.visualizer.value) if self.visualizer.value != "" else 0

# =============================================================================== Board utils

def render_image(screen, image, center):
	rect = image.get_rect(center=center)
	screen.blit(image, rect)

def render_cell(screen, board_dimension, graphic_board, coords, image):
	i, j = coords
	board_size = board_dimension * CELL_SIZE
	offset = (SCREEN_SIZE - board_size) // 2
	jc = j * CELL_SIZE + CELL_SIZE // 2 + offset
	ic = i * CELL_SIZE + CELL_SIZE // 2 + offset

	if graphic_board[i][j] != image:
		graphic_board[i][j] = image
		render_image(screen, image, (jc, ic))

def render_board(screen, board_dimension, board, graphic_board):
	for i in range(board_dimension):
		for j in range(board_dimension):
			cell = board[i][j]
			if cell == Marker.COVERED:
				render_cell(screen, board_dimension, graphic_board, (i, j), BUTTON)
			elif cell == Marker.FLAG:
				render_cell(screen, board_dimension, graphic_board, (i, j), BUTTON)
				render_cell(screen, board_dimension, graphic_board, (i, j), FLAG)
			elif cell == Marker.BOMB:
				render_cell(screen, board_dimension, graphic_board, (i, j), BOMB)
			elif cell == Marker.RED:
				render_cell(screen, board_dimension, graphic_board, (i, j), RED)
			else:
				render_cell(screen, board_dimension, graphic_board, (i, j), EMPTY)
				if cell in NUMBERS.keys():	# Numbers
					render_cell(screen, board_dimension, graphic_board, (i, j), NUMBERS[cell])

	pygame.display.flip()

def render_game_over(screen, board_dimension, board, graphic_board):
	board = [ [ Marker.RED if cell == Marker.COVERED else cell for cell in row ] for row in board ]
	render_board(screen, board_dimension, board, graphic_board)

def check_inside(pos, board_dimension):
	x, y = pos
	board_size = board_dimension * CELL_SIZE
	offset = (SCREEN_SIZE - board_size) // 2

	if x <= offset or x >= (offset + board_size) or y <= offset or y >= (offset + board_size):
		return False
	return True

def get_coords(pos, board_dimension):
	x, y = pos
	board_size = board_dimension * CELL_SIZE
	offset = (SCREEN_SIZE - board_size) // 2
	row = floor((y - offset) / CELL_SIZE)
	col = floor((x - offset) / CELL_SIZE)
	return row, col

def check_move(board, row, col):
	if board[row][col] == Marker.COVERED:
		return True
	return False

# =============================================================================== Misc utils

def get_font(size):
	return pygame.font.Font("assets/font.ttf", size)
