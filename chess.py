import pygame as pg
from time import sleep
from math import inf
from pickle import load
from evaluation_matrices import evalmats
pg.init()
pg.mixer.init()

screen = pg.display.set_mode((720, 1500))
clock = pg.time.Clock()

#   GLOBAL VARIABLES

mode = "robot"
tilesize = screen.get_width()//8
voffset = screen.get_height()/2 - tilesize*4
turn = 1
coloumns = ["a","b","c","d","e","f","g","h"]

possible_moves = []	# global variable to keep track of possible moves of the selected piece
all_possible_moves = {}

#_______________________

# Keep these None
selection = None
var_king_pos= None
const_king_pos = None
enpasantable = None
king_in_check = None
#_______________________

# Keep these False
white_king_moved = False
black_king_moved = False
right_w_rook_moved = False
left_w_rook_moved = False
right_B_rook_moved = False
left_B_rook_moved = False

move_record = []
gamestate = [
              [-5,-4,-3,-2,-1,-3,-4,-5],
              [-6,-6,-6,-6,-6,-6,-6,-6],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [6, 6, 6, 6, 6, 6, 6, 6],
              [5, 4, 3, 2, 1, 3, 4, 5]
]

# _________________________________

#   Loading Sound effects
move_sound = pg.mixer.Sound("Assets/Move.mp3")
capture_sound = pg.mixer.Sound("Assets/Capture.mp3")
move_sound.set_volume(1.0)
capture_sound.set_volume(1.0)

#   Loading pieces (pngs)
piece_names = ['_king', '_queen','_bishop', '_knight', '_rook', '_pawn']
s_piece_names= ['Kg', 'Qn','Bp', 'Kn', 'Rk', 'Pn']
pieces = {}
for i in range(6):
	img1 = pg.transform.scale(pg.image.load(f'Assets/White{piece_names[i]}.png'), (tilesize, tilesize-10))
	img2 = pg.transform.scale(pg.image.load(f'Assets/Black{piece_names[i]}.png'), (tilesize, tilesize-10))
	pieces[str(i+1)] = img1
	pieces[str(-(i+1))] = img2
#________________________________

# initializing font
moves_text_size = 30
index_text_size = 20
movetextx,movetexty = 20, 200

font = pg.font.Font(None, moves_text_size)
font2 = pg.font.Font(None, index_text_size)
endfont = pg.font.Font(None, 100)
endfont2 = pg.font.Font(None, 50)	

#_______________________________________

# Loading Attack Masks
with open("attack_masks.pkl", "rb") as f:
    attack_masks = load(f)

#  FUNCTIONS			
	
