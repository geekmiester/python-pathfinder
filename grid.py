import pygame
import sys
import time
from priority_queue import PrioritySet, PriorityQueue, AStarQueue
from math import inf
import random
from collections import deque

# Defined colors

# Active colors
BLACK = pygame.Color("#333533")
WHITE2 = pygame.Color("#f1faee")
SKY_BLUE = pygame.Color("#FFB300")
BLUE_END = pygame.Color("#457b9d")
GREEN_END2 = pygame.Color("#8ac926")
GREEN_END = pygame.Color("#558B2F")
BLUE_DARK = pygame.Color("#0077b6")
ORANGE2 = pygame.Color("#e63946")
GREEN = pygame.Color("#90be6d")
BROWN = pygame.Color("#f3722c")
GREY = pygame.Color("#bcb8b1")
# Buttons


class Button():
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        self.text = text

    def draw(self, win, outline=None):
        # Call this method to draw the Button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x, self.y,
                                            self.width, self.height), 0)

        pygame.draw.rect(win, self.color, (self.x+1, self.y +
                                           1, self.width-1, self.height-1), 0)

        if self.text != '':
            font = pygame.font.SysFont('Roboto', 18)
            text = font.render(self.text, 1, (0, 0, 0))
            win.blit(text, (self.x + int(self.width/2 - text.get_width()/2),
                            self.y + int(self.height/2 - text.get_height()/2)))

    def isOver(self, pos):
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True

        return False

# place to add different node types


class Node():

    nodetypes = ['blank', 'start', 'end', 'wall', 'mud', 'dormant']

    colors = {'regular': {'blank': WHITE2, 'start': ORANGE2, 'end': GREEN_END2, 'wall': BLACK, 'mud': BROWN, 'dormant': GREY},
              'visited': {'blank': SKY_BLUE, 'start': ORANGE2, 'end': GREEN_END, 'wall': BLACK, 'mud': GREEN, 'dormant': GREY},
              'path': {'blank': BLUE_DARK, 'start': ORANGE2, 'end': GREEN_END, 'wall': BLACK, 'mud': BLUE_DARK, 'dormant': GREY}
              }

    distance_modifiers = {'blank': 1, 'start': 1,
                          'end': 1, 'wall': inf, 'mud': 3, 'dormant': inf}

    def __init__(self, nodetype, text='', colors=colors, dmf=distance_modifiers):
        self.nodetype = nodetype
        self.rcolor = colors['regular'][self.nodetype]
        self.vcolor = colors['visited'][self.nodetype]
        self.pcolor = colors['path'][self.nodetype]
        self.is_visited = True if nodetype == 'start' else True if nodetype == 'end' else False
        self.is_path = True if nodetype == 'start' else True if nodetype == 'end' else False
        self.distance_modifier = dmf[self.nodetype]
        self.color = self.pcolor if self.is_path else self.vcolor if self.is_visited else self.rcolor

    def update(self, nodetype=False, is_visited='unchanged', is_path='unchanged', colors=colors, dmf=distance_modifiers, nodetypes=nodetypes):
        if nodetype:
            assert nodetype in nodetypes, f"nodetype must be one of: {nodetypes}"
            if (self.nodetype == ('start' or 'end')) and (nodetype == ('wall' or 'mud')):
                pass
            else:
                self.nodetype = nodetype

        if is_visited != 'unchanged':
            assert type(
                is_visited) == bool, "'is_visited' must be boolean: True or False"
            self.is_visited = is_visited

        if is_path != 'unchanged':
            assert type(
                is_path) == bool, "'is_path' must be boolean: True or False"
            self.is_path = is_path

        self.rcolor = colors['regular'][self.nodetype]
        self.vcolor = colors['visited'][self.nodetype]
        self.pcolor = colors['path'][self.nodetype]
        self.distance_modifier = dmf[self.nodetype]
        self.color = self.pcolor if self.is_path else self.vcolor if self.is_visited else self.rcolor


# setting the WIDTH and HEIGHT of each grid location
WIDTH = 7
HEIGHT = WIDTH  # creating them as squares
BUTTON_HEIGHT = 50

# Setting the margin between each cell
MARGIN = 0

# Creating a 2 dimensional array (a list of lists)
grid = []
ROWS = 95
# Iterating through every row and column, adding blank nodes
for row in range(ROWS):
    grid.append([])
    for column in range(ROWS):
        grid[row].append(Node('blank'))

# Setting the start and end points for the pathfinder
START_POINT = (random.randrange(2, ROWS-1, 2)-1,
               random.randrange(2, ROWS-1, 2)-1)
END_POINT = (random.randrange(2, ROWS-1, 2), random.randrange(2, ROWS-1, 2))

grid[START_POINT[0]][START_POINT[1]].update(nodetype='start')
grid[END_POINT[0]][END_POINT[1]].update(nodetype='end')

DIAGONALS = False
VISUALISE = True

# Creating handlers for click & drag
mouse_drag = False
drag_start_point = False
drag_end_point = False

# Used for deciding what to do in different situations
path_found = False
algorithm_run = False


