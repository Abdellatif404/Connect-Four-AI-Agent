
import math
import utils
import cProfile

PLAYER1 = 'R'
PLAYER2 = 'Y'
EMPTY = ' '
ROWS = 6
COLUMNS = 7
MIN_DEPTH = 5

positions_evaluated = 0


def reset_positions_counter():
	global positions_evaluated
	positions_evaluated = 0


def initial_state():
	"""
	Returns starting state of the board (6x7 grid).
	"""
	return [[EMPTY for _ in range(COLUMNS)] for _ in range(ROWS)]


def player(board):
	"""
	Returns player who has the next turn on a board.
	"""
	count = 0
	for row in board:
		for cell in row:
			if cell != EMPTY:
				count += 1
	if count == COLUMNS * ROWS:
		return None
	elif count % 2 == 0:
		return PLAYER1
	else:
		return PLAYER2


def actions(board):
	"""
	Returns set of all possible actions (row, column) available on the board.
	"""
	possible_actions = set()
	for cell in range(COLUMNS):
		for row in range(ROWS - 1, -1, -1):
			if board[row][cell] == EMPTY:
				possible_actions.add((row, cell))
				break
	return possible_actions


def result(board, action):
	"""
	Returns the board that results from making move (row, column) on the board.
	"""
	if (action[0] < 0 or action[0] > 5) or (action[1] < 0 or action[1] > 6):
		raise Exception("Action is out of bounds")
	# board_copy = copy.deepcopy(board)
	board_copy = [row[:] for row in board]
	if board_copy[action[0]][action[1]] is EMPTY:
		board_copy[action[0]][action[1]] = player(board)
	# else:
	#	 raise Exception("Not a valid action")
	return board_copy


def winner(board):
	"""
	Returns the winner of the game, if there is one.
	"""
	marks: str = ""
	for cell in range(COLUMNS):
		for row in range(ROWS - 1, -1, -1):
			marks += board[row][cell]
		marks += '|'

	for row in range(ROWS - 1, -1, -1):
		for cell in range(COLUMNS):
			marks += board[row][cell]
		marks += '|'

	starts = [(5, 3), (5, 4), (5, 5), (5, 6), (4, 6), (3, 6)]
	for start_pos in starts:
		row, col = start_pos
		while row >= 0 and 0 <= col < COLUMNS:
			marks += board[row][col]
			row -= 1
			col += -1
		marks += '|'

	starts = [(5, 3), (5, 2), (5, 1), (5, 0), (4, 0), (3, 0)]
	for start_pos in starts:
		row, col = start_pos
		while row >= 0 and 0 <= col < COLUMNS:
			marks += board[row][col]
			row -= 1
			col += 1
		marks += '|'

	return utils.check_win_sequence(marks)


def terminal(board):
	"""
	Returns True if game is over, False otherwise.
	"""
	return winner(board) is not None or player(board) is None


def utility(board):
	"""
	Returns 100 if PLAYER1 has won, -100 if PLAYER2 has won, 0 otherwise.
	"""
	win = winner(board)
	if win == PLAYER1:
		return 1000
	elif win == PLAYER2:
		return -1000
	else:
		return 0


