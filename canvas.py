import random
from collections import deque
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QColor
from PyQt6.QtCore import *
from tiles import *

"""Global Variables:

UNEXPOSED_DARK: Dark color to use before tile has been revealed
UNEXPOSED_LIGHT: Light color to use before tile has been revealed
UNEXPOSED_HIGHLIGHT: The hover color for the tiles.
EXPOSED_DARK: Dark color to use when a tile has been revealed
EXPOSED_LIGHT: Light color to use when a tile has been revealed
"""

UNEXPOSED_DARK = QColor("#D78521")
UNEXPOSED_LIGHT = QColor("#F2D398")
UNEXPOSED_HIGHLIGHT = QColor("#E6B062")
EXPOSED_DARK = QColor("#D5DBF0")
EXPOSED_LIGHT = QColor("#E8EBF7")

class Canvas(QGraphicsScene):
    """A Canvas object that represents the board of minesweeper. 
    
    width -- the number of tiles wide the board should be
    height -- the number of tiles high the board should be
    num_bombs -- the number of bombs on the board
    tile_size -- the size of each tile on the board
    grid -- a 2D array storing Tile references for each position on the grid
    game_over -- a boolean that tracks if the game is over
    game_won -- a boolean tha tracks if the game is won
    safes -- a deque consisting of all incorrectly flagged tiles. Note that
    this attribute is only ever computed when the player loses the game
    bombs -- a deque consisting of all bomb tiles that were unmarked. Note that
    this attribute is only ever computer when the player loses the game. 
    """
    def __init__(self, width, height, tile_size, num_bombs):
        """Create a Canvas object that is WIDTH tiles wide, HEIGHT tiles high, where each tile has 
        size TILE_SIZE, and the grid has NUM_BOMB randomly placed bombs.
        
        width -- An integer; number of tiles wide
        height -- An integer; number of tiles high
        tile_size -- An integer; the size of a tile
        num_bombs -- An integer; the number of bombs that should be randomly placed in the grid
        """
        # Reset the class attributes of Tile each time a new Canvas object is initialized.
        # Each time a new Canvas a object is initialized, a new game has been started so these
        # variables must be reset for the current game.
        Tile.num_flagged_cells = 0
        Tile.first_move_made = False

        self.width = width 
        self.height = height 
        self.num_bombs = num_bombs
        self.tile_size = tile_size
        # We will update self.grid to contain the Tile references when we call the self._randomize() method
        self.grid = [ [None] * width for i in range(height) ]
        self.game_over = False
        self.game_won = False
        # Initialize the scene to be width * tile_size pixels wide and height * tile_size pixels tall
        super().__init__(0, 0, width * tile_size, height * tile_size)
        # Randomize the tiles, and set the count values for each of the safe tiles
        self._randomize()
        self._compute_counts()
        # To be used for self._end_game_sequence()
        self.safes = deque()
        self.bombs = deque()

    def game_finished(self):
        """Returns a boolean on whether or not the game is over
        
        Returns:
            A boolean representing whether or not the game is over
        """
        return self.game_over
    
    def game_is_won(self):
        """Returns a boolean on whether or not the game has been won
        
        Returns:
            A boolean representing whether or not the game is won
        """
        return self.game_won

    def _compute_count_at(self, x, y):
        """Sets the number of bombs surrounding the tile located at position (X,Y)
        
        Args:
            x -- the x-coordinate of the tile measured from the left
            y -- the y-cooridnate of the tile measured from the top

        Raises:
            IndexError, AssertionError
        """
        assert self.grid[y][x].is_safe(), "Current tile is not safe." 

        dy = [0, 0, 1, 1, 1, -1, -1, -1]
        dx = [-1, 1, -1, 0, 1, -1, 0, 1]
        count = 0
        for i in range(len(dy)):
            y_new = y + dy[i] 
            x_new = x + dx[i]
            if 0 <= x_new and 0 <= y_new and x_new < self.width and y_new < self.height \
                and not self.grid[y_new][x_new].is_safe():
                count += 1
        self.grid[y][x].set_num_bombs(count)

    def _compute_counts(self):
        """Sets the number of bombs surrounding each SafeTile on the board."""
        for i in range(self.width):
            for j in range(self.height):
                if self.grid[j][i].is_safe():
                    self._compute_count_at(i, j)
    
    def _randomize_around_start(self, x, y):
        # TODO: The implementation of this function should essentially guarantee that on the first 
        # move of the game, the user does not pick a bomb. To ensure that the game is actually solvable,
        # it should also ensure that the generated floodfill region is concave, so that some tiles
        # can be immediately flagged as bombs. The arguments X, and Y should represent the location of 
        # the user's first move (here the first move must be a move where the user exposes a tile).  
        pass

    def _randomize(self):
        """Randomly assigns each grid position to a BombTile or a SafeTile while ensuring that
        there are exactly self.num_bombs number of BombTiles."""
        # 1 represents a BombTile, and 0 represents a SafeTile
        indicator = [1] * self.num_bombs + [0] * (self.width * self.height - self.num_bombs)
        random.shuffle(indicator)
        index = 0
        for i in range(self.width):
            for j in range(self.height):
                # The modulo 2 is here to make a chess-board like pattern
                if (i + j) % 2 == 0:
                    if indicator[index] == 0:
                        tile = SafeTile(UNEXPOSED_DARK, UNEXPOSED_HIGHLIGHT, EXPOSED_DARK, self.tile_size)
                    else:
                        tile = BombTile(UNEXPOSED_DARK, UNEXPOSED_HIGHLIGHT, self.tile_size)
                else:
                    if indicator[index] == 0:
                        tile = SafeTile(UNEXPOSED_LIGHT, UNEXPOSED_HIGHLIGHT, EXPOSED_LIGHT, self.tile_size)
                    else:
                        tile = BombTile(UNEXPOSED_LIGHT, UNEXPOSED_HIGHLIGHT, self.tile_size)
                # Add tiles to the QGraphicsScene
                tile.setPos(i * self.tile_size, j * self.tile_size)
                self.addItem(tile)
                self.grid[j][i] = tile
                index += 1
    
    def _floodfill(self, x, y):
        """Exposes every possible safe tile when a tile that is surrounded by zero bombs is selected.
        
        Args:
            x -- the x-coordinate of the tile measured from the left
            y -- the y-cooridnate of the tile measured from the top
        """
        assert self.grid[y][x].is_safe() and self.grid[y][x].get_num_bombs() == 0, "Tile cannot be floodfilled."
        # Just a standard DFS implementation 
        fringe = deque()
        fringe.append((x, y))
        visited = set()
        while not len(fringe) == 0:
            xtop, ytop = fringe.pop()
            if (xtop, ytop) in visited:
                continue
            self.grid[ytop][xtop].force_expose()
            visited.add((xtop, ytop))
            if self.grid[ytop][xtop].get_num_bombs() == 0:
                # Add any neighbors to the stack
                dy = [0, 0, 1, 1, 1, -1, -1, -1]
                dx = [-1, 1, -1, 0, 1, -1, 0, 1]
                for i in range(len(dy)):
                    y_new = ytop + dy[i] 
                    x_new = xtop + dx[i]
                    if 0 <= x_new and 0 <= y_new and x_new < self.width and y_new < self.height \
                        and self.grid[y_new][x_new].is_safe():
                        fringe.append((x_new, y_new))
        
    def _get_unmarked_bombs(self):
        """Populates self.bombs with all of the unmarked bombs (i.e. the bombs unknown to the user).
        To be used when the game is lost, and all the bombs need to be exposed."""
        for i in range(self.width):
            for j in range(self.height):
                if not self.grid[j][i].is_safe() and not self.grid[j][i].flagged():
                    self.bombs.append(self.grid[j][i])
        random.shuffle(self.bombs)
    
    def _get_incorrectly_marked_safe(self):
        """Populates self.safes with all of the incorrectly flagged tiles (i.e. the safe tiles that 
        were flagged). To be used when the game is lost, and all the incorrectly flagged tiles 
        need to be exposed."""
        for i in range(self.width):
            for j in range(self.height):
                if self.grid[j][i].is_safe() and self.grid[j][i].flagged():
                    self.safes.append(self.grid[j][i])
        random.shuffle(self.safes)
    
    def _end_game_sequence(self):
        """Force exposes all tiles in self.bombs and self.safes, with bombs being exposed every
        200, 300, or 400 milliseconds and safe tiles being crossed out every 50, 100, or 150 milliseconds.
        The QTimer is used to animate this process."""
        if len(self.bombs) != 0:
            self.bombs.pop().force_expose()
            QTimer.singleShot(random.choice([200, 300, 400]), self._end_game_sequence)
        elif len(self.safes) != 0:
            self.safes.pop().crossout()
            QTimer.singleShot(random.choice([50, 100, 150]), self._end_game_sequence)
                        
    def _disable_mouse_events(self):
        """Disable all tiles from accepting mouse events."""
        for i in range(self.width):
            for j in range(self.height):
                self.grid[j][i].setAcceptHoverEvents(False)
                self.grid[j][i].setActive(False)
                self.grid[j][i].setAcceptedMouseButtons(Qt.MouseButton.NoButton)
    
    def _check_win_condition(self):
        """Checks if the game has been won and updates the self.game_over and self.game_won
        attributes accordingly. Disables mouse events if the game has been won."""
        for i in range(self.width):
            for j in range(self.height):
                # If there is an unexposed safe tile, the game is not over
                if self.grid[j][i].is_safe() and not self.grid[j][i].is_exposed():
                    return 
        self.game_over = True
        self.game_won = True
        self._disable_mouse_events()

    def mousePressEvent(self, event):
        """Handler for mouse press events. Mouse events are also handled here for floodfilling
        and ending the game after it has been won or lost. 

        Args:
            event -- A QGraphicsSceneMouseEvent to handle
        """
        if self.game_over:
            return 
        if event.button() == Qt.MouseButton.LeftButton:
            point = event.buttonDownScenePos(Qt.MouseButton.LeftButton)
            x = int(point.x() // self.tile_size)
            y = int(point.y() // self.tile_size)
            # First, process the event at the Tile level
            self.grid[y][x].mousePressEvent(event)
            # If the user presses a bomb that is not flagged, the game is over
            if not self.grid[y][x].is_safe() and not self.grid[y][x].flagged():
                # Disable mouse events before starting to explode the bombs and cross out
                # incorrectly flagged tiles, since there have been bugs where the user can
                # still click on tiles during self._end_game_sequence()
                self._disable_mouse_events()
                # Populate self.bombs and self.safes
                self._get_unmarked_bombs()
                self._get_incorrectly_marked_safe()
                # Animate the explosions and crossouts
                self._end_game_sequence()
                self.game_over = True
                return 
            # If the user clicks on a safe tile with no bombs, floodfill it 
            elif self.grid[y][x].is_safe() and self.grid[y][x].get_num_bombs() == 0 \
                 and not self.grid[y][x].flagged():
                self._floodfill(x, y)
        # If you right click, then the Tile.mousePressEvent handles it perfectly.
        elif event.button() == Qt.MouseButton.RightButton:
            point = event.buttonDownScenePos(Qt.MouseButton.RightButton)
            x = int(point.x() // self.tile_size)
            y = int(point.y() // self.tile_size)
            self.grid[y][x].mousePressEvent(event)
        # Check if the game has been won after each mouse click
        self._check_win_condition()
    