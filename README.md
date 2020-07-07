# Pygame Pathfinder

Visualise maze generation and pathfinding algorithms with Pygame.

## Installation

After cloning the repo, you need to set up and activate an virtual enviornment.

To Create and activate your virtual environment:

- On MacOS/Linux:

```bash
virtualenv --no-site-packages env
source env/bin/activate
```

- On Windows:

```bash
virtualenv env
.\env\Scripts\activate
```

Install the required packages:

-pip install -r requirements.txt

### Use the program

got to the program folder and simply run the 'grid.py' file
python grid.py

#### Buttons

Maze/terrain generation buttons are on the right.

###### Grid interaction

Left click to create a wall or move the start and end points.

Hold left <kbd>CTRL</kbd> and left click to create a sticky mud patch (which reduces movement speed to 1/3).

After a pathfinding algorithm has been run you can drag the start/end points around and see the visualisation update instantly for the new path using the algorithm that was last run.

<!-- ## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. -->
