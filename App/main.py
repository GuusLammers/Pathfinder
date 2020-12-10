import pygame as pg
import math
from queue import PriorityQueue
import time
pg.font.init()

#GLOBAL VARIABLES
width = 700
height = 720

# colors for GUI
light_blue = (0, 234, 255)
dark_blue = (0, 131, 143)
pink = (255, 0, 200)
black = (0, 0, 0)
white = (255, 255, 255)
grey = (200, 200, 200)
green = (0, 255, 0)
red = (255, 0, 0)

# font
myfont = pg.font.SysFont('Arial', 15)


# SET DISPLAY CAPTION, WIDTH, AND HEIGHT
window = pg.display.set_mode((width, height))
pg.display.set_caption('Pathfinder')


# NODE CLASS FOR CREATING GRAPH 
class Node:

	def __init__(self, row, col, width, height, row_total, gap=0.9):
		self.row = row
		self.col = col
		self.row_total = row_total
		self.width = width * gap
		self.height = height * gap
		self.x_pos = row * height + 0.5 * (1 - gap) * width/gap  
		self.y_pos = col * width + 0.5 * (1 - gap) * height/gap
		self.neighbors = []
		self.color = white

	# returns (x,y) position of node on screen
	def position(self):
		return (self.x_pos, self.y_pos)

	# sets node to start node by making it green	
	def set_start(self):
		self.color = green

	# sets node to end node by making it red
	def set_end(self):
		self.color = red	

	# sets node to barrier by making it black	
	def set_barrier(self):
		self.color = black	

	# adds node to open set by making it light blue
	def set_open(self):
		self.color = light_blue	
		
	# sets node to closed by making it dark blue	
	def set_closed(self):
		self.color = dark_blue	

	# sets node to pink to draw the shortest path	
	def set_path(self):
		self.color = pink			

	# resets node by making it white
	def reset(self):
		self.color = white	
	
	# draws node represented as a rectangle on screen at its specified (x,y) position
	def draw(self):
		pg.draw.rect(window, self.color, (self.x_pos, self.y_pos, self.width, self.height))	

	# add neighbors if they are not barriers
	def add_neighbors(self, graph):
		# down: if not in the bottom row and not a barrier add to neighbors	
		if self.row	< self.row_total - 1:
			down = graph[self.row + 1][self.col]
			if down.color != black:
				self.neighbors.append(down)	
		# up: if not in the top row and not a barrier add to neighbors	
		if self.row > 0:
			up = graph[self.row - 1][self.col]
			if up.color != black:
				self.neighbors.append(up)
		# left: if not in the left most column and not a barrier add to neighbors	
		if self.col > 0:
			left = graph[self.row][self.col - 1]
			if left.color != black:
				self.neighbors.append(left)
		# right: if not in the right most column and not a barrier add to neighbors	
		if self.col < self.row_total - 1:	
			right = graph[self.row][self.col + 1]
			if right.color != black:
				self.neighbors.append(right)


# LABEL CLASS CONTROLS LABEL BEING DISPLAYED AT BOTTOM OF SCREEN 
class Label:

	def __init__(self):
		self.labels = []
		self.labels_idle = [
			# dijkstras
			myfont.render('1 - Run Dijkstras', True, (0, 0, 0)),
			# A* 
			myfont.render('2 - Run A*', True, (0, 0, 0)),
			# bfs 
			myfont.render('3 - Run Best First Search', True, (0, 0, 0)),
			# all
			myfont.render('Space - Run All', True, (0, 0, 0)),
			# reset
			myfont.render('C - Reset', True, (0, 0, 0))
		]
		self.label_dijkstras = [myfont.render('Dijkstras', True, (0, 0, 0))]
		self.label_a_star = [myfont.render('A*', True, (0, 0, 0))]
		self.label_bfs = [myfont.render('Best First Search', True, (0, 0, 0))]

	# show idle labels
	def set_idle(self):
		self.labels = self.labels_idle

	# show dijkstras label
	def set_dijkstras(self):
		self.labels = self.label_dijkstras

	# show a star label
	def set_a_star(self):
		self.labels = self.label_a_star
		
	# show best first search label		
	def set_bfs(self):
		self.labels = self.label_bfs

	# draws labels on screen
	def draw(self, width, win):
		# check if num labels is 1 or not
		if len(self.labels) == 1:
			text_len = self.labels[0].get_width()
			offset = 0.5 * (width - text_len)
			win.blit(self.labels[0], (offset, width))

		# shows idle labels if system is in idle state	
		else:
			text_len = 0
			for label in self.labels:
				text_len += label.get_width()

			pad_x = int(700 - text_len) // 6	

			offset = pad_x
			for label in self.labels: 
				win.blit(label, (offset, width))
				offset += label.get_width() + pad_x						