def draw_chess_board(gamestate):
	boxsize = tilesize
	for row in range(8):
		for col in range(8):
			switch = 1 if row%2 == 0 else 0
			if col%2 == switch:
				color = (118, 150, 86)
			else:
				color = (238, 238, 210)
			pg.draw.rect(screen, color,(col*boxsize,voffset + row*boxsize,boxsize,boxsize))
		
			# ovelaying possible moves
			code = gamestate[row][col]
			if possible_moves:
				if (row, col) in possible_moves:
					color = (0, 100, 255)
					if code/turn > 0:
						color = (100, 100, 100)
					elif code/turn < 0:
						color = (255, 100, 100)
					pg.draw.rect(screen, color, (col*boxsize,voffset + row*boxsize,boxsize,boxsize), 4)
			# showing king in check
			if king_in_check and code == turn:
				kcol, krow = const_king_pos[0], const_king_pos[1]
				pg.draw.rect(screen, (255, 0, 0), (kcol*boxsize,voffset + krow*boxsize,boxsize,boxsize))
			
			# drawing pieces
			if code:
				piece= pieces[str(code)]
				piece_rect = piece.get_rect(center = (col*boxsize + tilesize//2, row*boxsize + voffset + tilesize/2))
				screen.blit(piece, piece_rect)	
	add_index_numbers()					
				
				
																				
def handle_click(mx, my):
	global gamestate,selection,possible_moves, turn, king_in_check, const_king_pos, var_king_pos, white_king_moved,black_king_moved, right_w_rook_moved,left_w_rook_moved,right_B_rook_moved,left_B_rook_moved

	row = int((my - voffset) / tilesize)
	col = int(mx / tilesize)
	
	if 0 <= row <= 7 and 0 <= col <= 7:
			piece_code= gamestate[row][col]
			
			if not selection:
				if piece_code != 0 and piece_code/turn > 0:
					selection = (col, row)
					possible_moves = calculate_possible_moves(row, col, piece_code)
					
			elif piece_code/turn > 0:
					selection = (col, row)
					possible_moves = calculate_possible_moves(row, col, piece_code)
					
			elif ((row, col) in possible_moves if possible_moves != None else False) or (mode == "robot" and turn == -1):
				selected_piece = gamestate[selection[1]][selection[0]]
				
				gamestate, castled = make_move(gamestate, ((selection[1], selection[0]),(row, col)), selected_piece, True)
				if piece_code == 0:
					move_sound.play()
				else:
					capture_sound.play()
					
				selection = None
				king_in_check = False
				if not castled:
					if selected_piece == 1:
						white_king_moved = True
					elif selected_piece == -1:
						black_king_moved = True
					elif selected_piece == -5:
						if (row, col) == (0, 0):
							left_B_rook_moved = True
						else:
							right_B_rook_moved = True
					elif selected_piece == 5:
						if (row, col) == (7, 0):
							left_w_rook_moved = True
						else:
							right_w_rook_moved = True
				else:
					if selected_piece == 1:
						if (row, col) == (7, 0):
							left_w_rook_moved = True
						else:
							right_w_rook_moved = True
					if selected_piece == -1:
						if (row, col) == (0, 0):
							left_B_rook_moved = True
						else:
							right_B_rook_moved = True
					
				if kingincheck(gamestate, turn*-1):
					# var king pos always keeps changing when calculating moves but const king pos is set here only when the next turns king is in check
					king_in_check = True
					const_king_pos = var_king_pos
				
				move_record.append((s_piece_names[abs(selected_piece)-1], (row, col)))
				possible_moves = None
				turn *= -1
				detect_check_mate()



def castle_obstruction(selection, row, col):
	obstructed = False
	if selection[1] - 2 == col or selection[1] + 2 == col:
		dx = (col-selection[1])/abs(col-selection[1])
		for i in range(abs(col-selection[1])):
			tempx,tempy = int(selection[1] + dx*(i+1)), selection[0]
			if gamestate[tempy][tempx] != 0:
				return True
			state = [r[:] for r in gamestate]
			state[tempy][tempx] = state[selection[0]][selection[1]]
			state[selection[0]][selection[1]] = 0
			if kingincheck(state, turn):
				obstructed = True
				break
	return obstructed

	
		
def kingincheck(state, turn):
  
    global var_king_pos
    krow, kcol = None, None
    for row in range(8):
        for col in range(8):
            if state[row][col] == turn:
                krow, kcol = row, col
                var_king_pos = (kcol, krow)
                break
        if krow != None and kcol != None:
        	break


    knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
    for dr, dc in knight_moves:
        row, col = krow + dr, kcol + dc
        if 0 <= row < 8 and 0 <= col < 8:
            if state[row][col] == -4 * turn: # Enemy Knight
                return True
                
    directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1),   # Straight
        (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonal
    ]
    
    for i, (dr, dc) in enumerate(directions):
        for dist in range(1, 8):
            row, col = krow + (dr * dist), kcol + (dc * dist)
            if not (0 <= row < 8 and 0 <= col < 8):
                break
            
            piece = state[row][col]
            if piece == 0:
                continue
            
            if piece / turn < 0:
                p_type = abs(piece)
                # Straight lines
                if i < 4: 
                    if p_type == 2 or p_type == 5:
                    	return True
                 # diagonals
                else: 
                    if p_type == 2 or p_type == 3:
                    	return True
                    if dist == 1 and p_type == 6:
                        if turn == 1 and dr == -1:
                        	return True
                        if turn == -1 and dr == 1:
                        	return True
                  
                if dist == 1 and p_type == 1:
                	return True
                
                break
            else:
                break      
    return False	
			
					
def calculate_possible_moves(row, col, piece):
	Psuedo_moves = attack_masks[piece if piece == -6 or piece == -1 else abs(piece)][(row,col)]
	
	moves = []
	captures = []
	blockers = [] # own pieces blocking movement
	
	# filtering all moves that lie on own pieces and saving captures
	for y, x in Psuedo_moves:
		piece_side = gamestate[y][x]*turn
		if  piece_side <= 0:
			moves.append((y,x))
			if piece_side < 0:
				captures.append((y, x))
		else:
			blockers.append((y,x))
			
	#filtering pseudo pawn captures
	if abs(piece) == 6:
		for y, x in Psuedo_moves:
			pcode = gamestate[y][x]
			if (y, x) in moves:
				if x == col and pcode != 0:
					moves.pop(moves.index((y, x)))
				elif abs(y-row) == abs(x-col) and pcode == 0:
					moves.pop(moves.index((y, x)))
						
	# adding castling for kings
	elif piece == 1:
		if not white_king_moved:
			if not right_w_rook_moved and not castle_obstruction((row, col), 7, 6):
				moves.append((7, 6))
			if not left_w_rook_moved and not castle_obstruction((row, col), 7, 2):
				moves.append((7, 2))
				
	elif piece == -1:
		if not black_king_moved:
			if not right_B_rook_moved and not castle_obstruction((row, col), 0, 6):
				moves.append((0, 6))
			if not left_B_rook_moved and not castle_obstruction((row, col), 0, 2):
				moves.append((0, 2))
				
	elif abs(piece) != 4: # if piece is sliding
	
		blocked_paths = {}#contains the blocked directions
		
		for y, x in blockers:
			dx = x-col
			dy = y-row
			dist = max(abs(dx), abs(dy))
			dir = (dy//abs(dy) if dy != 0 else 0, dx//abs(dx) if dx != 0 else 0)
			if dir in blocked_paths:
				if blocked_paths[dir] > dist:
						blocked_paths[dir] = dist
			else:
				blocked_paths[dir] = dist
			
		for y, x in captures:
			dx = x-col
			dy = y-row
			dir = (dy//abs(dy) if dy != 0 else 0, dx//abs(dx) if dx != 0 else 0)
			dist = max(abs(dx), abs(dy)) + 1#offseting the blocker one step further because its a capturable piece
			if dir in blocked_paths:
				if blocked_paths[dir] > dist:
						blocked_paths[dir] = dist
			else:
				blocked_paths[dir] = dist

# Removing blocked squares from possible moves
		for y, x in Psuedo_moves:
			dx = x-col
			dy = y-row
			dir = (dy//abs(dy) if dy != 0 else 0, dx//abs(dx) if dx != 0 else 0)
			dist = max(abs(dx), abs(dy))
			if dir in blocked_paths.keys():
				if dist >= blocked_paths[dir]:
					if (y, x) in moves:
						moves.remove((y, x))
							
	# filtering moves that cause the king to be in check or leave it in check
	filtered_moves = []
	for move in moves:
		state,_= make_move(gamestate, ((row,col),move), piece)
		if not kingincheck(state, turn):
			filtered_moves.append(move)
	moves = filtered_moves
	
	return moves
					
	

def make_move(state, move, selected_piece, check_promotion = False):
	global enpasantable
	castled = False
	row, col = move[0][0], move[0][1]
	x, y = move[1][1], move[1][0]
	temp_state = [r[:] for r in state]
	
	if abs(selected_piece) == 1 and abs(x-col) > 1 and y == row:
		temp_state[row][col] = 0
		temp_state[y][x] = selected_piece
		temp_state[y][x -2 if x<col else x+1] = 0
		temp_state[y][x +1 if x<col else x-1] = 5*turn
		castled = True
		
		
	elif abs(selected_piece) == 6 and (y == 0 or y == 7) and check_promotion:
			if abs(y - row) == 2:
				enpasantable = (y, x)
			temp_state[y][x] = promote()
			temp_state[row][col] = 0
					
	else:
		temp_state[y][x] = selected_piece
		temp_state[row][col] = 0
		
	return (temp_state, castled)
	
	
def promote():
	running = True
	selected_piece = None
	codes = [2 ,3, 4, 5] if turn == 1 else [-2, -3, -4, -5]
	height = tilesize+10
	width = tilesize*4 + 20
	y = voffset - height - 10 if turn == 1 else voffset + 8*tilesize + 10
	left = screen.get_width()//2 - width//2
	
	pg.draw.rect(screen, "white", (left, y, width, height))
		
	for code in codes:
		piece= pieces[str(code)] if turn == 1 else pg.transform.rotate(pieces[str(code)], 180)
		num= abs(code)-2
		piece_rect = piece.get_rect(center = (left + num*tilesize + tilesize//2 + 10, y + 5 + tilesize//2))
		screen.blit(piece, piece_rect)
			
	pg.display.update()
	
	while running:
		mx ,my = pg.mouse.get_pos()
		events = pg.event.get()
		for event in events:
			if event.type == pg.FINGERDOWN:
				if my > y and my < y + height:
					if mx > left and mx < left + width:
						selected_piece = codes[(mx - left -10) // tilesize]
						running = False
					
	return selected_piece
	

def show_moves(xoffset = 0):
	doffset = (screen.get_width()-len(move_record)*100)
	xoffset = xoffset + abs(doffset) if doffset<0 else xoffset
	for index in range(len(move_record)):
		record = move_record[index]
		piece = record[0]
		move = record[1]
		
		text = font.render(f'{"W" if index%2 == 0 else "B"}{piece} {coloumns[move[1]]}{8-move[0]}', True, "white")
		text_rect = text.get_rect(topleft = (movetextx + index*100 - xoffset, movetexty))
		screen.blit(text, text_rect)



def add_index_numbers():
	#adding index numbers
	boxsize = tilesize
	for i in range(8):
		text = font2.render(f'{8-i}' ,True, "black")
		text_rect = text.get_rect(bottomleft = (2, voffset+i*boxsize+ boxsize))
		screen.blit(text, text_rect)
		
		text = font2.render(f'{coloumns[i]}' ,True, "black")
		text_rect = text.get_rect(bottomright= (i*boxsize -2 + boxsize, voffset + boxsize*8 ))
		screen.blit(text, text_rect)

				
		
def reset():
	global tilesize, voffset, turn, coloumns, possible_moves, move_count, white_checks, black_checks, selection, var_king_pos, const_king_pos, king_in_check, move_record, gamestate, moveoffset
	
	tilesize = screen.get_width()//8
	voffset = screen.get_height()/2 - tilesize*4
	turn = 1
	coloumns = ["a","b","c","d","e","f","g","h"]
	possible_moves = []	# global variable to keep track of possible moves of the selected piece

	
	# Keep these None
	selection = None
	var_king_pos= None
	const_king_pos = None
	king_in_check = None
	#_______________________
	
	# Keep these False
	white_king_moved = False
	black_king_moved = False
	right_w_rook_moved = False
	left_w_rook_moved = False
	right_B_rook_moved = False
	left_B_rook_moved = False
	
	move_record = []
	gamestate = [
              [-5,-4,-3,-2,-1,-3,-4,-5],
              [-6,-6,-6,-6,-6,-6,-6,-6],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0],
              [6, 6, 6, 6, 6, 6, 6, 6],
              [5, 4, 3, 2, 1, 3, 4, 5]
              ]
	moveoffset = 0
	


def detect_check_mate():
	pg.display.update()
	all_possibilities = all_moves(gamestate, turn)
	if len(all_possibilities) == 0:
			# Restart timer
		for i in range(5):
			draw_chess_board(gamestate)
			text = endfont.render('Checkmate' if king_in_check else "Statemate",True, "red" if king_in_check else "grey")
			text_rect = text.get_rect(center =(screen.get_width()//2, screen.get_height()//2))
			screen.blit(text, text_rect)
			text = endfont2.render(f'Restarting in {5-i}',True, "black")
			text_rect = text.get_rect(center =(screen.get_width()//2, screen.get_height()//2 + 100))
			screen.blit(text, text_rect)
			pg.display.update()
			sleep(1)
		reset()


def all_moves(state, turn):
	allmoves = []
	for row in range(8):
		for col in range(8):
			piece = gamestate[row][col]
			if piece/turn > 0:
				moves = calculate_possible_moves(row, col, piece)
				for move in moves:
					structured_move = ((row, col),(move[0],move[1]))
					target = state[move[0]][move[1]]
					allmoves.append((piece, structured_move))
	
	return allmoves

def evaluate(state):
	white_value = 0
	black_value = 0
	evalmatrices = evalmats
	for row in range(8):
		for col in range(8):
			piece = state[row][col]
			if piece < 0:
				black_value += evalmatrices[abs(piece)][7-row][7-col]
			elif piece > 0:
				white_value += evalmatrices[piece][row][col]
	return white_value-black_value



#_________MAIN BOT FUNCTIONS__________			

def minimax(state, depth, alpha, beta, maximizing_player):
    # Base case: reached the depth limit or game over
    if depth == 0:
        return evaluate(state)
    
    if maximizing_player:
        max_eval = -inf
        moves = all_moves(state, 1)
        
        # If no moves are possible, it's either checkmate or stalemate
        if not moves:
            return -9999 if kingincheck(state, 1) else 0

        for piece, move in moves:
            row = move[0][0]
            col = move[0][1]
            x = move[1][1]
            y = move[1][0]
            pcode = state[y][x]
            castled = False
            if abs(piece) == 1 and abs(x-col) > 1 and y == row:
            	original_pcode2 = state[y][x -2 if x<col else x+1]
            	original_pcode3 = state[y][x +1 if x<col else x-1]
            	castled = True
            	state[row][col] = 0
            	state[y][x] = piece
            	state[y][x -2 if x<col else x+1] = 0
            	state[y][x +1 if x<col else x-1] = 5
            else:
            	state[row][col] = 0
            	state[y][x] = piece
            
            eval = minimax(state, depth - 1, alpha, beta, False)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            # Alpha-Beta Pruning
            if beta <= alpha:
                break
            
            state[row][col] = piece
            state[y][x] = pcode
            if castled:
            	state[y][x -2 if x<col else x+1] = original_pcode2
            	state[y][x +1 if x<col else x-1] = original_pcode3
            
 
        return max_eval
        
    else: # Minimizing player (Black)
        min_eval = inf
        moves = all_moves(state, -1)
        
        if not moves:
            return 9999 if kingincheck(state, -1) else 0

        for piece, move in moves:
            row = move[0][0]
            col = move[0][1]
            x = move[1][1]
            y = move[1][0]
            pcode = state[y][x]
            
            castled = False
            if abs(piece) == 1 and abs(x-col) > 1 and y == row:
            	original_pcode2 = state[y][x -2 if x<col else x+1]
            	original_pcode3 = state[y][x +1 if x<col else x-1]
            	castled = True
            	state[row][col] = 0
            	state[y][x] = piece
            	state[y][x -2 if x<col else x+1] = 0
            	state[y][x +1 if x<col else x-1] = -5
            else:
            	state[row][col] = 0
            	state[y][x] = piece
            
            eval = minimax(state, depth - 1, alpha, beta, True)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            # Alpha-Beta Pruning
            if beta <= alpha:
                break
            
            state[row][col] = piece
            state[y][x] = pcode
            if castled:
            	state[y][x -2 if x<col else x+1] = original_pcode2
            	state[y][x +1 if x<col else x-1] = original_pcode3	
			
        return min_eval
        

def make_bot_move(state):
    best_move = None
    depth = 4
    
    if turn == 1: # If bot is playing White (Maximizing)
        best_val = -inf
        moves = all_moves(state, 1)
        for piece, move in moves:
            
            new_state, _ = make_move(state, move, piece)
            move_val = minimax(new_state, depth - 1, -inf, inf, False)
            if move_val > best_val:
                best_val = move_val
                best_move = move
                
    else: # If bot is playing Black (Minimizing)
        best_val = inf
        moves = all_moves(state, -1)
        for piece, move in moves:
        
             new_state, _ = make_move(state, move, piece)
             move_val = minimax(new_state, depth - 1, -inf, inf, True)
             if move_val < best_val:
                best_val = move_val
                best_move = move
                
    return best_move 
    
#_______________________________________
			

moveoffset = 0
running = True
while running:
	mx, my = pg.mouse.get_pos()
	events = pg.event.get()
	for event in events:
		if event.type == pg.QUIT:
			pg.quit()
		if event.type == pg.FINGERDOWN or event.type == pg.MOUSEBUTTONDOWN:
			if turn == 1:
				handle_click(mx, my)
			elif turn == -1 and mode != "robot":
				handle_click(mx, my)
			touchpos = mx
		if event.type == pg.FINGERMOTION or event.type == pg.MOUSEMOTION:
			if movetexty +moves_text_size+10> my > movetexty-10:
				newtouchpos = mx
				moveoffset=touchpos - newtouchpos
				
	
	screen.fill((43,42,41))
	draw_chess_board(gamestate)
	show_moves(moveoffset)
	
	if turn == -1 and mode == "robot":
		pg.display.update()
		move = make_bot_move(gamestate)
		if move:
			row = move[0][0]
			col = move[0][1]
			x = move[1][1] * tilesize
			y = move[1][0] * tilesize + voffset
			selection = (col, row)
			handle_click(x, y)
		
					
	pg.display.update()