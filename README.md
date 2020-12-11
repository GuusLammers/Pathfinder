# Pathfinder
This is a visulaization tool that compares Dijkstras search, A* search, and Best First Search pathfinding algorithms. 

<p align="center"><img src="img/idle.PNG" width="50%" height="50%"></p>

It allows the user to place the start node (green), end node (red), and barriers (black) anywhere on the grid. When the algorithm is activated it attempts to find the shortest path between the start and end node. A picture showing the shortest path is shown below.  

<p align="center"><img src="img/path.PNG" width="50%" height="50%"></p>

If you would like to see a visual of the search algoritms running there is a video in the video folder of this repository showing the algorithms searching through different mazes! 

# What I Learnt
<ol>
 <li>Used Pygame to build visualiztion GUI.</li>
 <li>Built graph by creating a custom Node class.</li>
 <li>Implemented the following path finding algorithms:
  <ul>
    <li><b>Dijkstra's</b> (Breadth First Search).</li>
    <li><b>A*</b> (Guided search using manhattan heuristic).</li>
    <li><b>Best First Search</b> (Greedy search using manhattan heuristic).</li> 
  </ul>
 </li>
</ol>

# User Instructions
<ol>
 <li>Download the main.py file and store it somewhere on your computer.</li>
 <li>To run the code you will need to create a Python environment and install pygame by opening your terminal and typing 'pip install pygame', this is the only external library you should need.</li>
 <li>Run the program from within your IDE or from the command line.</li>
 <li>To place the start node, end node, and barriers simply right click on the d=grid where you would like the node to be placed. To remove any nodes you can erase them by left cleft clicking.</li>
</ol>

 
