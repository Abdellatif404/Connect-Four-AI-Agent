import pygame
import sys
import time
import math
import connect_four as cf
import random


class ConnectFourGame:
	def __init__(self):
		pygame.init()
		pygame.display.set_caption("Connect Four")

		# Game settings
		self.square_size = 100
		self.animation_speed = 15  # pixels per frame
		self.fps = 60
		self.clock = pygame.time.Clock()

		# Board dimensions
		self.columns = cf.COLUMNS
		self.rows = cf.ROWS
		self.sidebar_width = 300
		self.width = self.columns * self.square_size + self.sidebar_width
		self.game_width = self.columns * self.square_size
		self.height = (self.rows + 1) * self.square_size
		self.size = (self.width, self.height)

		# Colors
		self.blue = (53, 93, 165)
		self.dark_blue = (37, 65, 118)
		self.black = (15, 15, 25)
		self.red = (220, 30, 30)
		self.dark_red = (180, 30, 30)
		self.yellow = (240, 230, 40)
		self.dark_yellow = (200, 190, 45)
		self.white = (245, 245, 245)
		self.gray = (200, 200, 200)
		self.light_gray = (230, 230, 230)
		self.sidebar_bg = (30, 30, 40)

		# Setup display
		self.screen = pygame.display.set_mode(self.size)
		pygame.display.set_icon(self.create_icon())

		# Load fonts
		self.title_font = pygame.font.SysFont("arial", 64, bold=True)
		self.large_font = pygame.font.SysFont("arial", 42, bold=True)
		self.medium_font = pygame.font.SysFont("arial", 28)
		self.small_font = pygame.font.SysFont("arial", 22)

		# Game state
		self.user = None
		self.board = cf.initial_state()
		self.ai_thinking = False
		self.game_over = False
		self.winner = None
		self.hover_col = None
		self.dropping_piece = False
		self.last_ai_move = None
		self.particles = []
		self.message = None
		self.drop_sound = self.generate_drop_sound()
		self.win_sound = self.generate_win_sound()
		self.ai_stats = {
			"moves": 0,
			"thinking_time": 0.0,
			"depth": 0,
			"positions_evaluated": 0,
			"positions_per_second": 0,
			"current_move_positions": 0,
			"total_positions": 0
		}

	def create_icon(self):
		"""Create a simple game icon"""
		icon = pygame.Surface((32, 32))
		icon.fill(self.blue)
		pygame.draw.circle(icon, self.red, (8, 8), 6)
		pygame.draw.circle(icon, self.yellow, (24, 24), 6)
		pygame.draw.circle(icon, self.black, (24, 8), 6)
		pygame.draw.circle(icon, self.black, (8, 24), 6)
		return icon

	@staticmethod
	def generate_drop_sound():
		"""Generate a simple sound effect for dropping pieces - fixed index range"""
		sound = pygame.mixer.Sound(buffer=bytes([128] * 4000))
		arr = pygame.sndarray.samples(sound)

		for i in range(min(4000, len(arr))):
			if i < 1000:
				arr[i] = int(32767 * math.sin(i * 0.03) * (1 - i / 1000))
			else:
				arr[i] = int(16383 * math.sin(i * 0.06) * (1 - (i - 1000) / 3000))
		return sound

	@staticmethod
	def generate_win_sound():
		"""Generate a simple victory sound effect - fixed index range"""
		sound = pygame.mixer.Sound(buffer=bytes([128] * 8000))
		arr = pygame.sndarray.samples(sound)

		for i in range(min(8000, len(arr))):
			if i < 4000:
				arr[i] = int(20000 * math.sin(i * 0.02) * (1 - i / 8000))
			else:
				arr[i] = int(20000 * math.sin(i * 0.03) * (1 - i / 8000))
		return sound

	@staticmethod
	def draw_rounded_rect(surface, rect, color, corner_radius):
		"""Draw a rounded rectangle"""
		if corner_radius < 0:
			corner_radius = 0

		# rect dimensions
		x, y, width, height = rect

		# Draw main rectangle
		pygame.draw.rect(surface, color, (x + corner_radius, y, width - 2 * corner_radius, height))
		pygame.draw.rect(surface, color, (x, y + corner_radius, width, height - 2 * corner_radius))

		# Draw four corners
		pygame.draw.circle(surface, color, (x + corner_radius, y + corner_radius), corner_radius)
		pygame.draw.circle(surface, color, (x + width - corner_radius, y + corner_radius), corner_radius)
		pygame.draw.circle(surface, color, (x + corner_radius, y + height - corner_radius), corner_radius)
		pygame.draw.circle(surface, color, (x + width - corner_radius, y + height - corner_radius), corner_radius)

	def draw_piece(self, col, row, player, y_offset=0):
		"""Draw a game piece with improved 3D effect"""
		x = int(col * self.square_size + self.square_size / 2)
		y = int((row + 1) * self.square_size + self.square_size / 2) + y_offset
		radius = int(self.square_size * 0.4)

		if player == cf.PLAYER1:  # Red player
			color = self.red
			highlight = (min(color[0] + 70, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
			shadow = (max(color[0] - 70, 0), max(color[1] - 30, 0), max(color[2] - 30, 0))
		else:  # Yellow player
			color = self.yellow
			highlight = (min(color[0] + 50, 255), min(color[1] + 50, 255), min(color[2] + 20, 255))
			shadow = (max(color[0] - 50, 0), max(color[1] - 50, 0), max(color[2] - 30, 0))

		# Draw gradient for more 3D effect (multiple circles from outer to inner)
		for i in range(5):
			factor = i / 4  # 0 to 1
			current_radius = radius * (1 - 0.2 * factor)

			# Blend between shadow and highlight based on position
			if i < 2:  # Outer rings - more shadow influence
				blend_color = (
					int(shadow[0] + (color[0] - shadow[0]) * factor * 1.5),
					int(shadow[1] + (color[1] - shadow[1]) * factor * 1.5),
					int(shadow[2] + (color[2] - shadow[2]) * factor * 1.5)
				)
			else:  # Inner rings - more highlight influence
				blend_color = (
					int(color[0] + (highlight[0] - color[0]) * (factor - 0.5) * 2),
					int(color[1] + (highlight[1] - color[1]) * (factor - 0.5) * 2),
					int(color[2] + (highlight[2] - color[2]) * (factor - 0.5) * 2)
				)

			pygame.draw.circle(self.screen, blend_color, (x, y), current_radius)

		# Draw glossy highlight (small circular highlight)
		highlight_radius = radius * 0.3
		highlight_offset = radius * 0.33
		pygame.draw.circle(
			self.screen,
			highlight,
			(x - highlight_offset, y - highlight_offset),
			highlight_radius
		)

		# Draw outline
		pygame.draw.circle(self.screen, self.black, (x, y), radius, width=2)

	def draw_board(self):
		"""Draw the game board with slots for pieces and the sidebar"""
		# Draw background
		self.screen.fill(self.black)

		# Draw sidebar background
		pygame.draw.rect(self.screen, self.sidebar_bg,
							(self.game_width, 0, self.sidebar_width, self.height))

		# Draw top bar
		pygame.draw.rect(self.screen, self.dark_blue, (0, 0, self.game_width, self.square_size))

		# Draw board background
		pygame.draw.rect(self.screen, self.blue,
							(0, self.square_size, self.game_width, self.height - self.square_size))

		# Draw hover column highlight if user's turn
		if self.hover_col is not None and cf.player(self.board) == self.user and not self.dropping_piece:
			pygame.draw.rect(self.screen, self.dark_blue,
								(self.hover_col * self.square_size, self.square_size,
								self.square_size, self.height - self.square_size))

			# Draw preview piece
			preview_alpha = 128  # Semi-transparent
			s = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
			if self.user == cf.PLAYER1:
				pygame.draw.circle(s, (self.red[0], self.red[1], self.red[2], preview_alpha),
									(self.square_size // 2, self.square_size // 2), int(self.square_size * 0.4))
			else:
				pygame.draw.circle(s, (self.yellow[0], self.yellow[1], self.yellow[2], preview_alpha),
									(self.square_size // 2, self.square_size // 2), int(self.square_size * 0.4))
			self.screen.blit(s, (self.hover_col * self.square_size, 0))

		# Draw board holes
		for c in range(self.columns):
			for r in range(self.rows):
				x = int(c * self.square_size + self.square_size / 2)
				y = int((r + 1) * self.square_size + self.square_size / 2)
				radius = int(self.square_size * 0.4)

				# Draw hole shadow
				pygame.draw.circle(self.screen, self.dark_blue, (x + 3, y + 3), radius)

				# Draw hole
				pygame.draw.circle(self.screen, self.black, (x, y), radius)

				# Draw subtle inner highlight
				pygame.draw.circle(self.screen, self.dark_blue, (x, y), radius, width=2)

		# Draw placed pieces (except the currently dropping one)
		for c in range(self.columns):
			for r in range(self.rows):
				# if (self.board[0] | self.board[1]) & (1 << (r * 8 + c)):
				if self.board[r][c] != cf.EMPTY:
					# Skip the currently dropping piece to avoid drawing it twice
					if not (self.dropping_piece and r == self.drop_row and c == self.drop_col):
						self.draw_piece(c, r, self.board[r][c])
						# player = cf.PLAYER1 if (self.board[0] & (1 << (r * 8 + c))) else cf.PLAYER2
						# self.draw_piece(c, r, player)
						# self.draw_piece(c, r, cf.player(self.board))

		# Draw the dropping piece if exists
		if self.dropping_piece:
			self.draw_piece(self.drop_col, self.drop_row, self.drop_player, y_offset=self.drop_y)

		# Highlight last AI move
		if self.last_ai_move and not self.game_over:
			row, col = self.last_ai_move
			x = col * self.square_size + self.square_size // 2
			y = (row + 1) * self.square_size + self.square_size // 2
			pygame.draw.circle(self.screen, self.white, (x, y), int(self.square_size * 0.45), width=2)

		# Draw particles
		for particle in self.particles:
			pygame.draw.circle(self.screen, particle['color'],
								(particle['x'], particle['y']),
								particle['size'])

		# Draw the sidebar content
		self.draw_sidebar()

	def draw_sidebar(self):
		"""Draw the sidebar with AI information and reset button"""
		# Draw dividing line
		pygame.draw.line(self.screen, self.white,
							(self.game_width, 0),
							(self.game_width, self.height), 2)

		# Draw title
		sidebar_title = self.medium_font.render("Game Info", True, self.white)
		title_rect = sidebar_title.get_rect(
			center=(self.game_width + self.sidebar_width // 2, 50)
		)
		self.screen.blit(sidebar_title, title_rect)

		# Draw player info
		y_pos = 110
		if self.user:
			player_text = "You: " + ("RED" if self.user == cf.PLAYER1 else "YELLOW")
			player_color = self.red if self.user == cf.PLAYER1 else self.yellow
			player_label = self.small_font.render(player_text, True, player_color)
			player_rect = player_label.get_rect(
				center=(self.game_width + self.sidebar_width // 2, y_pos)
			)
			self.screen.blit(player_label, player_rect)

			ai_text = "AI: " + ("YELLOW" if self.user == cf.PLAYER1 else "RED")
			ai_color = self.yellow if self.user == cf.PLAYER1 else self.red
			ai_label = self.small_font.render(ai_text, True, ai_color)
			ai_rect = ai_label.get_rect(
				center=(self.game_width + self.sidebar_width // 2, y_pos + 30)
			)
			self.screen.blit(ai_label, ai_rect)

		# Draw AI statistics
		y_pos = 210
		stats_title = self.small_font.render("AI Statistics:", True, self.white)
		self.screen.blit(stats_title, (self.game_width + 20, y_pos))

		y_pos += 30

		# Draw AI stats in a cleaner format with labels and values
		stats = [
			("Moves:", f"{self.ai_stats['moves']}"),
			("Thinking time:", f"{self.ai_stats['thinking_time']:.2f}s"),
			("Search depth:", f"{self.ai_stats['depth']}"),
			("Positions (last):", f"{self.ai_stats['current_move_positions']:,}"),
			("Positions (total):", f"{self.ai_stats['positions_evaluated']:,}"),
		]

		# Add positions per second if available
		if self.ai_stats['positions_per_second'] > 0:
			stats.append(("Positions/second:", f"{self.ai_stats['positions_per_second']:,.0f}"))

		for label, value in stats:
			# Label in white
			label_surface = self.small_font.render(label, True, self.white)
			self.screen.blit(label_surface, (self.game_width + 30, y_pos))

			# Value in light gray, right-aligned
			value_surface = self.small_font.render(value, True, self.light_gray)
			value_rect = value_surface.get_rect(
				right=self.game_width + self.sidebar_width - 30,
				top=y_pos
			)
			self.screen.blit(value_surface, value_rect)

			y_pos += 25

		# Draw reset button
		button_width, button_height = 180, 60
		reset_button = pygame.Rect(
			self.game_width + (self.sidebar_width - button_width) // 2,
			self.height - 100,
			button_width, button_height
		)

		self.draw_rounded_rect(self.screen, reset_button, self.blue, 10)
		self.draw_rounded_rect(
			self.screen,
			(reset_button.x + 3, reset_button.y + 3, button_width - 6, button_height - 6),
			self.dark_blue, 8
		)

		reset_text = self.medium_font.render("Reset Game", True, self.white)
		reset_rect = reset_text.get_rect(center=reset_button.center)
		self.screen.blit(reset_text, reset_rect)

		# Check for button click if game is in progress
		if self.user:  # Only enable the button if a game is in progress
			mouse_pos = pygame.mouse.get_pos()
			mouse_clicked = pygame.mouse.get_pressed()[0]

			# Highlight button on hover
			if reset_button.collidepoint(mouse_pos):
				pygame.draw.rect(self.screen, self.white, reset_button, width=2, border_radius=10)
				if mouse_clicked:
					time.sleep(0.2)
					self.reset_game()

	def update_particles(self):
		"""Update particle positions and lifetimes"""
		new_particles = []
		for particle in self.particles:
			particle['life'] -= 1
			if particle['life'] > 0:
				particle['x'] += particle['dx']
				particle['y'] += particle['dy']
				particle['dy'] += 0.2  # Gravity
				new_particles.append(particle)
		self.particles = new_particles

	def create_particles(self, x, y, color, count=20):
		"""Create celebration particles at position"""
		for _ in range(count):
			angle = 2 * math.pi * random.random()
			speed = 2 + 3 * random.random()
			self.particles.append({
				'x': x,
				'y': y,
				'dx': math.cos(angle) * speed,
				'dy': math.sin(angle) * speed - 2,  # Initial upward velocity
				'color': color,
				'size': 2 + random.random() * 4,
				'life': 30 + random.randint(0, 20)
			})

	def animate_piece_drop(self, col, row, player):
		"""Animate a piece dropping into place"""
		self.dropping_piece = True
		self.drop_col = col
		self.drop_row = row
		self.drop_player = player
		self.drop_y = -self.square_size
		self.target_y = 0

		while self.drop_y < self.target_y:
			self.drop_y += self.animation_speed
			if self.drop_y >= self.target_y:
				self.drop_y = self.target_y

			# Draw everything
			self.draw_board()

			# Top information display
			if not self.game_over:
				self.draw_turn_indicator()

			pygame.display.flip()
			self.clock.tick(self.fps)

		# Animation complete
		self.dropping_piece = False
		self.drop_sound.play()

		# Add impact particles
		x = col * self.square_size + self.square_size // 2
		y = (row + 1) * self.square_size + self.square_size // 2
		particle_color = self.red if player == cf.PLAYER1 else self.yellow
		self.create_particles(x, y + self.square_size * 0.4, particle_color, count=10)

	def handle_user_choice(self):
		"""Handle the player color selection screen"""
		self.screen.fill(self.black)

		# Calculate center of the game area (excluding sidebar)
		game_center_x = self.game_width // 2 + self.sidebar_width // 2

		# Draw title
		title = self.title_font.render("CONNECT FOUR", True, self.white)
		title_rect = title.get_rect(center=(game_center_x, self.height // 4 - 20))
		self.screen.blit(title, title_rect)

		# Draw subtitle
		subtitle = self.medium_font.render("Choose your color", True, self.gray)
		subtitle_rect = subtitle.get_rect(center=(game_center_x, self.height // 4 + 40))
		self.screen.blit(subtitle, subtitle_rect)

		# Draw buttons
		button_width, button_height = 220, 80

		# Red button - properly centered in game area
		red_button = pygame.Rect(game_center_x - button_width - 40,
									self.height // 2, button_width, button_height)
		self.draw_rounded_rect(self.screen, red_button, self.red, 15)
		self.draw_rounded_rect(self.screen,
								(red_button.x + 5, red_button.y + 5,
								button_width - 10, button_height - 10),
								self.dark_red, 10)

		red_text = self.large_font.render("RED", True, self.white)
		red_text_rect = red_text.get_rect(center=red_button.center)
		self.screen.blit(red_text, red_text_rect)

		# Yellow button - properly centered in game area
		yellow_button = pygame.Rect(game_center_x + 40,
									self.height // 2, button_width, button_height)
		self.draw_rounded_rect(self.screen, yellow_button, self.yellow, 15)
		self.draw_rounded_rect(self.screen,
								(yellow_button.x + 5, yellow_button.y + 5,
								button_width - 10, button_height - 10),
								self.dark_yellow, 10)

		yellow_text = self.large_font.render("YELLOW", True, self.black)
		yellow_text_rect = yellow_text.get_rect(center=yellow_button.center)
		self.screen.blit(yellow_text, yellow_text_rect)

		# Draw game instructions
		instructions = [
			"How to play:",
			"• Click to drop your piece in a column",
			"• Get 4 pieces in a row (horizontal, vertical, or diagonal) to win",
			"• Outsmart the AI opponent!"
		]

		y_pos = self.height * 3 / 4
		for instruction in instructions:
			text = self.small_font.render(instruction, True, self.gray)
			text_rect = text.get_rect(center=(game_center_x, y_pos))
			self.screen.blit(text, text_rect)
			y_pos += 30

		# Check for button clicks
		mouse_pos = pygame.mouse.get_pos()
		mouse_clicked = pygame.mouse.get_pressed()[0]

		# Highlight buttons on hover
		if red_button.collidepoint(mouse_pos):
			pygame.draw.rect(self.screen, self.white, red_button, width=3, border_radius=15)
			if mouse_clicked:
				time.sleep(0.2)
				self.user = cf.PLAYER1
				return True

		if yellow_button.collidepoint(mouse_pos):
			pygame.draw.rect(self.screen, self.white, yellow_button, width=3, border_radius=15)
			if mouse_clicked:
				time.sleep(0.2)
				self.user = cf.PLAYER2
				return True

		return False

	def draw_turn_indicator(self):
		"""Draw whose turn it is at the top of the screen"""
		current_player = cf.player(self.board)

		if self.ai_thinking:
			thinking_text = "AI thinking..."
			color = self.red if self.user != cf.PLAYER1 else self.yellow
			thinking_label = self.large_font.render(thinking_text, True, color)
			thinking_rect = thinking_label.get_rect(center=(self.width // 2 - self.sidebar_width // 2, self.square_size // 2))
			self.screen.blit(thinking_label, thinking_rect)

			# Add animated dots
			dot_count = int((time.time() * 2) % 4)
			dots = "." * dot_count
			dot_label = self.large_font.render(dots, True, color)
			dot_rect = dot_label.get_rect(left=thinking_rect.right, centery=thinking_rect.centery)
			self.screen.blit(dot_label, dot_rect)
		else:
			if current_player == self.user:
				text = "Your turn"
				color = self.red if self.user == cf.PLAYER1 else self.yellow
			else:
				text = "AI's turn"
				color = self.red if self.user != cf.PLAYER1 else self.yellow

			turn_label = self.large_font.render(text, True, color)
			turn_rect = turn_label.get_rect(center=(self.width // 2 - self.sidebar_width // 2, self.square_size // 2))
			self.screen.blit(turn_label, turn_rect)

			# Draw message if any
			if self.message and time.time() - self.message_time < 3:
				message_label = self.small_font.render(self.message, True, self.light_gray)
				message_rect = message_label.get_rect(center=(self.width // 2 - self.sidebar_width // 2, self.square_size // 2 + 30))
				self.screen.blit(message_label, message_rect)

	def handle_game_over(self):
		"""Handle game over screen with winner announcement and play again button"""
		# Draw particles for celebration
		if len(self.particles) < 100 and self.winner:
			# Create new victory particles near the corners
			particle_color = self.red if self.winner == cf.PLAYER1 else self.yellow
			self.create_particles(random.randint(0, self.width), random.randint(0, self.height), particle_color)

		# Draw semi-transparent overlay
		overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
		overlay.fill((0, 0, 0, 180))  # Black with alpha
		self.screen.blit(overlay, (0, 0))

		# Draw winner announcement
		if self.winner:
			if (self.winner == cf.PLAYER1 and self.user == cf.PLAYER1) or \
					(self.winner == cf.PLAYER2 and self.user == cf.PLAYER2):
				result_text = "You Win!"
			else:
				result_text = "AI Wins"

			color = self.red if self.winner == cf.PLAYER1 else self.yellow
		else:
			result_text = "It's a Tie!"
			color = self.white

		# Draw winner text with shadow
		winner_label = self.title_font.render(result_text, True, color)
		shadow_label = self.title_font.render(result_text, True, self.black)

		text_rect = winner_label.get_rect(center=(self.width // 2, self.height // 3))
		shadow_rect = shadow_label.get_rect(center=(self.width // 2 + 3, self.height // 3 + 3))

		self.screen.blit(shadow_label, shadow_rect)
		self.screen.blit(winner_label, text_rect)

		# Draw play again button
		button_width, button_height = 200, 60
		again_button = pygame.Rect(self.width // 2 - button_width // 2,
									self.height * 2 // 3, button_width, button_height)

		self.draw_rounded_rect(self.screen, again_button, self.blue, 10)
		self.draw_rounded_rect(self.screen,
								(again_button.x + 3, again_button.y + 3,
								button_width - 6, button_height - 6),
								self.dark_blue, 8)

		again_text = self.medium_font.render("Play Again", True, self.white)
		again_rect = again_text.get_rect(center=again_button.center)
		self.screen.blit(again_text, again_rect)

		# Check for button click
		mouse_pos = pygame.mouse.get_pos()
		mouse_clicked = pygame.mouse.get_pressed()[0]

		# Highlight button on hover
		if again_button.collidepoint(mouse_pos):
			pygame.draw.rect(self.screen, self.white, again_button, width=2, border_radius=10)
			if mouse_clicked:
				time.sleep(0.2)
				self.reset_game()
				return True

		return False

	def reset_game(self):
		"""Reset the game state for a new game"""
		self.user = None
		self.board = cf.initial_state()
		self.ai_thinking = False
		self.game_over = False
		self.winner = None
		self.last_ai_move = None
		self.particles = []
		self.message = None
		# Reset AI stats
		self.ai_stats = {
			"moves": 0,
			"thinking_time": 0.0,
			"depth": 0,
			"positions_evaluated": 0,
			"positions_per_second": 0,
			"current_move_positions": 0,
			"total_positions": 0
		}

	def check_valid_move(self, col):
		"""Check if a move in the given column is valid"""
		if col < 0 or col >= self.columns:
			return False

		# Check if the column is full
		return self.board[0][col] == cf.EMPTY

	def find_row(self, col):
		"""Find the row where a piece would land in the given column"""
		for row in range(self.rows - 1, -1, -1):
			if self.board[row][col] == cf.EMPTY:
				return row
		return -1  # Column is full

	def make_move(self, col, player):
		"""Make a move in the given column for the specified player"""
		row = self.find_row(col)
		if row == -1:  # Invalid move
			return False

		# Animate the piece dropping
		self.animate_piece_drop(col, row, player)

		# Update the board
		self.board = cf.result(self.board, (row, col))

		# Check for win condition
		win = cf.winner(self.board)
		if win or cf.terminal(self.board):
			self.game_over = True
			self.winner = win
			if win:
				self.win_sound.play()
				# Create winning particles
				color = self.red if win == cf.PLAYER1 else self.yellow
				for _ in range(50):
					self.create_particles(
						random.randint(0, self.width),
						random.randint(0, self.height),
						color
					)

		return True

	def run(self):
		"""Main game loop"""
		import time  # For AI thinking time measurement
		running = True

		while running:
			self.clock.tick(self.fps)

			# Process events
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False

				if event.type == pygame.MOUSEMOTION:
					# Track mouse for column highlighting
					if not self.game_over and self.user:
						x = event.pos[0]
						if x < self.game_width:  # Only within game area
							col = x // self.square_size
							if 0 <= col < self.columns:
								self.hover_col = col
							else:
								self.hover_col = None
						else:
							self.hover_col = None  # Mouse is in sidebar

				if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
					if not self.user:
						# At the color selection screen
						continue  # Handled in handle_user_choice
					elif not self.game_over and not self.dropping_piece:
						# In-game click
						if cf.player(self.board) == self.user:
							x = event.pos[0]
							if x < self.game_width:  # Only process clicks in game area
								col = x // self.square_size

								if self.check_valid_move(col):
									self.make_move(col, self.user)
								else:
									# Invalid move - show message
									if 0 <= col < self.columns:
										self.message = "Column is full! Try another column."
										self.message_time = time.time()

			# Game states
			if not self.user:
				# Color selection screen
				if self.handle_user_choice():
					# User made selection, proceed to game
					pass
			elif not self.game_over:
				# Normal gameplay
				current_player = cf.player(self.board)

				# Handle AI turn
				if current_player != self.user and not self.dropping_piece and not self.ai_thinking:
					self.ai_thinking = True
					self.draw_board()
					self.draw_turn_indicator()
					pygame.display.flip()

					# Measure AI thinking time
					start_time = time.time()

					# Add slight delay for AI "thinking"
					pygame.time.delay(750)

					# Get AI move
					res = cf.minimax(self.board)
					move = res[0][1]
					positions_in_this_move = res[2]  # Path cost is positions evaluated

					# Update AI stats
					ai_time = time.time() - start_time
					self.ai_stats["moves"] += 1
					self.ai_stats["depth"] = res[1]
					self.ai_stats["current_move_positions"] = positions_in_this_move
					self.ai_stats["positions_evaluated"] += positions_in_this_move

					# Calculate positions per second
					if ai_time > 0:
						self.ai_stats["positions_per_second"] = positions_in_this_move / ai_time

					# Update running average of thinking time
					if self.ai_stats["moves"] == 1:
						self.ai_stats["thinking_time"] = ai_time
					else:
						self.ai_stats["thinking_time"] = (
								(self.ai_stats["thinking_time"] * (self.ai_stats["moves"] - 1) + ai_time) /
								self.ai_stats["moves"]
						)

					self.ai_thinking = False

					if move:
						row, col = move
						self.last_ai_move = move
						self.make_move(col, current_player)

				# Draw the game board
				self.draw_board()
				self.draw_turn_indicator()
				self.update_particles()
			else:
				# Game over state
				self.draw_board()
				self.update_particles()
				if self.handle_game_over():
					# User clicked play again
					pass

			# Update display
			pygame.display.flip()

		pygame.quit()
		sys.exit()


if __name__ == '__main__':
	game = ConnectFourGame()
	game.run()
