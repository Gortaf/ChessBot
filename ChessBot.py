# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 05:15:48 2021

@author: Gortaf
"""

import os
import discord
import asyncio
import time
import datetime
import random
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from dotenv import load_dotenv
from discord.ext import commands

from ChessPieces import Pawn, Rook, Knight, Bishop, Queen, King

load_dotenv()

token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
client =commands.Bot(command_prefix = "$", intents = intents)
client.remove_command('help')

# =============================================================================
# Initialise some variables & global data at launch
# =============================================================================
@client.event
async def on_ready():
	client.startTime = time.time()
	client.startDateTime = datetime.datetime.now()
	
	print(f"Online as {client.user.name} at {client.startDateTime}")
	client.serv_dic = {}
	client.duel_ids = {}
	client.spectat_msgs = {}
	
	await client.change_presence(activity = discord.Game("$duel @someone"))
	
	# A dictionnary of all the bot's custom emotes (correspondes to the pieces)
	# 0 for white, 1 for black pieces
	client.emotes = {
		"pawn": ["<:pawn_white:798140768379863090>","<:pawn_black:798140768379863060>"],
		"rook": ["<:rook_white:798140768166084609>","<:rook_black:798140768438583296>"],
		"bishop": ["<:bishop_white:798140767801311243>","<:bishop_black:798140768102514699>"],
		"knight": ["<:knight_white:798140768383926272>","<:knight_black:798140768204095508>"],
		"queen": ["<:queen_white:798140768476725278>","<:queen_black:798140768442384404>"],
		"king": ["<:king_white:798140768165429278>","<:king_black:798140768187449395>"]
		}

# =============================================================================
# The coroutine that runs the actual duel
# =============================================================================
async def game_on(ctx,duel_channel, duelist, victim, duel_msg):
	
	def command_check(message):
		return message.channel == duel_channel and message.author != client.user
	
	async def endgame():
		await asyncio.sleep(60)
		await duel_channel.delete()
	
	async def get_piece(idt):
		if white == turnset:
			for piece in white_pieces:
				if piece.idt.lower() == idt.lower():
					return piece
			else:
				return None
			
		elif black == turnset:
			for piece in black_pieces:
				if piece.idt.lower() == idt.lower():
					return piece
				
			else:
				return None
	
	board = [[{"color": None, "piece": None} for i in range(8)] for i in range(8)]
	
	# Filling the board's color
	col = "W"
	for line in board:
		for cell in line:
			cell["color"] = col
			
			# Swap the next cell color
			if col == "W":
				col = "B"
			elif col == "B":
				col = "W"
	
	# Filling the board with pieces
	# White Pawns
	for x in range(len(board[1])):
		board[1][x]["piece"] = Pawn("W",x,1,f"P{x+1}")
		
	# Black Pawns
	for x in range(len(board[6])):
		board[6][x]["piece"] = Pawn("B",x,6,f"P{x+1}")
		
	# Rooks
	board[0][0]["piece"] = Rook("W",0,0,"R1")
	board[0][7]["piece"] = Rook("W",7,0,"R2")
	board[7][0]["piece"] = Rook("B",0,7,"R1")
	board[7][7]["piece"] = Rook("B",7,7,"R2")
	
	# Knights
	board[0][1]["piece"] = Knight("W",1,0,"K1")
	board[0][6]["piece"] = Knight("W",6,0,"K2")
	board[7][1]["piece"] = Knight("B",1,7,"K1")
	board[7][6]["piece"] = Knight("B",6,7,"K2")
		
	# Bishops
	board[0][2]["piece"] = Bishop("W",2,0,"B1")
	board[0][5]["piece"] = Bishop("W",5,0,"B2")
	board[7][2]["piece"] = Bishop("B",2,7,"B1")
	board[7][5]["piece"] = Bishop("B",5,7,"B2")
	
	# Queens
	board[0][3]["piece"] = Queen("W",3,0,"Q")
	board[7][3]["piece"] = Queen("B",3,7,"Q")
	
	# Kings
	board[0][4]["piece"] = King("W",4,0,"K")
	white_king = board[0][4]["piece"]
	board[7][4]["piece"] = King("B",4,7,"K")
	black_king = board[7][4]["piece"]
	
	# Randomly decides who is white and who is black
	if random.randint(0,1):
		white = duelist
		black = victim
	
	else:
		white = victim
		black = duelist
	
	# Initialising stuff
	turnset = white
	winner = None		
	old_x = None
	old_y = None
	move_x = None
	move_y = None
	old_piece = None
	castled_rook = False
	white_queen_nb= 1
	black_queen_nb = 1
	white_taken = {"pawn":0,"rook":0,"bishop":0,"knight":0,"queen":0,"king":0}
	black_taken = {"pawn":0,"rook":0,"bishop":0,"knight":0,"queen":0,"king":0}
	
	
	msg = f"Here's how you play chess with {ctx.guild.me.mention}:\n```\n"
	msg += "When it's your turn, move your piece with:  $move [piece name] [destination coordinates]\n"
	msg += "For exemple, to move the 3rd Pawn (P3) to the f4 cell, use $move P3 f4\n(note that you can use $m instead of $move, and that the piece's names and positions aren't caps sensitive)\n\n"
	msg += "Castling is done with $castle [castling rook].\nFor exemple, to castle using the R1 rook, use $castle R1\n\n"
	msg += "You can concede anytime with $concede, even if it's not your turn. You can also ask your opponent to declare the game a draw with $draw (they will have to accept).\nTo win, you have to take the king (not just checkmate it)."
	msg += "\n\nWhile I will not register illegal moves, I also won't stop you from putting your king in danger :)\n\n"
	msg += "If someone doesn't take their turn within 10 minutes, the game times out, and the other player is declared winner.\n```"
	await duel_channel.send(msg)
	
	while True:  # Turns will continue until a King is taken
	
		if winner == None:
			
			# Constructing the list of taken pieces as emotes
			white_toadd = ""
			black_toadd = ""
			for taken_piece,nb in white_taken.items():
				if nb == 0:
					continue
				white_toadd += f"  {client.emotes[taken_piece][1]}\\*{nb}"
			
			for taken_piece,nb in black_taken.items():
				if nb == 0:
					continue
				black_toadd += f"  {client.emotes[taken_piece][0]}\\*{nb}"
			
			turn_msg = f"**White:** {white.name}  -{white_toadd}\n**Black:** {black.name}  -{black_toadd}"
			
			if old_x != None and old_y != None:
				turn_msg+=f"\nLast turn: **{old_piece.idt}** moved (*{chr(old_x+97)}{old_y+1}* → *{chr(move_x+97)}{move_y+1}*)"
				if castled_rook:
					castled_rook = False
					turn_msg+=" **-castling-**"
			
			turn_msg += f"\nWaiting for a play from: {turnset.mention}"
		else:
			turn_msg = f"**White:** {white.name}\n**Black:** {black.name}\n**{winner.name} WINS!**"
		
		# Checks if either king is in check
		if winner == None:
			white_check = white_king.is_in_check(board)
			black_check = black_king.is_in_check(board)
		
		if white_check[0]:
			turn_msg += "\n**⚠️---THE WHITE KING IS IN CHECK---⚠️**\n"
		if black_check[0]:
			turn_msg += "\n**⚠️---THE BLACK KING IS IN CHECK---⚠️**\n"
		
		# Initalising the list of pieces of both players
		white_pieces = []
		black_pieces = []
		
		# Using PIL to construct the chessboard
		board_img = Image.open("Ressources/ChessBoard.png")
		start_x = 22
		start_y = 1200
		cell_size = 162
		offset = cell_size//4
		
		# Loading the font for the pieces ID
		font = ImageFont.truetype("Ressources/F25_font.ttf", 31)
		draw = ImageDraw.Draw(board_img)
		
		for i in range(8):
			for j in range(8):
				
				# Calculating this cell's absolute coordinates (in px)
				point_coords = (start_x + j*cell_size+offset, start_y- i*cell_size-offset)
				piece = board[i][j]["piece"]
				
				# Skipping empty cells
				if piece == None:
					continue
				else:
					
					# putting the piece into the piece list
					if piece.color == "W":
						white_pieces.append(piece)
					elif piece.color == "B":
						black_pieces.append(piece)
					
					# Getting the corresponding piece file
					piece_filepath = "Ressources/Pieces/"+piece.file
					piece_img = Image.open(piece_filepath)
				
				
				# pasting the piece into the board
				board_img.paste(piece_img,point_coords,piece_img)
				piece_img.close()
				
				# Adding the text
				point_coords = list(point_coords)
				point_coords[0] = point_coords[0] - (offset//3)
				point_coords = tuple(point_coords)
				
				# The text is black, or red if the piece is threatening a king
				color = "black"
				if piece in white_check[1] or piece in black_check[1]:
					color = "red"
				
				draw.text(point_coords,piece.idt,font=font,fill=color)	
		
		# If there was a move last turn, draw a line representing it
		if old_x != None and old_y != None:
			old_px = (start_x+old_x*cell_size+int(2.6*offset),start_y-old_y*cell_size+(offset//1.1))
			new_px = (start_x+move_x*cell_size+int(2.6*offset),start_y-move_y*cell_size+(offset//1.1))
			
			draw.line(old_px + new_px, fill = "red", width=5)
		
		# Saving the image
		randname = random.randint(100,9999999)
		board_img.save(str(randname)+".png")
		board_img.close()
		
		# Sending updated board & updated turn message, then deleting the image
		turn_sent = await duel_channel.send(content=turn_msg, file=discord.File(str(randname)+".png"))
		os.remove(str(randname)+".png")
		
		if winner != None:
			await duel_channel.send(f"{winner.name} wins the game!\n(This channel will be deleted in 1 minute)")
			await endgame()	
			return
		
		end_turn = True
		while True and end_turn:
			
			try:
				reply = await client.wait_for("message", check=command_check, timeout = 600)
		
			except asyncio.TimeoutError:
				await duel_channel.send(f"{turnset.mention} didn't play in time (10min). Game canceled.\n(This channel will be deleted in 1 minute)")
				await endgame()
				return
			
			
			from_player = reply.author == white or reply.author == black
			if "$concede" in reply.content and from_player:
				await duel_channel.send(f"**{reply.author.name} has conceded!**\n(This channel will be deleted in 1 minute)")
				await endgame()
				return
			
			if "$draw" == reply.content and from_player:
				await duel_channel.send(f"{reply.author.name} wants to declare this game a draw.\nType $accept to accept\nType $refuse to refuse")
				
				# Waiting for an answer
				while True:
					try:
						reply_draw = await client.wait_for("message", check=command_check, timeout = 180)
						
					except asyncio.TimeoutError: 
						duel_channel.send("No reply was given in time. Draw request canceled.")
						break
					
					# The draw request was accepted. Ending the match
					if reply_draw.content == "$accept":
						await duel_channel.send("**This match has been declared a draw!**\n(This channel will be deleted in 1 minute)")
						await endgame()
						return
					
					elif reply_draw.content == "$refuse":
						await duel_channel.send("Draw request refused. The match continues!")
						break
					
					else:
						tmp = await reply_draw.channel.fetch_message(reply_draw.id)
						await tmp.add_reaction("💬")
						await tmp.delete(delay = 15)
			
			# If there is no commands, then this is a chat message (15sec lifespan)
			mv_cmd = "$move" not in reply.content and "$m " not in reply.content
			if mv_cmd and "$castle" not in reply.content and "$draw" not in reply.content:
				tmp = await reply.channel.fetch_message(reply.id)
				await tmp.add_reaction("💬")
				await tmp.delete(delay = 15)
				continue
			
			if reply.author == turnset:	
				elements = reply.content.split(" ")
				
				# Easy way to avoid problems between commands argument number
				if len(elements)<3:
					elements.append(None)
					elements.append(None)
				
				# Finding the piece in question (if it exists)
				piece = await get_piece(elements[1])
				if piece == None:
					tmp = await reply.channel.fetch_message(reply.id)
					await tmp.add_reaction("👎")
					await tmp.delete(delay =2)
					continue
				
				if "$castle" in reply.content:
					
					# Only Rooks can castle
					if type(piece) == Rook:
						king = await get_piece("K")							
						
						# Can't castle if K or R has moved
						if piece.can_castle and king.can_castle:
							castle_check = piece.castling(king.x, king.y, board)
							
							# Can't castle if there's anything in the path
							# Also can't castle if king is in check
							if castle_check[0] and not king.in_check:
								
								# Results depend on the type of castling
								if castle_check[1] == "big":
									k_mod = -2
									r_mod = 3
									
								elif castle_check[1] == "small":
									k_mod = 2
									r_mod = -2
									
								# Moving the Rook
								old_x = piece.x
								old_y = piece.y
								board[piece.y][piece.x+r_mod]["piece"] = piece
								board[old_y][old_x]["piece"] = None
								piece.x = piece.x + r_mod
								piece.can_castle = False
								
								# Moving the king
								old_x = king.x
								old_y = king.y
								board[king.y][king.x+k_mod]["piece"] = king
								board[old_y][old_x]["piece"] = None
								king.x = king.x + k_mod
								king.can_castle = False
								
								# Updates the move coords for the movement line
								move_x = king.x
								move_y = king.y
								old_piece = king
								castled_rook = True
								
								# This turn ends								
								end_turn = False
								continue
										
					# Castling failed
					tmp = await reply.channel.fetch_message(reply.id)
					await tmp.add_reaction("👎")
					await tmp.delete(delay =2)
					continue
								
				
				try:
					move_x = ord(elements[2][0].lower())-97
					move_y = int(elements[2][1])-1
				
				except Exception as e:
					tmp = await reply.channel.fetch_message(reply.id)
					await tmp.add_reaction("👎")
					await tmp.delete(delay =2)
					continue
				
				old_x = piece.x
				old_y = piece.y
				
				# Attempts to move the piece
				if piece.move(move_x, move_y, board):
					
					old_piece = piece
					cur_piece = board[move_y][move_x]["piece"]
					
					if cur_piece != None:
						if turnset == white:
							white_taken[cur_piece.piece_type] += 1
							
						else:
							black_taken[cur_piece.piece_type] += 1
						
					
					# If a king is taken, the game ends
					if board[move_y][move_x]["piece"] != None and board[move_y][move_x]["piece"].idt == "K":
						winner = turnset
					
					board[move_y][move_x]["piece"] = piece
					board[old_y][old_x]["piece"] = None
					
					# If a pawn gets to the end of the board, it becomes a queen
					if "P" in piece.idt and ((piece.y == 0 and piece.color == "B") or (piece.y == 7 and piece.color == "W")):
						
						# Avoids new queens having the same id
						if turnset == white:
							to_add = white_queen_nb
							white_queen_nb +=1
							
						else:
							to_add = black_queen_nb
							black_queen_nb +=1
						
						board[move_y][move_x]["piece"] = Queen(piece.color,piece.x,piece.y,f"Q{to_add}")
						
					
					break
					
				else: 
					tmp = await reply.channel.fetch_message(reply.id)
					await tmp.add_reaction("👎")
					await tmp.delete(delay =2)
					continue
			else:
				tmp = await reply.channel.fetch_message(reply.id)
				await tmp.add_reaction("🤨")
				await tmp.delete(delay =2)
				continue
				
		# Deleting the messages
		tmp = await reply.channel.fetch_message(reply.id)
		await tmp.delete()
		tmp = await turn_sent.channel.fetch_message(turn_sent.id)
		await tmp.delete()
		
		# next turn
		if turnset == white:
			turnset = black
		elif turnset == black:
			turnset = white
		
		end_turn = False
		
		
		
# =============================================================================
# The $duel command is used to start a game
# =============================================================================
@client.command(pass_context=True, aliases = ["game","challenge"])
async def duel(ctx, victim_str=None, *args):
	
	# Called to verify if a message is a reply to a duel request
	def accept_check(message):
		return (message.content == "$accept" or message.content == "$refuse") and message.author == victim
	
	if not victim_str:
		await ctx.send("You need to specify the user you wish to duel.")
		return
	
	if len(ctx.message.mentions) == 0:
		await ctx.send(f"Cannot find user \"{victim_str.strip('@')}\".")
		return
	
	# The User objects of the 2 participants
	duelist = ctx.author
	victim = ctx.message.mentions[0]
	
	if victim == ctx.author:
		await ctx.send("You can't challenge yourself...")
		return
	
	if victim == client.user:
		await ctx.send("You cannot challenge me (for your own good).")
		return
	
	await ctx.send(f"{duelist.mention} has challenged you, {victim.mention}, in a game of chess. Will you accept the duel?\n\nType \"$accept\" to accept the duel.\nType \"$refuse\" to refuse the duel.")
	
	try:
		reply = await client.wait_for("message", check=accept_check, timeout = 600)
	
	except asyncio.TimeoutError:
		await ctx.send(f"{duelist.mention}'s challenge request has expired. {victim.mention} didn't accept in time.")
		return
	
	if reply.content == "$refuse":
		await ctx.send(f"{victim.mention} has refused {duelist.mention}'s challenge.")
		return
	
	# If we're here, both parties are ready for the duel
	# Generating duel ID
	duel_id = random.randint(10000, 99999)
	while duel_id in client.duel_ids.keys():
		duel_id = random.randint(10000, 99999)
		
	client.duel_ids[duel_id] = ctx.guild.id
	
	# Creating duel channel
	overwrites = {
		ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
		duelist: discord.PermissionOverwrite(read_messages=True, send_messages=True),
		victim:  discord.PermissionOverwrite(read_messages=True, send_messages=True)
		
		}
	
	if "public" in args:
		overwrites[ctx.guild.default_role] = discord.PermissionOverwrite(send_messages=False)
		
	else:
		overwrites[ctx.guild.default_role] = discord.PermissionOverwrite(read_messages=False)
	
	duel_channel = await ctx.guild.create_text_channel(f"chess-{duel_id}", overwrites=overwrites, category=ctx.channel.category)
	
	# Adding duel entry
	if ctx.guild.id not in client.serv_dic.keys():
		client.serv_dic[ctx.guild.id] = {}
	
	client.serv_dic[ctx.guild.id][duel_id] = {
		"duel_channel": duel_channel,
		"duelist": duelist,
		"victim": victim,
		"start_time": datetime.datetime.now()
		}
	
	# Sending the duel message
	msg = f"{victim.mention} has accepted {duelist.mention}'s duel!\nThe duel will take place in {duel_channel.mention}."
	if "private" not in args and "public" not in args:
		msg += "\n\n Everyone can react with 👁️ to this message to gain access to the duel channel as a spectator."
	duel_msg = await ctx.send(msg)
	
	# If the game is private, no spectating is allowed
	if "private" not in args and "public" not in args:
		await duel_msg.add_reaction("👁️")
	
		# Storing the message to allow spectators to join
		client.spectat_msgs[duel_msg.id] = duel_channel
	
	await game_on(ctx, duel_channel, duelist, victim, duel_msg)
	del client.spectat_msgs[duel_msg.id]
	
# =============================================================================
# Fake commands (avoids raising useless errors)
# =============================================================================
@client.command(pass_context=False)
async def accept(ctx):
	pass
@client.command(pass_context=False)
async def refuse(ctx):
	pass
@client.command(pass_context=False)
async def move(ctx):
	pass
@client.command(pass_context=False)
async def m(ctx):
	pass
@client.command(pass_context=False)
async def castle(ctx):
	pass
@client.command(pass_context=False)
async def draw(ctx):
	pass
@client.command(pass_context=False)
async def concede(ctx):
	pass

# =============================================================================
# Reads reaction for spectator mode
# =============================================================================
@client.event
async def on_raw_reaction_add(payload):
	
	if payload.message_id in client.spectat_msgs.keys() and payload.emoji.name == "👁️" and payload.user_id != client.user.id:
		await client.spectat_msgs[payload.message_id].set_permissions(payload.member, read_messages=True, send_messages=False)

@client.event
async def on_raw_reaction_remove(payload):
	
	if payload.message_id in client.spectat_msgs.keys() and payload.emoji.name == "👁️" and payload.user_id != client.user.id:
		await client.spectat_msgs[payload.message_id].set_permissions(payload.member, read_messages=False, send_messages=False)

client.run(token)