# MANHATTAN DISTANCE HEURISTIC
def dist_manhattan(p1, p2):
	return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) 


# DIJKSTRAS SEARCH ALGORITHM
def dijkstras(draw, graph, start, end):
	counter = 0
	open_set = PriorityQueue()
	open_set.put((0, counter, start))
	came_from = {}
	
	# set scores for all nodes to infinity and score for start to 0
	g_score = {}
	for row in graph:
		for node in row:
			g_score[node] = float('inf')
	g_score[start] = 0	

	# add start to open set and closed
	open_set_hash = {start}
	closed = {start}

	# main loop, runs until open set is empty or end node is found
	while not open_set.empty():
		# allows closing of application while running
		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()

		# get current node object from priority queue		
		current_node = open_set.get()[2]
		open_set_hash.remove(current_node)
		
		# check if current node is the end node
		if current_node == end:
			construct_path(came_from, end, start, end, draw)
			end.set_end()
			start.set_start()
			return True

		# check all of current nodes neighbors
		for neighbor in current_node.neighbors:
			g_score_temp = g_score[current_node] + 1
			# if a path with a lower score to a neighbor is found overwrite previous score
			if g_score_temp < g_score[neighbor]:
				came_from[neighbor] = current_node
				g_score[neighbor] = g_score_temp
				# if neighbor has not been analyzed add to open set
				if neighbor not in open_set_hash and neighbor not in closed:
					counter += 1
					open_set.put((g_score[neighbor], counter, neighbor))
					open_set_hash.add(neighbor)
					neighbor.set_open()

		# redraw updated screen			
		draw()			
		if current_node != start:
			current_node.set_closed()
			closed.add(current_node)
	
	# if no path to en is found return false				
	return False		


# A* SEARCH USING MANHATTAN DISTANCE
def a_star(draw, graph, start, end):
	counter = 0
	open_set = PriorityQueue()
	open_set.put((0, counter, start))
	came_from = {}
	
	# set scores for all nodes to infinity and score for start to manhattan distance
	g_score = {}
	f_score = {}
	for row in graph:
		for node in row:
			g_score[node] = float('inf')
			f_score[node] = float('inf')
	g_score[start] = 0
	f_score[start] = dist_manhattan(start.position(), end.position())		

	# add start to open set and closed
	open_set_hash = {start}
	closed = {start}

	# main loop, runs until open set is empty or end node is found
	while not open_set.empty():
		# allows closing of application while running
		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()

		# get current node object from priority queue			
		current_node = open_set.get()[2]
		open_set_hash.remove(current_node)
		
		# check if current node is the end node
		if current_node == end:
			construct_path(came_from, end, start, end, draw)
			end.set_end()
			start.set_start()
			return True

		# check all of current nodes neighbors	
		for neighbor in current_node.neighbors:
			g_score_temp = g_score[current_node] + 1
			# if a path with a lower score to a neighbor is found overwrite previous score
			if g_score_temp < g_score[neighbor]:
				came_from[neighbor] = current_node
				g_score[neighbor] = g_score_temp
				f_score[neighbor] = g_score_temp + dist_manhattan(neighbor.position(), end.position())
				# if neighbor has not been analyzed add to open set
				if neighbor not in open_set_hash and neighbor not in closed:
					counter += 1
					open_set.put((f_score[neighbor], counter, neighbor))
					open_set_hash.add(neighbor)
					neighbor.set_open()

		# redraw updated screen					
		draw()			
		if current_node != start:
			current_node.set_closed()
			closed.add(current_node)
				
	# if no path to en is found return false				
	return False		


