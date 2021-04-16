#!/usr/bin/env python

from manim import *
from manim.utils.color import Colors

# To watch one of these scenes, run the following:
# python --quality m manim -p example_scenes.py SquareToCircle
#
# Use the flag --quality l for a faster rendering at a lower quality.
# Use -s to skip to the end and just save the final frame
# Use the -p to have preview of the animation (or image, if -s was
# used) pop up once done.
# Use -n <number> to skip ahead to the nth animation of a scene.
# Use -r <number> to specify a resolution (for example, -r 1920,1080
# for a 1920x1080 video)


# Not used anymore
# class Trimino(Polygon):
# 	CONFIG = {
# 	  "fill_color" : RED,
# 	  "fill_opacity": 0.8, 
# 	  "name" : None,
# 	  "dim" : 3,
# 	  "target": None
# 	}
# 	def __init__(self, offset=0.1, direcao=0, center=np.array([0,0]), **kwargs):
# 		self.offset=offset
# 		Polygon.__init__(self, [-1+self.offset, -1+self.offset, 0], [1-self.offset, -1+self.offset, 0], [1-self.offset, -self.offset, 0], [-self.offset, -self.offset, 0], [-self.offset, 1-self.offset, 0], [-1+self.offset, 1-self.offset, 0], **kwargs)
# 		self.rotate(direcao*PI/2)
# 		self.shift(center[1]*UP+center[0]*RIGHT)

