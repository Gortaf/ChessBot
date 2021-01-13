# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 22:35:49 2021

@author: Nicolas
"""

class ChessPiece:
	
	def __init__(self, color, x, y, idt): 
		self.color = color
		self.x = x  # Always use board[y][x]
		self.y = y
		self.idt =idt
		if color == "W":
			self.suf = "white"
		elif color == "B":
			self.suf = "black"
		
class Pawn(ChessPiece):
	
	def __init__(self, color, x, y, idt):
		super().__init__(color, x, y, idt)
		self.piece_type = "pawn"
		self.file = "pawn_"+self.suf+".png"
		self.can_double_move = True
	
	# Moves the piece
	def move(self, new_x, new_y, board, check_move = False):
		
		# Check for out of bounds
		if new_x < 0 or new_x > 7 or new_y < 0 and new_x > 7:
			return False
		
		# Can't move to where the piece already is
		if new_x == self.x and new_y == self.y:
			return False
		
		# Common checks
		same_col = (new_x == self.x)
		
		if self.color == "W":
			
			# Specific checks for white pawns
			good_mov = (new_y == self.y+1 or (new_y == self.y+2 and self.can_double_move))
			empty_dest = board[new_y][new_x]["piece"] == None
			
			atk_left = board[new_y][new_x]["piece"] != None and board[new_y][new_x]["piece"].color == "B" and new_x == self.x-1 and new_y == self.y+1
			atk_right = board[new_y][new_x]["piece"] != None and board[new_y][new_x]["piece"].color == "B" and new_x == self.x+1 and new_y == self.y+1
			
		elif self.color == "B":
			
			# Specific checks for black pawns
			good_mov = (new_y == self.y-1 or (new_y == self.y-2 and self.can_double_move))
			empty_dest = board[new_y][new_x]["piece"] == None
			atk_left = board[new_y][new_x]["piece"] != None and board[new_y][new_x]["piece"].color == "W" and new_x == self.x-1 and new_y == self.y-1
			atk_right = board[new_y][new_x]["piece"] != None and board[new_y][new_x]["piece"].color == "W" and new_x == self.x+1 and new_y == self.y-1
			
		# Normal movement
		if same_col and good_mov and empty_dest:
			if not check_move:  # Truly move only if this wasn't a test
				self.x = new_x
				self.y = new_y
				
			self.can_double_move = False
			return True
	
		# Attacking movement
		if atk_right or atk_left:
			if not check_move:
				self.x = new_x
				self.y = new_y
				
			self.can_double_move = False
			return True
		
		return False

class Rook(ChessPiece):
	
	def __init__(self, color, x, y, idt):
		super().__init__(color, x, y, idt)
		self.piece_type = "rook"
		self.file = "rook_"+self.suf+".png"
		self.can_castle = True
		
	def move(self, new_x, new_y, board, check_move = False):
		
		# Check for out of bounds
		if new_x < 0 or new_x > 7 or new_y < 0 and new_x > 7:
			return False
		
		# Can't move to where the piece already is
		if new_x == self.x and new_y == self.y:
			return False
		
		# No diagonal movement for the rook
		if new_x != self.x and new_y != self.y:
			return False
		
		# Checking that the new cell doesn't have an allied piece
		new_cell_piece = board[new_y][new_x]["piece"]
		if new_cell_piece == None:
			pass
		elif new_cell_piece.color == self.color:
			return False
		
		# Vertical movement
		if new_x == self.x:
			
			# Checking if path is interupted
			scan_start = min(self.y,new_y)+1
			scan_end = max(self.y,new_y)
			for tmp_y in range(scan_start, scan_end):
				if board[tmp_y][new_x]["piece"] != None:
					return False
			else:
				if not check_move:  # Only move if this wasn't a test
					self.x = new_x
					self.y = new_y
					
				self.can_castle = False
				return True
			
		# Horizontal movement
		if new_y == self.y:
			
			# Checking if path is interupted
			scan_start = min(self.x,new_x)+1
			scan_end = max(self.x,new_x)
			for tmp_x in range(scan_start, scan_end):
				if board[new_y][tmp_x]["piece"] != None:
					return False
			else:
				if not check_move:
					self.x = new_x
					self.y = new_y
					
				self.can_castle = False
				return True
		
		return False
	
	# Called to attempt castling with this rook
	def castling(self, king_x, king_y, board):
		
		# can_castle is checked in main to also check the King's attribute
		# Finds out which rook is concerned (this is kinda meh)
		if self.x == 0:  # Top left rook
			to_iter = range(1,4)
			castle_type = "big"
			
		elif self.x == 7:  # Top right rook
			to_iter = range(5,7)
			castle_type = "small"
			
		for i in to_iter:
			if board[king_y][i]["piece"]!=None:
				return (False, None)
		else:
			return (True, castle_type)
	
class Bishop(ChessPiece):
	
	def __init__(self, color, x, y, idt):
		super().__init__(color, x, y, idt)
		self.piece_type = "bishop"
		self.file = "bishop_"+self.suf+".png"
		
	def move(self, new_x, new_y, board, check_move = False):
		
		x_dist = abs(new_x-self.x)
		y_dist = abs(new_y-self.y)
		
		# Check for out of bounds
		if new_x < 0 or new_x > 7 or new_y < 0 and new_x > 7:
			return False
		
		# Can't move to where the piece already is
		if new_x == self.x and new_y == self.y:
			return False
		
		# Check if the new cell is on a valid diagonal
		if x_dist != y_dist:
			return False
		
		# Checking that the new cell doesn't have an allied piece
		new_cell_piece = board[new_y][new_x]["piece"]
		if new_cell_piece == None:
			pass
		elif new_cell_piece.color == self.color:
			return False
		
		# Modifiers to check the diagonals
		if new_x > self.x and new_y > self.y:  # Up Right
			xmod = 1
			ymod = 1
		
		elif new_x > self.x and new_y < self.y:  # Down Right
			xmod = 1
			ymod = -1
		
		elif new_x < self.x and new_y > self.y:  # Up Left
			xmod = -1
			ymod = 1
		
		elif new_x < self.x and new_y < self.y:  # Down Left
			xmod = -1
			ymod = -1
		
		xscan = self.x
		yscan = self.y
		for i in range(x_dist-1):  # x_dist == y_dist True at this point
			xscan += xmod
			yscan += ymod
			
			if board[yscan][xscan]["piece"] != None:
				return False
		
		else:
			if not check_move:  # Only move if this wasn't a test
				self.x = new_x
				self.y = new_y
				
			return True
		
class King(ChessPiece):
	
	def __init__(self, color, x, y, idt):
		super().__init__(color, x, y, idt)
		self.piece_type = "king"
		self.file = "king_"+self.suf+".png"
		self.can_castle = True
		self.in_check = False
		
	def move(self, new_x, new_y, board, check_move = False):
		
		x_dist = abs(new_x-self.x)
		y_dist = abs(new_y-self.y)
		
		# Check for out of bounds
		if new_x < 0 or new_x > 7 or new_y < 0 and new_x > 7:
			return False
		
		# Checking that the new cell doesn't have an allied piece
		new_cell_piece = board[new_y][new_x]["piece"]
		if new_cell_piece == None:
			pass
		elif new_cell_piece.color == self.color:
			return False
		
		# Checking the move is within 1 cell of movement
		if not ((x_dist == 1 or y_dist == 1) and x_dist < 2 and y_dist < 2):
			return False
		
		self.can_castle = False
		if not check_move:  # Only move if this wasn't a test
			self.x = new_x
			self.y = new_y
		return True
	
	def is_in_check(self, board):
		
		danger = []  # List of pieces that might check the king
		
		# Checks for knights (8 possible positions)
		for axis in [1,-1]:
			for coords in [(2,1),(2,-1),(-2,1),(-2,-1)]:
				coords = coords[::axis]  # Will invert the mods for 2nd main iter
			
				try:
					to_add = board[self.y+coords[0]][self.x+coords[1]]["piece"]
					if type(to_add) == Knight and to_add.color != self.color:
						danger.append(to_add)
				
				except IndexError:  # Out of bound coordinate
					continue
				
				
		# Horizontal and Vertical rows of the king
		hor = [board[self.y][x]["piece"] for x in range(8)]
		ver = [board[y][self.x]["piece"] for y in range(8)]
				
		
		# Get the first left, right, down & up pieces
		l_piece = None
		for l_piece in hor[:self.x][::-1]:
			if l_piece != None:
				break
		
		r_piece = None
		for r_piece in hor[self.x+1:]:
			if r_piece != None:
				break
			
		d_piece = None
		for d_piece in ver[:self.y][::-1]:
			if d_piece != None:
				break
			
		u_piece = None
		for u_piece in ver[self.y+1:]:
			if u_piece != None:
				break
		
		# Get the first diagonal
		offset = self.x - self.y
		diag = [row[i+offset] for i,row in enumerate(board) if 0 <= i+offset < len(row)]
		
		# Get the first diagonal pieces
		ru_piece = None
		ld_piece = None
		king_passed = False
		for cell in diag:
			
			if cell["piece"] == self:
				king_passed = True
				continue
				
			if not king_passed and cell["piece"] != None:
				ru_piece = cell["piece"]
				continue
			
			if king_passed and cell["piece"] != None:
				ld_piece = cell["piece"]
				continue
		
		# Get the second diagonal
		rev_y = 7 - self.y
		offset = self.x - rev_y
		diag = [row[len(board)-i+offset-1] for i,row in enumerate(board) if 0 <= len(board)-i+offset-1 < len(board)]
		
		# Get the first diagonal pieces
		lu_piece = None
		rd_piece = None
		king_passed = False
		for cell in diag:
			
			if cell["piece"] == self:
				king_passed = True
				continue
				
			if not king_passed and cell["piece"] != None:
				lu_piece = cell["piece"]
				continue
			
			if king_passed and cell["piece"] != None:
				rd_piece = cell["piece"]
				continue
			
		pieces = [l_piece, r_piece, u_piece, d_piece, lu_piece, rd_piece, ru_piece, ld_piece]
		pieces = [tmp for tmp in pieces if tmp != None]
		
		danger += pieces
		true_danger = []  # List of pieces that ACTUALLY check the king
		for to_check in danger:
			
			# Tests to see if movement to the king is possible
			if to_check.move(self.x, self.y, board, check_move = True):
				true_danger.append(to_check)
		
		if len(true_danger) == 0:
			self.in_check = False
			return (False, [])
		else:
			self.in_check = True
			return (True, true_danger)
		
class Knight(ChessPiece):
	
	def __init__(self, color, x, y, idt):
		super().__init__(color, x, y, idt)
		self.piece_type = "knight"
		self.file = "knight_"+self.suf+".png"
	
	def move(self, new_x, new_y, board, check_move = False):
		
		# Check for out of bounds
		if new_x < 0 or new_x > 7 or new_y < 0 and new_x > 7:
			return False
		
		# Checking that the new cell doesn't have an allied piece
		new_cell_piece = board[new_y][new_x]["piece"]
		if new_cell_piece == None:
			pass
		elif new_cell_piece.color == self.color:
			return False
	
		# A knight only has 8 possible moves. It's easier to calculate those
		# first, then simply compare the proposed coordinates.
		# (Not very elegant, but more readable)
		
		# Calculating moves
		moves = []
		
		# Up(2) right & left(1)
		moves.append([self.x-1,self.y+2])
		moves.append([self.x+1,self.y+2])
		
		# Down(2) left & right(1)
		moves.append([self.x-1,self.y-2])
		moves.append([self.x+1,self.y-2])
		
		# Left(2) up & down(1)
		moves.append([self.x-2,self.y-1])
		moves.append([self.x-2,self.y+1])
		
		# Right(2) up & down(1)
		moves.append([self.x+2,self.y-1])
		moves.append([self.x+2,self.y+1])
		
		if [new_x,new_y] in moves:
			
			if not check_move: # Only move if this wasn't a test
				self.x = new_x
				self.y = new_y
				
			return True
		else:
			return False
		
class Queen(ChessPiece):
	
	def __init__(self, color, x, y, idt):
		super().__init__(color, x, y, idt)
		self.piece_type = "queen"
		self.file = "queen_"+self.suf+".png"
		
	def move(self, new_x, new_y, board, check_move = False):
		
		# Check for out of bounds
		if new_x < 0 or new_x > 7 or new_y < 0 and new_x > 7:
			return False
		
		# Can't move to where the piece already is
		if new_x == self.x and new_y == self.y:
			return False
		
		# Checking that the new cell doesn't have an allied piece
		new_cell_piece = board[new_y][new_x]["piece"]
		if new_cell_piece == None:
			pass
		elif new_cell_piece.color == self.color:
			return False
		
		# Vertical movement
		if new_x == self.x:
			
			# Checking if path is interupted
			scan_start = min(self.y,new_y)+1
			scan_end = max(self.y,new_y)
			for tmp_y in range(scan_start, scan_end):
				if board[tmp_y][new_x]["piece"] != None:
					return False
			else:
				if not check_move:  # Only move if this wasn't a test
					self.x = new_x
					self.y = new_y
					
				return True
			
		# Horizontal movement
		if new_y == self.y:
			
			# Checking if path is interupted
			scan_start = min(self.x,new_x)+1
			scan_end = max(self.x,new_x)
			for tmp_x in range(scan_start, scan_end):
				if board[new_y][tmp_x]["piece"] != None:
					return False
			else:
				if not check_move:
					self.x = new_x
					self.y = new_y
					
				return True
		
		# If we're here, then the proposed movement isn't vertical
		# Checking for diagonals
		x_dist = abs(new_x-self.x)
		y_dist = abs(new_y-self.y)		
		
		# Check if the new cell is on a valid diagonal
		if x_dist != y_dist:
			return False
		
		# Modifiers to check the diagonals
		if new_x > self.x and new_y > self.y:  # Up Right
			xmod = 1
			ymod = 1
		
		elif new_x > self.x and new_y < self.y:  # Down Right
			xmod = 1
			ymod = -1
		
		elif new_x < self.x and new_y > self.y:  # Up Left
			xmod = -1
			ymod = 1
		
		elif new_x < self.x and new_y < self.y:  # Down Left
			xmod = -1
			ymod = -1
		
		xscan = self.x
		yscan = self.y
		for i in range(x_dist-1):  # x_dist == y_dist True at this point
			xscan += xmod
			yscan += ymod
			
			if board[yscan][xscan]["piece"] != None:
				return False
		else:
			if not check_move:  # Only move if this wasn't a test
				self.x = new_x
				self.y = new_y
				
			return True
		
		return False