# BEST FIRST SEARCH MANHATTAN DISTANCE
def best_first_search(draw, graph, start, end):
	counter = 0
	open_set = PriorityQueue()
	open_set.put((0, counter, start))
	came_from = {}
	
	# set scores for all nodes to infinity and score for start to manhattan distance
	f_score = {}
	for row in graph:
		for node in row:
			f_score[node] = float('inf')
	f_score[start] = dist_manhattan(start.position(), end.position())		

	# add start to open set and closed
	open_set_hash = {start}
	closed = {start}

	# main loop, runs until open set is empty or end node is found
	while not open_set.empty():
		# allows closing of application while running
		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()

		# get current node object from priority queue			
		current_node = open_set.get()[2]
		open_set_hash.remove(current_node)
		
		# check if current node is the end node
		if current_node == end:
			construct_path(came_from, end, start, end, draw)
			end.set_end()
			start.set_start()
			return True

		# check all of current nodes neighbors		
		for neighbor in current_node.neighbors:
			if neighbor not in closed:
				came_from[neighbor] = current_node
				f_score[neighbor] = dist_manhattan(neighbor.position(), end.position()) 
				# if neighbor has not been analyzed add to open set
				if neighbor not in open_set_hash:
					counter += 1
					open_set.put((f_score[neighbor], counter, neighbor))
					open_set_hash.add(neighbor)
					neighbor.set_open()

		# redraw updated screen					
		draw()			
		if current_node != start:
			current_node.set_closed()
			closed.add(current_node)
			
	# if no path to en is found return false					
	return False		


# CONSTRUCT SHORTEST PATH
def construct_path(came_from, current, start, end, draw):
	while current in came_from:	
		current = came_from[current]
		current.set_path()
		draw()
	
	end.set_end()
	start.set_start()	
	draw()


# INITIALIZE GRAPH INTO 2D LIST
def init_graph(rows, width):
	graph = []
	gap = width // rows
	# create 2D list holding all nodes
	for i in range(rows):
		graph.append([])
		for j in range(rows):
			graph[i].append(Node(i, j, gap, gap, rows))	

	return graph		
		

# DRAW OUT SCREEN
def draw(win, grid, rows, width, labels):
	# make background grey
	win.fill(grey)

	# draw all nodes
	for row in grid:
		for node in row:
			node.draw()

	# draw labels
	labels.draw(width, win)
		
	# update display		
	pg.display.update()			


# RETURN CLICKED NODES POSITION IN 2D LIST (GRAPH)
def clicked_node(pos, rows, width):
	gap = width // rows
	x, y = pos

	row = y // gap
	col = x // gap

	return row, col


