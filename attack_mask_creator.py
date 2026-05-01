import json

move_functions = {
6: (lambda x, y, row, col: row-2 == y and x == col or row-1 == y and x == col or row-1 == y and (col -1 == x or col+1 == x) if row==6  else row-1 == y and x == col or row-1 == y and (col -1 == x or col+1 == x)),

-6: (lambda x, y, row, col: row+2 == y and x == col or row+1 == y and x == col or row+1 == y and (col -1 == x or col+1 == x) if row==1 else row+1 == y and x == col or row+1 == y and (col -1 == x or col+1 == x)),

5: (lambda x, y, row, col: col == x or y == row),

4: (lambda x, y, row, col: abs(x-col) + abs(y-row) == 3 and (abs(x-col) > 0 and abs(y-row) > 0)),

3: (lambda x, y, row, col: abs(x-col) == abs(y-row)),

2: (lambda x, y, row, col: (col == x or y == row) or abs(x-col) == abs(y-row)),

1: (lambda x, y, row, col: (x == col + 1 or x == col - 1 or x == col) and (y == row+1 or y == row or y == row-1)),

-1: (lambda x, y, row, col: (x == col + 1 or x == col - 1 or x == col) and (y == row+1 or y == row or y == row-1))
}

def applychanges(state, moves, piecepos, piece):
	state[piecepos[0]][piecepos[1]] = f"{piece}"
	for move in moves:
		state[move[0]][move[1]] = "*"

	return state

def calculate_possible_moves(row, col, piece):
	moves = []
	for y in range(8):
		for x in range(8):
			if (x,y) != (col, row):
				if move_functions[piece](x,y,row,col):
					moves.append((y,x))
	return moves
	
piece_attack_masks = {}
pieces = [-6, -1, 1, 2, 3, 4, 5, 6]

print(" CALCULATING PIECE ATTACK MASKS")
for i in range(len(pieces)):
	piece = pieces[i]
	square_attacks_dict = {}
	print("")
	print(f"__________________________ {piece} MOVES_________________________")
	print("")
	for row in range(8):
		for col in range(8):
			moves = calculate_possible_moves(row, col, piece)
			square_attacks_dict[(row, col)] = moves
			
			temp_state = [["_" for x in range(8)] for y in range(8)]
			temp_state = applychanges(temp_state, moves, (row, col), piece)
			for i in temp_state:
				print(i)
			print("")
			
	piece_attack_masks[piece] = square_attacks_dict
print("______________DONE____________________")

print(" Writing to file ")
with open("Attack_masks.JSON", "w") as f:
	f.write(json.dumps(str(piece_attack_masks)))