def heuristic(board, action):
	"""
	Returns a heuristic value for the board.
	"""
	score = 0
	marks: str = ""
	open_seq = ""
	three_seq = []
	two_seq = []
	pl = player(board)

	if action[0] > 0:
		b = result(board, (action[0] - 1, action[1]))
		threat = terminal(b)
		if threat and pl == PLAYER1 and winner(b) == PLAYER2:
			return -1000
		if threat and pl == PLAYER2 and winner(b) == PLAYER1:
			return 1000

	if pl == PLAYER2:
		open_seq = ' RRR '
		three_seq = ['RRR ', ' RRR', 'RR R', 'R RR']
		two_seq = ['RR  ', 'R R ', 'R  R', ' RR ', ' R R', '  RR']
	elif pl == PLAYER1:
		open_seq = ' YYY '
		three_seq = ['YYY ', ' YYY', 'YY Y', 'Y YY']
		two_seq = ['YY  ', 'Y Y ', 'Y  Y', ' YY ', ' Y Y', '  YY']

	for cell in range(COLUMNS):
		for row in range(ROWS - 1, -1, -1):
			marks += board[row][cell]
		marks += '|'

	for row in range(ROWS - 1, -1, -1):
		for cell in range(COLUMNS):
			marks += board[row][cell]
		marks += '|'

	starts = [(5, 3), (5, 4), (5, 5), (5, 6), (4, 6), (3, 6)]

	for start_pos in starts:
		row, col = start_pos
		while row >= 0 and col < COLUMNS:
			marks += board[row][col]
			row -= 1
			col -= 1
		marks += '|'

	starts = [(5, 3), (5, 2), (5, 1), (5, 0), (4, 0), (3, 0)]

	for start_pos in starts:
		row, col = start_pos
		while row >= 0 and col < COLUMNS:
			marks += board[row][col]
			row -= 1
			col += 1
		marks += '|'

	score += marks.count(open_seq) * 30
	for seq in three_seq:
		score += marks.count(seq) * 20
	for seq in two_seq:
		score += marks.count(seq) * 10

	score += utils.score_action_position(board, action, pl)

	if pl == PLAYER1:
		return score * -1
	return score


def max_value(board, depth, prev_min_score=None, action=None):
	"""
	Returns the maximum value of the board (score, move, path_cost).
	"""
	if terminal(board):
		return utility(board), None, 1
	if depth == 0:
		return heuristic(board, action), None, 1

	min_score: float = -math.inf
	best_path_cost: int = 100000000
	move = None
	i = 0
	global positions_evaluated
	for action in actions(board):
		i += 1
		if (prev_min_score is not None and prev_min_score < min_score) and min_score != -math.inf:
			break
		positions_evaluated += 1
		value = min_value(result(board, action), depth - 1, min_score, action)
		score: float = value[0]
		path_cost = value[2]
		if min_score == -math.inf or (score > min_score or (score == min_score and path_cost < best_path_cost)):
			min_score = score
			move = action
			best_path_cost = path_cost
		if prev_min_score is None:
			print(f"+Action {action}: Score {score}, Path Cost {path_cost}, Depth {depth}, Positions Evaluated {positions_evaluated}")
	return min_score, move, best_path_cost + 1


def min_value(board, depth, prev_max_score=None, action=None):
	"""
	Returns the minimum value of the board (score, move, path_cost).
	"""
	if terminal(board):
		return utility(board), None, 1
	if depth == 0:
		return heuristic(board, action), None, 1

	max_score: float = math.inf
	best_path_cost: int = 100000000
	move = None
	i = 0
	global positions_evaluated
	for action in actions(board):
		i += 1
		if (prev_max_score is not None and prev_max_score > max_score) and max_score != math.inf:
			break
		positions_evaluated += 1
		value = max_value(result(board, action), depth - 1, max_score, action)
		score: float = value[0]
		path_cost = value[2]
		if max_score == math.inf or (score < max_score or (score == max_score and path_cost < best_path_cost)):
			max_score = score
			move = action
			best_path_cost = path_cost
		if prev_max_score is None:
			print(f"-Action {action}: Score {score}, Path Cost {path_cost}, Depth {depth}, Positions Evaluated {positions_evaluated}")
	return max_score, move, best_path_cost + 1


def minimax(board):
	"""
	Returns the optimal action for the current player on the board ((score, move, path_cost), depth, positions_evaluated).
	"""
	global positions_evaluated
	reset_positions_counter()

	depth = int((43 - utils.count_empty_places(board)) / 8 + MIN_DEPTH)

	if player(board) == PLAYER1:
		res = max_value(board, depth)
		# print("Depth: ", depth)
		# print("Max Value: ", res[0])
		# print("Move: ", res[1])
		# print("Path Cost: ", res[2])
		# print("Total Positions Evaluated: ", positions_evaluated)
		# print("\n")
		return res, depth, positions_evaluated
	else:
		res = min_value(board, depth)
		# print("Depth: ", depth)
		# print("Min Value: ", res[0])
		# print("Move: ", res[1])
		# print("Path Cost: ", res[2])
		# print("Total Positions Evaluated: ", positions_evaluated)
		# print("\n")
		return res, depth, positions_evaluated