# Intializing pygame
pygame.init()

# Setting a default font for nodes
FONT = pygame.font.SysFont('Roboto', 18)

# Setting the width and height of the screen [width, height]
SCREEN_WIDTH = ROWS * (WIDTH + MARGIN) + MARGIN * 2
SCREEN_HEIGHT = SCREEN_WIDTH + BUTTON_HEIGHT * 3
WINDOW_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(WINDOW_SIZE)

screen = pygame.display.set_mode((WINDOW_SIZE), pygame.RESIZABLE,)
pygame.display.set_caption("PATHFINDING SIMULATOR")

# while True:
#     screen.fill(pygame.Color("#f1faee"))
# Creating Controls
dijkstraButton = Button(GREY, 0, SCREEN_WIDTH, SCREEN_WIDTH/3,
                        BUTTON_HEIGHT, "Dijkstra (=BFS when constant distances)")
dfsButton = Button(GREY, 0, SCREEN_WIDTH + BUTTON_HEIGHT,
                   SCREEN_WIDTH/6, BUTTON_HEIGHT, "DFS")
bfsButton = Button(GREY, 0 + SCREEN_WIDTH/6 + 1, SCREEN_WIDTH +
                   BUTTON_HEIGHT, SCREEN_WIDTH/6, BUTTON_HEIGHT, "BFS")
astarButton = Button(GREY, 0, SCREEN_WIDTH + BUTTON_HEIGHT *
                     2, SCREEN_WIDTH/3, BUTTON_HEIGHT, "A*")
resetButton = Button(GREY, SCREEN_WIDTH/3, SCREEN_WIDTH,
                     SCREEN_WIDTH/3, BUTTON_HEIGHT*2, "Reset")
mazeButton = Button(GREY, (SCREEN_WIDTH/3)*2, SCREEN_WIDTH,
                    SCREEN_WIDTH/6, BUTTON_HEIGHT, "Maze (Prim)")
altPrimButton = Button(GREY, (SCREEN_WIDTH/6)*5, SCREEN_WIDTH,
                       SCREEN_WIDTH/6, BUTTON_HEIGHT, "Maze (Alt Prim)")
recursiveMazeButton = Button(GREY, (SCREEN_WIDTH/3)*2, SCREEN_WIDTH +
                             BUTTON_HEIGHT, SCREEN_WIDTH/3, BUTTON_HEIGHT, "Maze (recursive div)")
terrainButton = Button(GREY, (SCREEN_WIDTH/3)*2, SCREEN_WIDTH +
                       BUTTON_HEIGHT*2, SCREEN_WIDTH/3, BUTTON_HEIGHT, "Random Terrain")
visToggleButton = Button(GREY, SCREEN_WIDTH/3, SCREEN_WIDTH + BUTTON_HEIGHT*2,
                         SCREEN_WIDTH/3, BUTTON_HEIGHT, f"Visualise: {str(VISUALISE)}")

# pygame.display.update()
# for event in pygame.event.get():
#     if event.type == pygame.QUIT:
#         pygame.quit()
#         sys.exit()
#     if event.type == pygame.KEYDOWN:
#         if event.key == pygame.K_ESCAPE:
#             pygame.quit()
#             sys.exit()

#     if event.type == pygame.VIDEORESIZE:
#         # There's some code to add back window content here.
#         surface = pygame.display.set_mode((event.w, event.h),
#                                           pygame.RESIZABLE)


# Loops until the close Button is clicked.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