class Grid(VGroup):
	colors = [YELLOW, PURPLE, TEAL, GREEN_C, ORANGE]

	#creates a grid made of squares pieces
	def __init__(self, order, square_side=1, square_spacing=0, **kwargs):
		VGroup.__init__(self, **kwargs)
		self.missingppiece = np.array([])
		self.order = order
		self.square_side = square_side
		self.square_spacing = square_spacing
		self.size = 2**order
		#Creates a grid of Rectangles (so far, I only used squares, but this may change in the future)
		for i in range(self.size):
			row = VGroup(*[Rectangle(height=square_side, width=square_side, fill_opacity=1, color=WHITE, fill_color=BLACK, stroke_width=1.5) for _ in range(self.size)])
			row.arrange(direction=np.array([1,0,0]), buff=square_spacing)
			self.add(row)
		self.arrange(direction=np.array([0,1,0]), buff=square_spacing)
		self.move_to(ORIGIN)

	def set_missing_piece(self, missingppiece):
		if (missingppiece[0] < 0 or missingppiece[1] < 0 or missingppiece[0] > self.size or missingppiece[1] > self.size):
			raise Exception("Piece out of bounds")

		self[missingppiece[0]][missingppiece[1]].set_fill(YELLOW).scale(0.9)
		self.missingppiece = missingppiece

	#Highlight a Trimino in the grid and plays this in the scene (cena)
	# (i, i) are the coordinate of the center square of the Trimino and (d[0], d[1]) are the relative positions of its other two squares
	# d[0] = vertical change (+1 or -1), d[1]=horizontal change (+1 or -1)
	def tile(self, cena, i, j, d, time=0.5, cor=RED):
		# t = VGroup(self[i+d[0]][j], self[i][j], self[i][j+d[1]])
		# t.scale(0.9)
		# not sure why, but if I add "t.animate.scale(0.9)" inside the list below, it does not work
		# rect.scale(<scalefactor>, about_edge=UP
		offset_factor=0.9
		cena.play(
			self[i][j].animate.set_fill(cor).scale(offset_factor), 
			self[i+d[0]][j].animate.stretch_to_fit_width(offset_factor*self.square_side).shift(d[0]*DOWN*(self.square_spacing+((1-offset_factor)/2)*self.square_side)).set_fill(cor), 
			self[i][j+d[1]].animate.stretch_to_fit_height(offset_factor*self.square_side).shift(d[1]*LEFT*(self.square_spacing+((1-offset_factor)/2)*self.square_side)).set_fill(cor),
			selfrun_time=time)

		#The following function one would be an alternative way draws a new Trimino, instead of highlighting the squares from the gride.
		#But it is work in progress
		# self.add(Trimino(direcao=d,fill_opacity=0.8, fill_color=BLUE, center=np.array([i,j])))

	##check is a piece is colored. This function is not used so far
	def get_status(self,i, j):
		return (self[i][j].get_fill_color().get_hex() != "#000")

	# return the left-bottom corner of the quadrant where "piece" is located. 
	# The result if one of [0,0], [0, size/2], [size/2, 0], [size/2, size/2]
	def get_new_corner(self, piece, size):
		if (piece[0] < 0 or piece[1] < 0 or piece[0] > size or piece[1] > size):
			raise Exception("Piece out of bounds")
		A = 0 if piece[0] < size/2 else int(size/2)
		B = 0 if piece[1] < size/2 else int(size/2)
		return np.array([A, B])


	# "leftcorner" is the left-bottom corner of the current subgrid beeing solved. 
	# This is necessary, because colors are attributed to the original pieces in the grid that was created
	# we need to recover absolute coordinates of those pieces in the grid, at the moment we highlight them
	# "marked" is the original missingppiece, with relative coordinates in the current subgrid.
	# Using relative coordinates makes it easier to determine the quadrant of the subgrid where "marked" is located
	def solve(self, cena,  currentOrder, marked=np.array([]), leftcorner=np.array([0,0]), time=1):
		if (currentOrder==0):
			return

		#set marked as the class value, in case it was not explicitly provided
		if(marked==np.array([])):
			if(self.missingppiece!=np.array([])):
				marked = self.missingppiece
			else:
				raise ValueError("No marked piece")

		currentSize = 2**currentOrder

		# We will create a square surouding the current subgrid
		#ss = shift size (length), is the shift to position such square, measured from the center of ManimScence, in manim coordinates
		#Adding a number to an np.array, will add that number to each of its coordinates. Same for multiplication.
		unitdistance = self.square_side+self.square_spacing
		ss = unitdistance*((currentSize - self.size)/2 + leftcorner)
		square = Square(side_length=(currentSize*unitdistance-self.square_spacing), color=RED).shift((ss[0])*UP + (ss[1])*RIGHT).scale(1.05)
		cena.add(square)
		# cena.play(FadeIn(square), run_time=time)

		#Finds the quadrant of marked relative to current subgrid
		# d can be: DR = [-1, 1], UR=[1, 1], DL=[-1,-1] or UL=[1, 1]
		# This will also determine the direction in which the center Trimino is placed
		d = [ (1 if marked[0] >= currentSize/2 else -1) , (1 if marked[1] >= currentSize/2 else -1)]
		
		#(c0, c1) = Center of Trimino given in (integer) coordinates relative to the current subgrid
		#It is locates in the middle and shifted to the quadrant in opposite direction of the missing piece
		c0 = int(currentSize/2 - (d[0]+1)/2)
		c1 = int(currentSize/2 - (d[1]+1)/2)

		# Highlight the trimino at the center.
		# tile method deals with absolute grid coordinate, so we add leftcorner to c0, c1
		self.tile(cena, c0+leftcorner[0], c1+leftcorner[1], d, cor=Grid.colors[currentOrder%5], time=time)

		# Recurse into the 4 subgrides of smaller currentOrder
		if(currentOrder > 1):
			# The first quadrant is the one where the original marked piece is located
			delta_leftcorner = self.get_new_corner(marked, currentSize)
			self.solve(cena, currentOrder-1, marked-delta_leftcorner, delta_leftcorner+leftcorner, time=time/3)

			#Then, the other 3 quadrants. In each of them, one square of the Trimino e passed as marked.
			trimono_pieces = ( np.array([c0+d[0], c1 ]), np.array([c0, c1]), np.array([c0 , c1+d[1]]) )
			for piece in trimono_pieces:
				delta_leftcorner = self.get_new_corner(piece, currentSize)
				self.solve(cena,  currentOrder-1, piece - delta_leftcorner, delta_leftcorner+leftcorner, time=time/3)

		cena.remove(square)
		# cena.play(FadeOut(square), run_time=time)



class OpeningManim(Scene):
	def construct(self):
		# thisorder = 4, square_side=5.5/size, square_spacing=0.8/size, sounds good
		missing_piece=np.array([10,5])
		thisorder = 4
		size = 2**thisorder
		g = Grid(order=thisorder, square_side=5.5/size, square_spacing=0)
		g.set_missing_piece(missing_piece)

		self.play(FadeIn(g))
		self.wait(1)
		g.solve(cena=self, currentOrder=thisorder, marked=missing_piece, time=0.8)
		self.wait(1)