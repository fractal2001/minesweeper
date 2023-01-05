import random
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QColor
from PyQt6.QtCore import *
from collections import deque
from tiles import *

UNEXPOSED_DARK = QColor("#D78521")
UNEXPOSED_LIGHT = QColor("#F2D398")
UNEXPOSED_HIGHLIGHT = QColor("#E6B062")

EXPOSED_LIGHT = QColor("#E8EBF7")
EXPOSED_DARK = QColor("#D5DBF0")

class Canvas(QGraphicsScene):
    def __init__(self, width, height, tile_size, num_bombs):
        self.width = width 
        self.height = height 
        self.num_bombs = num_bombs
        self.tile_size = tile_size
        super().__init__(0, 0, width * tile_size, height * tile_size)
        self.grid = [ [None] * width for i in range(height) ]
        self.game_over = False
        self.game_won = False

        self.randomize()
        self.compute_counts()

        self.safes = deque()
        self.bombs = deque()
    # y comes from top, x comes from left, but x goes first
    def randomize_around_start(self, x, y):
        pass

    def game_finished(self):
        return self.game_over
    
    def game_is_won(self):
        return self.game_won

    def _compute_count_at(self, x, y):
        assert self.grid[y][x].is_safe(), "Current tile is not safe" 

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

    def compute_counts(self):
        for i in range(self.width):
            for j in range(self.height):
                if self.grid[j][i].is_safe():
                    self._compute_count_at(i, j)

    def randomize(self):
        indicator = [1] * self.num_bombs + [0] * (self.width * self.height - self.num_bombs)
        random.shuffle(indicator)
        index = 0

        for i in range(self.width):
            for j in range(self.height):
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
                tile.setPos(i * self.tile_size, j * self.tile_size)
                self.addItem(tile)
                self.grid[j][i] = tile
                index += 1
    
    def floodfill(self, x, y):
        assert self.grid[y][x].is_safe() and self.grid[y][x].get_num_bombs() == 0
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
                dy = [0, 0, 1, 1, 1, -1, -1, -1]
                dx = [-1, 1, -1, 0, 1, -1, 0, 1]
                for i in range(len(dy)):
                    y_new = ytop + dy[i] 
                    x_new = xtop + dx[i]
                    if 0 <= x_new and 0 <= y_new and x_new < self.width and y_new < self.height \
                        and self.grid[y_new][x_new].is_safe():
                        fringe.append((x_new, y_new))
        
    def _get_unmarked_bombs(self):
        for i in range(self.width):
            for j in range(self.height):
                if not self.grid[j][i].is_safe() and not self.grid[j][i].flagged():
                    self.bombs.append(self.grid[j][i])
        random.shuffle(self.bombs)
    
    def _get_incorrectly_marked_safe(self):
        for i in range(self.width):
            for j in range(self.height):
                if self.grid[j][i].is_safe() and self.grid[j][i].flagged():
                    self.safes.append(self.grid[j][i])
        random.shuffle(self.safes)
    
    def _end_game_sequence(self):
        if len(self.bombs) != 0:
            self.bombs.pop().force_expose()
            QTimer.singleShot(random.choice([200, 300, 400]), self._end_game_sequence)
        elif len(self.safes) != 0:
            self.safes.pop().crossout()
            QTimer.singleShot(random.choice([50, 100, 150]), self._end_game_sequence)
                        
    def _disable_mouse_events(self):
        for i in range(self.width):
            for j in range(self.height):
                self.grid[j][i].setAcceptHoverEvents(False)
                self.grid[j][i].setActive(False)
                self.grid[j][i].setAcceptedMouseButtons(Qt.MouseButton.NoButton)
    
    def check_win_condition(self):
        for i in range(self.width):
            for j in range(self.height):
                if self.grid[j][i].is_safe() and not self.grid[j][i].is_exposed():
                    return 
        self.game_over = True
        self.game_won = True
        self._disable_mouse_events()

    def mousePressEvent(self, event):
        if self.game_over:
            return 
        if event.button() == Qt.MouseButton.LeftButton:
            point = event.buttonDownScenePos(Qt.MouseButton.LeftButton)
            x = int(point.x() // self.tile_size)
            y = int(point.y() // self.tile_size)
            self.grid[y][x].mousePressEvent(event)

            if not self.grid[y][x].is_safe() and not self.grid[y][x].flagged():
                self._disable_mouse_events()

                self._get_unmarked_bombs()
                self._get_incorrectly_marked_safe()

                self._end_game_sequence()

                self.game_over = True
                return 
            elif self.grid[y][x].is_safe() and self.grid[y][x].get_num_bombs() == 0 \
                 and not self.grid[y][x].flagged():
                self.floodfill(x, y)
        elif event.button() == Qt.MouseButton.RightButton:
            point = event.buttonDownScenePos(Qt.MouseButton.RightButton)
            x = int(point.x() // self.tile_size)
            y = int(point.y() // self.tile_size)
            self.grid[y][x].mousePressEvent(event)
        self.check_win_condition()
    
    def update_parameters(self, width, height, tile_size, num_bombs):
        self.__init__(width, height, tile_size, num_bombs)