#---------------------------------------#
# -------- Main Program Loop -----------
while not done:
    # --- Main event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            # Find out which keys have been pressed
            pressed = pygame.key.get_pressed()

            # If click is inside grid
            if pos[1] <= SCREEN_WIDTH-1:

                # Change the x/y screen coordinates to grid coordinates
                column = pos[0] // (WIDTH + MARGIN)
                row = pos[1] // (HEIGHT + MARGIN)

                if (row, column) == START_POINT:
                    drag_start_point = True
                elif (row, column) == END_POINT:
                    drag_end_point = True
                else:
                    cell_updated = grid[row][column]
                    if pressed[pygame.K_LCTRL]:
                        update_cell_to = 'mud'
                    else:
                        update_cell_to = 'wall'
                    cell_updated.update(nodetype=update_cell_to)
                    mouse_drag = True
                    if algorithm_run and cell_updated.is_path == True:
                        path_found = update_path()

            # NOTE: optimize button handling and state management
            # TODO: try creating an onClick method inside the button class
            # where treatment can be defined instead for so many if statements for different buttons

            # For Dijkstra's Algorithm
            elif dijkstraButton.isOver(pos):
                clear_visited()
                update_gui(draw_background=False, draw_buttons=False)
                if VISUALISE:
                    pygame.display.flip()
                path_found = dijkstra(grid, START_POINT, END_POINT)
                grid[START_POINT[0]][START_POINT[1]].update(nodetype='start')
                algorithm_run = 'dijkstra'

            # For DFS algorithm
            elif dfsButton.isOver(pos):
                clear_visited()
                update_gui(draw_background=False, draw_buttons=False)
                if VISUALISE:
                    pygame.display.flip()
                path_found = xfs(grid, START_POINT, END_POINT, x='d')
                grid[START_POINT[0]][START_POINT[1]].update(nodetype='start')
                algorithm_run = 'dfs'

            # For BFS algorithm
            elif bfsButton.isOver(pos):
                clear_visited()
                update_gui(draw_background=False, draw_buttons=False)
                if VISUALISE:
                    pygame.display.flip()
                path_found = xfs(grid, START_POINT, END_POINT, x='b')
                grid[START_POINT[0]][START_POINT[1]].update(nodetype='start')
                algorithm_run = 'bfs'

            # For A* algorithm
            elif astarButton.isOver(pos):
                clear_visited()
                update_gui(draw_background=False, draw_buttons=False)
                if VISUALISE:
                    pygame.display.flip()
                path_found = dijkstra(grid, START_POINT, END_POINT, astar=True)
                grid[START_POINT[0]][START_POINT[1]].update(nodetype='start')
                algorithm_run = 'astar'

            # Reset Button
            elif resetButton.isOver(pos):
                path_found = False
                algorithm_run = False
                for row in range(ROWS):
                    for column in range(ROWS):
                        if (row, column) != START_POINT and (row, column) != END_POINT:
                            grid[row][column].update(
                                nodetype='blank', is_visited=False, is_path=False)

            # Prim Button
            elif mazeButton.isOver(pos):
                path_found = False
                algorithm_run = False
                for row in range(ROWS):
                    for column in range(ROWS):
                        if (row, column) != START_POINT and (row, column) != END_POINT:
                            grid[row][column].update(
                                nodetype='blank', is_visited=False, is_path=False)
                grid = better_prim()

            # Better Prim Button
            elif altPrimButton.isOver(pos):
                path_found = False
                algorithm_run = False
                for row in range(ROWS):
                    for column in range(ROWS):
                        if (row, column) != START_POINT and (row, column) != END_POINT:
                            grid[row][column].update(
                                nodetype='blank', is_visited=False, is_path=False)
                grid = prim()

            # Random Maze (recursive division) Button
            elif recursiveMazeButton.isOver(pos):
                path_found = False
                algorithm_run = False
                for row in range(ROWS):
                    for column in range(ROWS):
                        if (row, column) != START_POINT and (row, column) != END_POINT:
                            grid[row][column].update(
                                nodetype='blank', is_visited=False, is_path=False)
                            draw_square(row, column)
                if VISUALISE:
                    pygame.display.flip()
                recursive_division()

            # Random Terrain Button
            elif terrainButton.isOver(pos):
                path_found = False
                algorithm_run = False
                for row in range(ROWS):
                    for column in range(ROWS):
                        if (row, column) != START_POINT and (row, column) != END_POINT:
                            grid[row][column].update(
                                nodetype='blank', is_visited=False, is_path=False)
                update_gui(draw_background=False, draw_buttons=False)
                random_terrain()

            # Visualisation Toggle Button
            elif visToggleButton.isOver(pos):
                if VISUALISE:
                    VISUALISE = False
                else:
                    VISUALISE = True

        elif event.type == pygame.MOUSEBUTTONUP:
            # Turning off all mouse drags if mouse Button released
            mouse_drag = drag_end_point = drag_start_point = False

        elif event.type == pygame.MOUSEMOTION:

            # Boolean values saying whether left, middle and right mouse buttons are currently pressed
            left, middle, right = pygame.mouse.get_pressed()

            # NOTE: Sometimes it gets stuck in this loop if the mousebutton is released while not in the pygame screen
            # This acts to break out of that loop
            if not left:
                mouse_drag = drag_end_point = drag_start_point = False
                continue

            # On mouse move, Get the position
            pos = pygame.mouse.get_pos()

            # Change the x/y screen coordinates to grid coordinates
            column = pos[0] // (WIDTH + MARGIN)
            row = pos[1] // (HEIGHT + MARGIN)

            # Turn mouse_drag off if mouse goes outside of grid
            if pos[1] >= SCREEN_WIDTH-2 or pos[1] <= 2 or pos[0] >= SCREEN_WIDTH-2 or pos[0] <= 2:
                mouse_drag = False
                continue

            cell_updated = grid[row][column]

            # Adding walls or sticky mud patches
            if mouse_drag == True:
                if (row, column) == START_POINT:
                    pass
                elif (row, column) == END_POINT:
                    pass
                else:
                    if pressed[pygame.K_LCTRL]:
                        update_cell_to = 'mud'
                    else:
                        update_cell_to = 'wall'
                    cell_updated.update(nodetype=update_cell_to)

                mouse_drag = True

                if algorithm_run:
                    if cell_updated.is_path == True:
                        path_found = update_path()

            # Moving the start point
            elif drag_start_point == True:
                if grid[row][column].nodetype == "blank":
                    grid[START_POINT[0]][START_POINT[1]].update(
                        nodetype='blank', is_path=False, is_visited=False)
                    START_POINT = (row, column)
                    grid[START_POINT[0]][START_POINT[1]].update(
                        nodetype='start')
                    # If we have already run the algorithm, update it as the point is moved
                    if algorithm_run:
                        path_found = update_path()
                        grid[START_POINT[0]][START_POINT[1]].update(
                            nodetype='start')

            # Moving the end point
            elif drag_end_point == True:
                if grid[row][column].nodetype == "blank":
                    grid[END_POINT[0]][END_POINT[1]].update(
                        nodetype='blank', is_path=False, is_visited=False)
                    END_POINT = (row, column)
                    grid[END_POINT[0]][END_POINT[1]].update(nodetype='end')
                    # If we have already run the algorithm, update it as the point is moved
                    if algorithm_run:
                        path_found = update_path()
                        grid[START_POINT[0]][START_POINT[1]].update(
                            nodetype='start')

            pygame.display.flip()
    # ---------------------------------------------
    # --------------MAZE GAME LOGIC---------------

    ### UTILITY FUNCTIONS ###

    # Clear board, keeping excluded nodes

    def clear_visited():
        excluded_nodetypes = ['start', 'end', 'wall', 'mud']
        for row in range(ROWS):
            for column in range(ROWS):
                if grid[row][column].nodetype not in excluded_nodetypes:
                    grid[row][column].update(
                        nodetype="blank", is_visited=False, is_path=False)
                else:
                    grid[row][column].update(is_visited=False, is_path=False)
        update_gui(draw_background=False, draw_buttons=False)

    def update_path(algorithm_run=algorithm_run):

        clear_visited()

        valid_algorithms = ['dijkstra', 'astar', 'dfs', 'bfs']

        assert algorithm_run in valid_algorithms, f"last algorithm used ({algorithm_run}) is not in valid algorithms: {valid_algorithms}"

        if algorithm_run == 'dijkstra':
            path_found = dijkstra(
                grid, START_POINT, END_POINT, visualise=False)
        elif algorithm_run == 'astar':
            path_found = dijkstra(
                grid, START_POINT, END_POINT, visualise=False, astar=True)
        elif algorithm_run == 'dfs':
            path_found = xfs(grid, START_POINT, END_POINT,
                             x='d', visualise=False)
        elif algorithm_run == 'bfs':
            path_found = xfs(grid, START_POINT, END_POINT,
                             x='b', visualise=False)
        else:
            path_found = False
        return path_found

    def random_terrain(mazearray=grid, num_patches=False, visualise=VISUALISE):
        if not num_patches:
            num_patches = random.randrange(int(ROWS/10), int(ROWS/4))

        terrain_nodes = set([])

        if VISUALISE:
            pygame.display.flip()

        # NOTE: For each patch being created, it is started with a central node and branches outwards
        # getting neighbours of neighbours etc. for each node that is considered, there is
        # a variable probability of it becoming a patch of mud
        # As we branch outwards that probability decreases
        for patch in range(num_patches+1):
            neighbour_cycles = 0
            centre_point = (random.randrange(1, ROWS-1),
                            random.randrange(1, ROWS-1))
            patch_type = 'mud'
            terrain_nodes.add(centre_point)

            while len(terrain_nodes) > 0:
                node = terrain_nodes.pop()

                if grid[node[0]][node[1]].nodetype != 'start' and grid[node[0]][node[1]].nodetype != 'end':
                    grid[node[0]][node[1]].update(nodetype=patch_type)
                    draw_square(node[0], node[1])

                    if visualise:
                        update_square(node[0], node[1])
                        time.sleep(0.000001)

                neighbour_cycles += 1

                for node, ntype in get_neighbours(node):

                    if grid[node[0]][node[1]].nodetype == 'mud':
                        continue
                    threshold = 700-(neighbour_cycles*10)

                    if random.randrange(1, 101) <= threshold:
                        terrain_nodes.add(node)

    # Function for moving an item between two dicts
    def dict_move(from_dict, to_dict, item):
        to_dict[item] = from_dict[item]
        from_dict.pop(item)
        return from_dict, to_dict

    # + represents non-diagonal neighbours, x diagonal neighbours
    def get_neighbours(node, max_width=ROWS-1, diagonals=DIAGONALS):
        if not diagonals:
            neighbours = (
                ((min(max_width, node[0]+1), node[1]), "+"),
                ((max(0, node[0]-1), node[1]), "+"),
                ((node[0], min(max_width, node[1]+1)), "+"),
                ((node[0], max(0, node[1]-1)), "+")
            )
        else:
            neighbours = (
                ((min(max_width, node[0]+1), node[1]), "+"),
                ((max(0, node[0]-1), node[1]), "+"),
                ((node[0], min(max_width, node[1]+1)), "+"),
                ((node[0], max(0, node[1]-1)), "+"),
                ((min(max_width, node[0]+1), min(max_width, node[1]+1)), "x"),
                ((min(max_width, node[0]+1), max(0, node[1]-1)), "x"),
                ((max(0, node[0]-1), min(max_width, node[1]+1)), "x"),
                ((max(0, node[0]-1), max(0, node[1]-1)), "x")
            )

        # return neighbours
        return (neighbour for neighbour in neighbours if neighbour[0] != node)

    # For Pygame: this draws a square in the given location (for when properties updated)
    def draw_square(row, column, grid=grid):
        pygame.draw.rect(
            screen,
            grid[row][column].color,
            [
                (MARGIN + HEIGHT) * column + MARGIN,
                (MARGIN + HEIGHT) * row + MARGIN,
                WIDTH,
                HEIGHT
            ]
        )
        pygame.event.pump()

    # For Pygame: this updates the screen for the given square
    # (as opposed to pygame.display.flip() which updates the entire screen)
    def update_square(row, column):
        pygame.display.update(
            (MARGIN + WIDTH) * column + MARGIN,
            (MARGIN + HEIGHT) * row + MARGIN,
            WIDTH,
            HEIGHT
        )
        pygame.event.pump()

    # -------------------------------------
    ### MAZE CREATION ALGORITHMS ###

    # randomized Prim's algorithm for creating random mazes
    def prim(mazearray=False, start_point=False, visualise=VISUALISE):

        # If a maze isn't input, we just create a grid full of walls
        if not mazearray:
            mazearray = []
            for row in range(ROWS):
                mazearray.append([])
                for column in range(ROWS):
                    mazearray[row].append(Node('wall'))
                    if visualise:
                        draw_square(row, column, grid=mazearray)

        n = len(mazearray) - 1

        if not start_point:
            start_point = (random.randrange(0, n, 2),
                           random.randrange(0, n, 2))
        #     START_POINT = start_point
        # mazearray[start_point[0]][start_point[1]].update(nodetype='start')

        if visualise:
            draw_square(start_point[0], start_point[1], grid=mazearray)
            pygame.display.flip()

        walls = set([])

        neighbours = get_neighbours(start_point, n)

        for neighbour, ntype in neighbours:
            if mazearray[neighbour[0]][neighbour[1]].nodetype == 'wall':
                walls.add(neighbour)
                # walls.append(neighbour)

        # NOTE: While there are walls in the list:
        # Pick a random wall from the list. If only one of the cells that the wall divides is visited, then:
        # # Make the wall a passage and mark the unvisited cell as part of the maze.
        # # Add the neighboring walls of the cell to the wall list.
        # Remove the wall from the list.
        while len(walls) > 0:
            wall = random.choice(tuple(walls))
            wall_neighbours = get_neighbours(wall, n)
            neighbouring_walls = set()
            pcount = 0
            for wall_neighbour, ntype in wall_neighbours:
                if wall_neighbour == (start_point or END_POINT):
                    continue
                if mazearray[wall_neighbour[0]][wall_neighbour[1]].nodetype != 'wall':
                    pcount += 1
                else:
                    neighbouring_walls.add(wall_neighbour)

            if pcount <= 1:
                mazearray[wall[0]][wall[1]].update(nodetype='blank')
                if visualise:
                    draw_square(wall[0], wall[1], mazearray)
                    update_square(wall[0], wall[1])
                    time.sleep(0.000001)

                walls.update(neighbouring_walls)

            walls.remove(wall)

        mazearray[END_POINT[0]][END_POINT[1]].update(nodetype='end')
        mazearray[START_POINT[0]][START_POINT[1]].update(nodetype='start')

        return mazearray

    # randomized Prim's algorithm for creating random mazes
    # This version maintains the traditional "maze" look, where a route cannot
    # be diagonally connected to another point on the route
    def better_prim(mazearray=False, start_point=False, visualise=VISUALISE):

        # If a maze isn't input, we just create a grid full of walls
        if not mazearray:
            mazearray = []
            for row in range(ROWS):
                mazearray.append([])
                for column in range(ROWS):
                    if row % 2 != 0 and column % 2 != 0:
                        mazearray[row].append(Node('dormant'))
                    else:
                        mazearray[row].append(Node('wall'))
                    if visualise:
                        draw_square(row, column, grid=mazearray)

        n = len(mazearray) - 1

        if not start_point:
            start_point = (random.randrange(1, n, 2),
                           random.randrange(1, n, 2))
            mazearray[start_point[0]][start_point[1]].update(nodetype='blank')

        if visualise:
            draw_square(start_point[0], start_point[1], grid=mazearray)
            pygame.display.flip()

        walls = set()

        starting_walls = get_neighbours(start_point, n)

        for wall, ntype in starting_walls:
            if mazearray[wall[0]][wall[1]].nodetype == 'wall':
                walls.add(wall)

        # NOTE: While there are walls in the list (set):
        # Pick a random wall from the list. If only one of the cells that the wall divides is visited, then:
        # # Make the wall a passage and mark the unvisited cell as part of the maze.
        # # Add the neighboring walls of the cell to the wall list.
        # Remove the wall from the list.
        while len(walls) > 0:
            wall = random.choice(tuple(walls))
            visited = 0
            add_to_maze = []

            for wall_neighbour, ntype in get_neighbours(wall, n):
                if mazearray[wall_neighbour[0]][wall_neighbour[1]].nodetype == 'blank':
                    visited += 1

            if visited <= 1:
                mazearray[wall[0]][wall[1]].update(nodetype='blank')

                if visualise:
                    draw_square(wall[0], wall[1], mazearray)
                    update_square(wall[0], wall[1])
                    time.sleep(0.0001)

                # NOTE: A 'dormant' node (below) is a different type of node I had to create for this algo
                # otherwise the maze generated doesn't look like a traditional maze.
                # Every dormant eventually becomes a blank node, while the regular walls
                # sometimes become a passage between blanks and are sometimes left as walls
                for neighbour, ntype in get_neighbours(wall, n):
                    if mazearray[neighbour[0]][neighbour[1]].nodetype == 'dormant':
                        add_to_maze.append((neighbour[0], neighbour[1]))

                if len(add_to_maze) > 0:
                    cell = add_to_maze.pop()
                    mazearray[cell[0]][cell[1]].update(nodetype='blank')

                    if visualise:
                        draw_square(cell[0], cell[1], mazearray)
                        update_square(cell[0], cell[1])
                        time.sleep(0.0001)

                    for cell_neighbour, ntype in get_neighbours(cell, n):
                        if mazearray[cell_neighbour[0]][cell_neighbour[1]].nodetype == 'wall':
                            walls.add(cell_neighbour)

            walls.remove(wall)

        mazearray[END_POINT[0]][END_POINT[1]].update(nodetype='end')
        mazearray[START_POINT[0]][START_POINT[1]].update(nodetype='start')

        return mazearray

    # NOTE: This is for use in the recursive division function
    # it is to avoid creating a gap where there will ultimately be an intersection
    # of perpendicular walls, creating an unsolveable maze
    # TODO: generalise this
    def gaps_to_offset():
        return [x for x in range(2, ROWS, 3)]

    # Recursive division algorithm
    def recursive_division(chamber=None, visualise=VISUALISE, gaps_to_offset=gaps_to_offset(), halving=True):

        sleep = 0.001
        sleep_walls = 0.001

        # When no "chamber" is input,we are starting with the base grid
        if chamber == None:
            chamber_width = len(grid)
            chamber_height = len(grid[1])
            chamber_left = 0
            chamber_top = 0
        else:
            chamber_width = chamber[2]
            chamber_height = chamber[3]
            chamber_left = chamber[0]
            chamber_top = chamber[1]

        if halving:
            x_divide = int(chamber_width/2)
            y_divide = int(chamber_height/2)

        if chamber_width < 3:
            pass
        else:
            # draw x wall
            for y in range(chamber_height):
                grid[chamber_left + x_divide][chamber_top +
                                              y].update(nodetype='wall')
                draw_square(chamber_left + x_divide, chamber_top + y)
                if visualise:
                    update_square(chamber_left + x_divide, chamber_top + y)
                    time.sleep(sleep_walls)

        if chamber_height < 3:
            pass
        else:
            # draw y wall
            for x in range(chamber_width):
                grid[chamber_left + x][chamber_top +
                                       y_divide].update(nodetype='wall')
                draw_square(chamber_left + x, chamber_top + y_divide)
                if visualise:
                    update_square(chamber_left + x, chamber_top + y_divide)
                    time.sleep(sleep_walls)

        # Base case: stop dividing
        if chamber_width < 3 and chamber_height < 3:
            return

        # define the 4 new chambers (left, top, width, height)

        top_left = (chamber_left,                  chamber_top,
                    x_divide,                       y_divide)
        top_right = (chamber_left + x_divide + 1,   chamber_top,
                     chamber_width - x_divide - 1,   y_divide)
        bottom_left = (chamber_left,                  chamber_top + y_divide + 1,
                       x_divide,                       chamber_height - y_divide - 1)
        bottom_right = (chamber_left + x_divide + 1,   chamber_top + y_divide + 1,
                        chamber_width - x_divide - 1,   chamber_height - y_divide - 1)

        chambers = (top_left, top_right, bottom_left, bottom_right)

        # define the 4 walls (of a + symbol) (left, top, width, height)

        left = (chamber_left,                     chamber_top +
                y_divide,      x_divide,                       1)
        right = (chamber_left + x_divide + 1,      chamber_top +
                 y_divide,      chamber_width - x_divide - 1,   1)
        top = (chamber_left + x_divide,          chamber_top,
               1,                              y_divide)
        bottom = (chamber_left + x_divide,          chamber_top + y_divide + 1,
                  1,                              chamber_height - y_divide - 1)

        walls = (left, right, top, bottom)

        gaps = 3
        for wall in random.sample(walls, gaps):
            # print(wall)
            if wall[3] == 1:
                x = random.randrange(wall[0], wall[0]+wall[2])
                y = wall[1]
                if x in gaps_to_offset and y in gaps_to_offset:
                    if wall[2] == x_divide:
                        x -= 1
                    else:
                        x += 1
                if x >= ROWS:
                    x = ROWS - 1
            else:  # the wall is horizontal
                x = wall[0]
                y = random.randrange(wall[1], wall[1]+wall[3])
                if y in gaps_to_offset and x in gaps_to_offset:
                    if wall[3] == y_divide:
                        y -= 1
                    else:
                        y += 1
                if y >= ROWS:
                    y = ROWS-1
            grid[x][y].update(nodetype="blank")
            draw_square(x, y)
            if visualise:
                update_square(x, y)
                time.sleep(sleep)

        # recursively apply the algorithm to all chambers
        for num, chamber in enumerate(chambers):
            recursive_division(chamber)

    # -------------------------------------------------------------------
    ### -------------------PATHFINDING ALGORITHMS------------------ ###

    # Dijkstra's pathfinding algorithm, with the option to switch to A* by adding a heuristic of expected distance to end node
    def dijkstra(mazearray, start_point=(0, 0), goal_node=False, display=pygame.display, visualise=VISUALISE, diagonals=DIAGONALS, astar=False):

        heuristic = 0
        distance = 0

        # Get the dimensions of the (square) maze
        n = len(mazearray) - 1

        # Create the various data structures with speed in mind
        visited_nodes = set()
        unvisited_nodes = set([(x, y) for x in range(n+1) for y in range(n+1)])
        queue = AStarQueue()

        queue.push(distance+heuristic, distance, start_point)
        v_distances = {}

        # If a goal_node is not set, put it in the bottom right (1 square away from either edge)
        if not goal_node:
            goal_node = (n, n)
        priority, current_distance, current_node = queue.pop()
        start = time.perf_counter()

        # Main algorithm loop
        while current_node != goal_node and len(unvisited_nodes) > 0:
            if current_node in visited_nodes:
                if len(queue.show()) == 0:
                    return False
                else:
                    priority, current_distance, current_node = queue.pop()
                    continue

            # Call to check neighbours of the current node
            for neighbour in get_neighbours(current_node, n, diagonals=diagonals):
                neighbours_loop(
                    neighbour,
                    mazearr=mazearray,
                    visited_nodes=visited_nodes,
                    unvisited_nodes=unvisited_nodes,
                    queue=queue,
                    v_distances=v_distances,
                    current_node=current_node,
                    current_distance=current_distance,
                    astar=astar
                )

            # When the current node is checked, add and remove appropriately
            visited_nodes.add(current_node)
            unvisited_nodes.discard(current_node)

            # Add the distance to the visited distances dictionary (used for traceback)
            v_distances[current_node] = current_distance

            # Pygame part: visited nodes mark visited nodes as green
            if (current_node[0], current_node[1]) != start_point:
                mazearray[current_node[0]][current_node[1]].update(
                    is_visited=True)
                draw_square(current_node[0], current_node[1], grid=mazearray)

                # If we want to visualise it (rather than run instantly)
                # then we update the grid with each loop
                if visualise:
                    update_square(current_node[0], current_node[1])
                    time.sleep(0.000001)

            # If there are no nodes in the queue then we return False (no path)
            if len(queue.show()) == 0:
                return False
            # Otherwise we take the minimum distance as the new current node
            else:
                priority, current_distance, current_node = queue.pop()

        # TODO: update this line so it works properly
        v_distances[goal_node] = current_distance + \
            (1 if not diagonals else 2**0.5)
        visited_nodes.add(goal_node)

        # Draw the path back from goal node to start node
        trace_back(goal_node, start_point, v_distances, visited_nodes,
                   n, mazearray, diags=diagonals, visualise=visualise)

        end = time.perf_counter()
        num_visited = len(visited_nodes)
        time_taken = end-start

        # Print timings
        print(
            f"Program finished in {time_taken:.4f} seconds after checking {num_visited} nodes. That is {time_taken/num_visited:.8f} seconds per node.")

        # The commented out line returns the distance to the end node
        return False if v_distances[goal_node] == float('inf') else v_distances[goal_node]
        # return False if v_distances[goal_node] == float('inf') else True

    # (DIJKSTRA/A*) loop to check all neighbours of the "current node"

    def neighbours_loop(neighbour, mazearr, visited_nodes, unvisited_nodes, queue, v_distances, current_node, current_distance, diags=DIAGONALS, astar=False):

        neighbour, ntype = neighbour

        heuristic = 0

        if astar:
            heuristic += abs(END_POINT[0] - neighbour[0]) + \
                abs(END_POINT[1] - neighbour[1])
            heuristic *= 1  # if this goes above 1 then the shortest path is not guaranteed, but the attempted route becomes more direct

        # If the neighbour has already been visited
        if neighbour in visited_nodes:
            pass
        elif mazearr[neighbour[0]][neighbour[1]].nodetype == 'wall':
            visited_nodes.add(neighbour)
            unvisited_nodes.discard(neighbour)
        else:
            modifier = mazearr[neighbour[0]][neighbour[1]].distance_modifier
            if ntype == "+":
                queue.push(current_distance+(1*modifier)+heuristic,
                           current_distance+(1*modifier), neighbour)
            elif ntype == "x":
                queue.push(current_distance+((2**0.5)*modifier)+heuristic,
                           current_distance+((2**0.5)*modifier), neighbour)

    # (DIJKSTRA/A*) trace a path back from the end node to the start node after the algorithm has been run
    def trace_back(goal_node, start_node, v_distances, visited_nodes, n, mazearray, diags=False, visualise=VISUALISE):

        # begin the list of nodes which will represent the path back, starting with the end node
        path = [goal_node]

        current_node = goal_node

        # Set the loop in motion until we get back to the start
        while current_node != start_node:
            # Start an empty priority queue for the current node to check all neighbours
            neighbour_distances = PriorityQueue()

            neighbours = get_neighbours(current_node, n, diags)

            # Had some errors during testing, not sure if this is still necessary
            try:
                distance = v_distances[current_node]
            except Exception as e:
                print(e)

            # For each neighbour of the current node, add its location and distance
            # to a priority queue
            for neighbour, ntype in neighbours:
                if neighbour in v_distances:
                    distance = v_distances[neighbour]
                    neighbour_distances.push(distance, neighbour)

            # Pop the lowest value off; that is the next node in our path
            distance, smallest_neighbour = neighbour_distances.pop()
            mazearray[smallest_neighbour[0]
                      ][smallest_neighbour[1]].update(is_path=True)

            # Update pygame display
            draw_square(smallest_neighbour[0],
                        smallest_neighbour[1], grid=mazearray)
            # update_square(smallest_neighbour[0],smallest_neighbour[1])

            path.append(smallest_neighbour)
            current_node = smallest_neighbour

        pygame.display.flip()

        mazearray[start_node[0]][start_node[1]].update(is_path=True)

    def xfs(mazearray, start_point, goal_node, x, display=pygame.display, visualise=VISUALISE, diagonals=DIAGONALS):
        '''
        NOTE:This is a function where you choose x='b' or x='d' to run bfs (breadth-first search) or
        dfs (depth-first search) on your chosen mazearray (grid format), with chosen start_point (x,y)
        and chosen goal_node (x,y)
        '''
        assert x == 'b' or x == 'd', "x should equal 'b' or 'd' to make this bfs or dfs"

        # Get the dimensions of the (square) maze
        n = len(mazearray) - 1

        # Create the various data structures with speed in mind
        mydeque = deque()
        mydeque.append(start_point)
        visited_nodes = set([])
        path_dict = {start_point: None}

        # Main algorithm loop
        while len(mydeque) > 0:
            if x == 'd':
                current_node = mydeque.pop()
            elif x == 'b':
                current_node = mydeque.popleft()

            if current_node == goal_node:
                # Trace back to start using path_dict
                path_node = goal_node
                while True:
                    path_node = path_dict[path_node]
                    mazearray[path_node[0]][path_node[1]].update(is_path=True)
                    draw_square(path_node[0], path_node[1], grid=mazearray)
                    if visualise:
                        update_square(path_node[0], path_node[1])
                    if path_node == start_point:
                        return True

            if mazearray[current_node[0]][current_node[1]].nodetype == 'wall':
                continue

            if current_node not in visited_nodes:
                visited_nodes.add(current_node)
                mazearray[current_node[0]][current_node[1]].update(
                    is_visited=True)
                draw_square(current_node[0], current_node[1], grid=mazearray)
                if visualise:
                    update_square(current_node[0], current_node[1])
                    time.sleep(0.001)

                for neighbour, ntype in get_neighbours(current_node, n):
                    mydeque.append(neighbour)
                    # Used for tracing back
                    if neighbour not in visited_nodes:
                        path_dict[neighbour] = current_node

        pygame.display.flip()
        return False

    grid[START_POINT[0]][START_POINT[1]].update(nodetype='start')
    grid[END_POINT[0]][END_POINT[1]].update(nodetype='end')
    # Update the GUI

    def update_gui(draw_background=True, draw_buttons=True, draw_grid=True):

        if draw_background:
            # Draw a black background to set everything on
            screen.fill(BLACK)
            pass

        if draw_buttons:
            visToggleButton = Button(GREY, SCREEN_WIDTH/3, SCREEN_WIDTH + BUTTON_HEIGHT*2,
                                     SCREEN_WIDTH/3, BUTTON_HEIGHT, f"Visualise: {str(VISUALISE)}")
            # Draw Button below grid
            dijkstraButton.draw(screen, (0, 0, 0))
            dfsButton.draw(screen, (0, 0, 0))
            bfsButton.draw(screen, (0, 0, 0))
            astarButton.draw(screen, (0, 0, 0))
            resetButton.draw(screen, (0, 0, 0))
            mazeButton.draw(screen, (0, 0, 0))
            altPrimButton.draw(screen, (0, 0, 0))
            recursiveMazeButton.draw(screen, (0, 0, 0))
            terrainButton.draw(screen, (0, 0, 0))
            visToggleButton.draw(screen, (0, 0, 0))

        if draw_grid:
            # Draw the grid
            for row in range(ROWS):
                for column in range(ROWS):
                    color = grid[row][column].color
                    draw_square(row, column)

    # --- Drawing code should go here
    update_gui()

    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # --- Limit to 60 frames per second
    clock.tick(60)

# Close the window and quit.
pygame.quit()
