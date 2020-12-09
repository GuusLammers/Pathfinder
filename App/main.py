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


# SET DISPLAY
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

	def position(self):
		return (self.x_pos, self.y_pos)

	def set_start(self):
		self.color = green

	def set_end(self):
		self.color = red	

	def set_barrier(self):
		self.color = black	

	def set_open(self):
		self.color = light_blue	
		
	def set_closed(self):
		self.color = dark_blue	

	def set_path(self):
		self.color = pink			

	def reset(self):
		self.color = white	
	
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

	#def __lt__(self, other):
		#return False			


# LABEL CLASS 
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

	def set_idle(self):
		self.labels = self.labels_idle

	def set_dijkstras(self):
		self.labels = self.label_dijkstras

	def set_a_star(self):
		self.labels = self.label_a_star
		
	def set_bfs(self):
		self.labels = self.label_bfs

	def draw(self, width, win):
		# check if num labels is 1 or not
		if len(self.labels) == 1:
			text_len = self.labels[0].get_width()
			offset = 0.5 * (width - text_len)
			win.blit(self.labels[0], (offset, width))

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


# DIJKSTRAS SEARCH
def dijkstras(draw, graph, start, end):
	counter = 0
	open_set = PriorityQueue()
	open_set.put((0, counter, start))
	
	came_from = {}
	
	g_score = {}
	for row in graph:
		for node in row:
			g_score[node] = float('inf')
	g_score[start] = 0	

	open_set_hash = {start}
	closed = {start}

	while not open_set.empty():
		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()

		current_node = open_set.get()[2]
		open_set_hash.remove(current_node)
		
		if current_node == end:
			construct_path(came_from, end, start, end, draw)
			end.set_end()
			start.set_start()
			return True

		for neighbor in current_node.neighbors:
			g_score_temp = g_score[current_node] + 1
			if g_score_temp < g_score[neighbor]:
				came_from[neighbor] = current_node
				g_score[neighbor] = g_score_temp
				if neighbor not in open_set_hash and neighbor not in closed:
					counter += 1
					open_set.put((g_score[neighbor], counter, neighbor))
					open_set_hash.add(neighbor)
					neighbor.set_open()

		draw()			
		if current_node != start:
			current_node.set_closed()
			closed.add(current_node)
					
	return False		


# A* SEARCH USING MANHATTAN DISTANCE
def a_star(draw, graph, start, end):
	counter = 0
	open_set = PriorityQueue()
	open_set.put((0, counter, start))
	
	came_from = {}
	
	g_score = {}
	f_score = {}
	for row in graph:
		for node in row:
			g_score[node] = float('inf')
			f_score[node] = float('inf')
	g_score[start] = 0
	f_score[start] = dist_manhattan(start.position(), end.position())		

	open_set_hash = {start}
	closed = {start}

	while not open_set.empty():
		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()

		current_node = open_set.get()[2]
		open_set_hash.remove(current_node)
		
		if current_node == end:
			construct_path(came_from, end, start, end, draw)
			end.set_end()
			start.set_start()
			return True

		for neighbor in current_node.neighbors:
			g_score_temp = g_score[current_node] + 1
			if g_score_temp < g_score[neighbor]:
				came_from[neighbor] = current_node
				g_score[neighbor] = g_score_temp
				f_score[neighbor] = g_score_temp + dist_manhattan(neighbor.position(), end.position())
				if neighbor not in open_set_hash and neighbor not in closed:
					counter += 1
					open_set.put((f_score[neighbor], counter, neighbor))
					open_set_hash.add(neighbor)
					neighbor.set_open()

		draw()			
		if current_node != start:
			current_node.set_closed()
			closed.add(current_node)
					
	return False		


# BEST FIRST SEARCH MANHATTAN DISTANCE
def best_first_search(draw, graph, start, end):
	counter = 0
	open_set = PriorityQueue()
	open_set.put((0, counter, start))
	
	came_from = {}
	
	f_score = {}
	for row in graph:
		for node in row:
			f_score[node] = float('inf')

	f_score[start] = dist_manhattan(start.position(), end.position())		

	open_set_hash = {start}
	closed = {start}

	while not open_set.empty():
		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()

		current_node = open_set.get()[2]
		open_set_hash.remove(current_node)
		
		if current_node == end:
			construct_path(came_from, end, start, end, draw)
			end.set_end()
			start.set_start()
			return True

		for neighbor in current_node.neighbors:
			if neighbor not in closed:
				came_from[neighbor] = current_node
				f_score[neighbor] = dist_manhattan(neighbor.position(), end.position())
				if neighbor not in open_set_hash:
					counter += 1
					open_set.put((f_score[neighbor], counter, neighbor))
					open_set_hash.add(neighbor)
					neighbor.set_open()

		draw()			
		if current_node != start:
			current_node.set_closed()
			closed.add(current_node)
					
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
		