# MAIN FUNCTION, CONTROLLS MAIN LOOP
def main(win, width):
	# set number of rows
	rows = 70

	# initialize graph and labels
	graph = init_graph(rows, width)
	labels = Label()
	labels.set_idle()

	# controls if start and end nodes have been placed or not
	start = None
	end = None

	# controls if main loop is running and if algorithm is running
	run = True
	started = False

	# main loop
	while run:
		# draw screen
		draw(win, graph, rows, width, labels)
		
		# check through all events
		for event in pg.event.get():
			# allows user to close app
			if event.type == pg.QUIT:
				run = False

			# if algorithm is running skip remaining instrucions in loop	
			if started: 
				continue	

			# if left mouse button is clicked set node depending on conditions	
			if pg.mouse.get_pressed()[0]:
				try:
					pos = pg.mouse.get_pos()
					col, row = clicked_node(pos, rows, width)
					node = graph[row][col]
					# place start node if not yet placed
					if not start:
						start = node
						start.set_start()
					# place end node if not yet placed	
					elif not end:	
						if node != start:
							end = node
							end.set_end()
					# place barrier if start and end node have been placed		
					elif node != start and node != end:
						node.set_barrier()

				except:
					pass		

			# if right mouse button is clicked reset node	
			elif pg.mouse.get_pressed()[2]:
				try:
					pos = pg.mouse.get_pos()
					col, row = clicked_node(pos, rows, width)
					node = graph[row][col]
					# if node is start reset node and set start to none
					if node is start:
						node.reset()
						start = None
					# if node is end reset node and set end to none
					elif node is end:
						node.reset()
						end = None
					# reset node
					else:
						node.reset()		

				except:
					pass

			# if key pressed		
			if event.type == pg.KEYDOWN:
				# if key 1 is pressed run dijkstras search algoritm
				if event.key == pg.K_1 and not started:
					# update neighbors for all nodes in graph
					for row in graph:
						for node in row:
							node.add_neighbors(graph)
						
					# set label to display running algorithm	
					labels.set_dijkstras()		

					# run algorithm
					dijkstras(lambda: draw(win, graph, rows, width, labels), graph, start, end)	

					# set label to display idle
					labels.set_idle()

				# if key 2 is pressed run A* search algoritm
				elif event.key == pg.K_2 and not started:
					# update neighbors for all nodes in graph
					for row in graph:
						for node in row:
							node.add_neighbors(graph)
						
					# set label to display running algorithm	
					labels.set_a_star()		

					# run algorithm
					a_star(lambda: draw(win, graph, rows, width, labels), graph, start, end)
					
					# set label to display idle
					labels.set_idle()

				# if key 3 is pressed run best first search algoritm
				elif event.key == pg.K_3 and not started:
					# update neighbors for all nodes in graph
					for row in graph:
						for node in row:
							node.add_neighbors(graph)
						
					# set label to display running algorithm	
					labels.set_bfs()		

					# run algorithm
					best_first_search(lambda: draw(win, graph, rows, width, labels), graph, start, end)		

					# set label to display idle
					labels.set_idle()

				# if key space is pressed run all search algorithms
				elif event.key == pg.K_SPACE and not started:
					# update neighbors for all nodes in graph
					for row in graph:
						for node in row:
							node.add_neighbors(graph)

					# set label to display running algorithm	
					labels.set_dijkstras()		

					# run algorithm
					dijkstras(lambda: draw(win, graph, rows, width, labels), graph, start, end)	

					# sleep for 2.5 seconds
					time.sleep(2.5)

					# reset graph colors
					for row in graph:
						for node in row:
							if node.color != black:
								node.reset()
					start.set_start()
					end.set_end()			

					# set label to display running algorithm
					labels.set_a_star()

					# run algorithm
					a_star(lambda: draw(win, graph, rows, width, labels), graph, start, end)	

					# sleep for 2.5 seconds
					time.sleep(2.5)

					# reset graph colors
					for row in graph:
						for node in row:
							if node.color != black:
								node.reset()
					start.set_start()
					end.set_end()

					# sleep for 2.5 seconds
					time.sleep(2.5)

					# set label to display running algorithm
					labels.set_bfs()

					# run algorithm
					best_first_search(lambda: draw(win, graph, rows, width, labels), graph, start, end)	

					# set label to display idle
					labels.set_idle()

				# if key c is pressed reset graph	
				elif event.key == pg.K_c and not started:
					start = None
					end = None
					graph = init_graph(rows, width)		
						
	pg.quit()			

# main loop
main(window, width)	
