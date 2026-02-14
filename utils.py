
def count_empty_places(board):
	"""
	Returns the number of empty spaces on the board.
	"""
	count = 0
	from connect_four import EMPTY
	for row in board:
		for cell in row:
			if cell == EMPTY:
				count += 1
	return count


def check_win_sequence(sequence):
	"""
	Check if a sequence contains a winning combination.
	A winning combination is defined as four consecutive pieces of the same color.
	"""
	from connect_four import PLAYER1, PLAYER2
	if sequence.find("RRRR") >= 0:
		return PLAYER1
	elif sequence.find("YYYY") >= 0:
		return PLAYER2
	return None


def check_sloped_diagonals(board, starts, direction):
	"""
	Check sloped diagonals for a win.
	"""
	from connect_four import COLUMNS
	for start_pos in starts:
		row, col = start_pos
		marks: str = ""
		while row >= 0 and 0 <= col < COLUMNS:
			marks += board[row][col]
			row -= 1
			col += direction
		res = check_win_sequence(marks)
		if res is not None:
			return res
	return None


def score_action_position(board, action, pl):
	"""
	Returns the score of the action position by counting the number of empty spaces
	and the number of pieces of the player in all directions from the action position.
	"""
	from connect_four import COLUMNS, ROWS
	row, col = action
	j: int = 1
	i: int = -8
	while row >= 0:
		if board[row][col] == pl:
			break
		row -= 1
		i += j

	row = action[0]

	while row < ROWS:
		if board[row][col] == pl:
			break
		row += 1
		i += j

	row = action[0]

	while col >= 0:
		if board[row][col] == pl:
			break
		col -= 1
		i += j

	col = action[1]

	while col < COLUMNS:
		if board[row][col] == pl:
			break
		col += 1
		i += j

	col = action[1]

	while row >= 0 and col >= 0:
		if board[row][col] == pl:
			break
		row -= 1
		col -= 1
		i += j

	row = action[0]
	col = action[1]

	while row < ROWS and col < COLUMNS:
		if board[row][col] == pl:
			break
		row += 1
		col += 1
		i += j

	row = action[0]
	col = action[1]

	while row >= 0 and col < COLUMNS:
		if board[row][col] == pl:
			break
		row -= 1
		col += 1
		i += j

	row = action[0]
	col = action[1]

	while row < ROWS and col >= 0:
		if board[row][col] == pl:
			break
		row += 1
		col -= 1
		i += j

	return i