# CURRENT ALGORITHM RUNNING DISPLAY
def running(win, width, running):	
	labels = [
		# dijkstras
		myfont.render('Dijkstras Search', True, (0, 0, 0)),
		# A* euclidean
		myfont.render('A* Search', True, (0, 0, 0)),
		# bfs euclidean
		myfont.render('Best First Search', True, (0, 0, 0))
	]

	if running[0]:
		win.blit(labels[0], (0, width))

	elif running[1]:
		win.blit(labels[1], (0, width))
		
	elif running[2]:
		win.blit(labels[2], (0, width))



# DRAW OUT SCREEN
def draw(win, grid, rows, width, labels):
	win.fill(grey)

	for row in grid:
		for node in row:
			node.draw()

	labels.draw(width, win)
			
	pg.display.update()			


# RETURN CLICKED NODES POSITION IN 2D LIST (GRAPH)
def clicked_node(pos, rows, width):
	gap = width//rows
	x, y = pos

	row = y//gap
	col = x//gap

	return row, col


# MAIN FUNCTION, CONTROLLS MAIN LOOP
def main(win, width):
	rows = 70
	graph = init_graph(rows, width)
	
	labels = Label()
	labels.set_idle()

	start = None
	end = None

	run = True
	started = False

	while run:
		draw(win, graph, rows, width, labels)
		for event in pg.event.get():
			if event.type == pg.QUIT:
				run = False

			if started: 
				continue	

			# if left mouse button is clicked	
			if pg.mouse.get_pressed()[0]:
				try:
					pos = pg.mouse.get_pos()
					col, row = clicked_node(pos, rows, width)
					node = graph[row][col]
					if not start:
						start = node
						start.set_start()
					elif not end:	
						if node != start:
							end = node
							end.set_end()
					elif node != start and node != end:
						node.set_barrier()

				except:
					pass		

			# if right mouse button is clicked	
			elif pg.mouse.get_pressed()[2]:
				try:
					pos = pg.mouse.get_pos()
					col, row = clicked_node(pos, rows, width)
					node = graph[row][col]
					if node is start:
						node.reset()
						start = None
					elif node is end:
						node.reset()
						end = None
					else:
						node.reset()		

				except:
					pass

			if event.type == pg.KEYDOWN:
				# run dijkstras search algoritm
				if event.key == pg.K_1 and not started:
					for row in graph:
						for node in row:
							node.add_neighbors(graph)
						
					labels.set_dijkstras()		

					dijkstras(lambda: draw(win, graph, rows, width, labels), graph, start, end)	

					labels.set_idle()

				# run A* search algoritm
				elif event.key == pg.K_2 and not started:
					for row in graph:
						for node in row:
							node.add_neighbors(graph)
						
					labels.set_a_star()		

					a_star(lambda: draw(win, graph, rows, width, labels), graph, start, end)
					
					labels.set_idle()

				# run best first search algoritm
				elif event.key == pg.K_3 and not started:
					for row in graph:
						for node in row:
							node.add_neighbors(graph)
						
					labels.set_bfs()		

					best_first_search(lambda: draw(win, graph, rows, width, labels), graph, start, end)		

					labels.set_idle()

				# run all search algorithms
				elif event.key == pg.K_SPACE and not started:
					for row in graph:
						for node in row:
							node.add_neighbors(graph)
	
					labels.set_dijkstras()		

					# run dijkstras
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

					labels.set_a_star()

					# run A*
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

					labels.set_bfs()

					# run best first search
					best_first_search(lambda: draw(win, graph, rows, width, labels), graph, start, end)	

					labels.set_idle()

				# reset graph	
				elif event.key == pg.K_c and not started:
					start = None
					end = None
					graph = init_graph(rows, width)		
						
	pg.quit()			

# main loop
main(window, width)	
