import random
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PyQt6.QtCore import *

"""Global Variables:

BOMB_COLORS: A set of colors to use when exploding the bombs. These colors are 
to be selected randomly from.

NUMBER_COLORS: The colors to use when exposing safe tiles. Blue should be used
if the tile is bordering one bomb, green should be used if the tile is bordering 
two bombs, red should be used if the tile is bordering three bombs, and so on. 

FLAG_FILE_PATH: The image file to use when the user wants to flag a tile.

ERROR: The color to use when crossing out the incorrectly flagged tiles, after the 
player has lost the game.
"""

BOMB_COLORS = [
    QColor("#4D9DE0"),
    QColor("#E1BC29"),
    QColor("#3BB273"),
    QColor("#7768AE"),
    QColor("#E15554"),
]
NUMBER_COLORS = [
    Qt.GlobalColor.blue,
    Qt.GlobalColor.green,
    Qt.GlobalColor.red,
    Qt.GlobalColor.darkMagenta,
    Qt.GlobalColor.black,
    Qt.GlobalColor.gray,
    Qt.GlobalColor.darkRed,
    Qt.GlobalColor.cyan,
]
FLAG_FILE_PATH = "images/flag.png"
ERROR = Qt.GlobalColor.red

class Tile(QGraphicsItem):
    """A Tile object represents a single tile in the game of minesweeper.

    Class Attributes:
        Tile.num_flagged_cells -- the number of flagged cells on the board
        Tile.first_move_made -- a boolean that represents whether or not the player
        has made the first move on the board already
    Instance Attributes:
        normal_color -- the color to use when the user is not hovering over the tile,
        and the tile has not been exposed yet. That is, the color with which to display
        the tile at the start of the game, until it has been interacted with. 
        hover_color -- the color to use when the user has not interacted with the tile,
        but is hovering over it. 
        size -- the size of the tile in pixels
        is_hovering -- a boolean representing when the user is hovering over the tile
        is_bomb -- a boolean representing whether the current tile is a bomb or not
        is_flagged -- a boolean representing whether or not the tile has been flagged
        is_pressed -- a boolean representing whether the tile has been pressed or not. In
        the case that it has been pressed, it should be exposed. 
    """
    num_flagged_cells = 0
    first_move_made = False

    def __init__(self, normal_color, hover_color, size, is_bomb = False):
        """Create a Tile with normal color NORMAL_COLOR, hover color HOVER_COLOR, of size SIZE,
        and a boolean IS_BOMB dictating whether or not the current tile is a bomb. 

        normal_color -- A QColor; the color with which to display the tile, before it has been
        interacted with. 
        hover_color -- A QColor; the color with which to display the tile, after a mouse hover 
        event.
        size -- An integer; the size in pixels of the tile
        is_bomb -- A boolean; represents whether or not the current tile is a bomb 
        """
        super().__init__()
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.size = size
        self.is_hovering = False
        self.is_bomb = is_bomb
        self.is_flagged = False 
        self.is_pressed = False
        self.setAcceptHoverEvents(True)
    
    def force_expose(self):
        """Exposes tile by setting self.is_pressed to True, and calling a repaint."""
        self.is_pressed = True
        # If the tile is flagged, then it will be unflagged, and the number of 
        # flagged cells, which is kept track of by the class attribute will be
        # reduced by 1. 
        if self.flagged():
            self.is_flagged = False
            Tile.num_flagged_cells -= 1
        self.update()
    
    def is_safe(self):
        """Method to check if this tile is safe or a bomb tile.

        Returns:
            A boolean that represents whether or not the current tile is safe.
        """
        return not self.is_bomb
        
    def is_exposed(self):
        """Method to check if this tile has been pressed.

        Returns:
            A boolean that represents whether or not the current tile has been pressed.
        """
        return self.is_pressed
    
    def flagged(self):
        """Method to check if this tile is safe.

        Returns:
            A boolean that represents whether or not the current tile has been pressed.
        """
        return self.is_flagged
    
    def hoverEnterEvent(self, event):
        """Overrides super().hoverEnterEvent by setting self.is_hovering to True and calling repaint.
        
        Args:
            event -- A QGraphicsSceneMouseEvent to handle
        """
        self.is_hovering = True 
        self.update()
    
    def hoverLeaveEvent(self, event):
        """Overrides super().hoverLeaveEvent by setting self.is_hovering to False and calling repaint.
        
        Args:
            event -- A QGraphicsSceneMouseEvent to handle
        """
        self.is_hovering = False
        self.update()

    def boundingRect(self):
        """Implements the virtual function boundingRect needed to implement QGraphicsItem.

        Returns:
            A QRectF object that bounds the graphic scene to be painted.
        """
        return QRectF(0, 0, self.size, self.size)

    def paint(self, painter, option, widget = None):
        """Implements the virtual function paint needed to implement QGraphicsItem
        
        Args:
            painter: A QPainter; the painter to draw the tile
            option: A QStyleOptionGraphicsItem; controls the style of the painter, including 
            the level of detail.
            widget: A QWidget; the widget to draw the tile on. Since the tile will be painted
            on QGraphicsScene, the default argument will be None. 
        """
        # Vectorizes graphics
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.is_hovering:
            painter.fillRect(0, 0, self.size, self.size, QBrush(self.hover_color))
        else: 
            painter.fillRect(0, 0, self.size, self.size, QBrush(self.normal_color))
        
        if self.is_flagged:
            painter.drawPixmap(0, 0, self.size, self.size, QPixmap(FLAG_FILE_PATH))        
    
    def mousePressEvent(self, event):
        """Handler for mouse press events. Calls repaint after processing events.

        Args:
            event -- A QGraphicsSceneMouseEvent to handle
        """
        # Right click to flag a tile
        if event.button() == Qt.MouseButton.RightButton and not self.is_exposed():
            self.is_flagged = not self.is_flagged
            # Fancy value manipulation to basically subtract 1 if it is flagged, and add 1 if it is unflagged
            Tile.num_flagged_cells += 2 * self.is_flagged - 1
            self.update()
        elif event.button() == Qt.MouseButton.LeftButton and self.is_flagged:
            # Don't do anything if the user left clicks a flagged tile
            return 

class BombTile(Tile):
    """A BombTile object representing a bomb tile in a game of minesweeper.

    Attributes:
    bomb_color -- A randomly selected color to use for the bomb, when the tile is 
    left clicked. 
    """
    def __init__(self, normal_color, highlight_color, size):
        """Create a BombTile with normal color NORMAL_COLOR, hover color HIGHLIGHT_COLOR of size SIZE.

        normal_color -- A QColor; the color with which to display the tile, before it has been
        interacted with. 
        highlight_color -- A QColor; the color with which to display the tile, after a mouse hover 
        event.
        size -- An integer; the size in pixels of the tile
        """
        super().__init__(normal_color, highlight_color, size, True)
        self.bomb_color = random.choice(BOMB_COLORS)
    
    def mousePressEvent(self, event):
        """Handler for mouse press events. Overrides super().mousePressEvent.

        Args:
            event -- A QGraphicsSceneMouseEvent to handle
        """
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton and not self.is_flagged and not self.is_pressed:
            # The moment the user left clicks a box, the first move has been made
            Tile.first_move_made = True
            # If the user has not flagged this tile, and left clicked it, then it has been pressed
            # and so we must set is_pressed to True and call a repaint.
            self.is_pressed = True
            self.update()
    
    def paint(self, painter, option, widget = None):
        """Overrides super().paint in order to "explode" the tile after the user left clicks the tile. 
        
        Args:
            painter: A QPainter; the painter to draw the tile
            option: A QStyleOptionGraphicsItem; controls the style of the painter, including 
            the level of detail.
            widget: A QWidget; the widget to draw the tile on. Since the tile will be painted
            on QGraphicsScene, the default argument will be None. 
        """
        # Code to "explode" the tile after the user presses on it
        if self.is_pressed:
            painter.fillRect(0, 0, self.size, self.size, QBrush(self.bomb_color))
            painter.setBrush(QBrush(self.bomb_color.darker()))
            painter.setPen(QPen(self.bomb_color.darker()))
            painter.drawEllipse(QPoint(self.size // 2, self.size // 2), self.size // 3, self.size // 3)
        # If the tile is not pressed, then the super().paint method handles everything correctly
        else:
            super().paint(painter, option, widget)

class SafeTile(Tile):
    """A SafeTile object representing a non-bomb tile in a game of minesweeper.

    Attributes:
    num_bombs -- the number of bombs surrounding this tile in the game
    exposed_color -- the color to use for the background when exposing the tile
    draw_x -- a boolean that tells the paint function when to cross out the tile.
    To be used at the end of the game, where incorrectly flagged cells are crossed out. 
    """
    def __init__(self, normal_color, highlight_color, exposed_color, size):
        """Create a SafeTile with normal color NORMAL_COLOR, hover color HIGHLIGHT_COLOR, exposed color
        EXPOSED_COLOR of size SIZE.

        normal_color -- A QColor; the color with which to display the tile, before it has been
        interacted with. 
        highlight_color -- A QColor; the color with which to display the tile, after a mouse hover 
        event.
        exposed_color -- A QColor; the color with which to display the tile, after it has been 
        pressed (i.e. exposed)
        size -- An integer; the size in pixels of the tile
        """
        super().__init__(normal_color, highlight_color, size)
        self.num_bombs = 0 # number of neighboring bombs
        self.exposed_color = exposed_color
        self.draw_x = False
    
    def get_num_bombs(self):
        """Gives the number of bombs surrounding this tile
        
        Returns:
            An integer; the number of bombs surrounding this tile
        """
        return self.num_bombs
    
    def set_num_bombs(self, num_bombs):
        """Sets the number of bombs to num_bombs
        
        Args:
            num_bombs -- the number of bombs to set self.num_bombs to
        """
        self.num_bombs = num_bombs
        
    def crossout(self):
        """Sets self.draw_x to True and calls a repaint so that this cell will be crossed out."""
        self.draw_x = True
        self.is_flagged = False
        self.update()
    
    def mousePressEvent(self, event):
        """Handler for mouse press events. Overrides super().mousePressEvent.

        Args:
            event -- A QGraphicsSceneMouseEvent to handle
        """
        super().mousePressEvent(event)
        # If you left click this tile, and it is not flagged, has not been pressed before, and is not
        # crossed out, then call a repaint after updating some attributes
        if event.button() == Qt.MouseButton.LeftButton and not self.is_flagged \
            and not self.is_pressed and not self.draw_x:
            # The moment the user left clicks a tile, the game has begun 
            Tile.first_move_made = True
            self.is_pressed = True
            self.update()
            
    def paint(self, painter, option, widget = None):
        """Overrides super().paint in order to expose a tile, or cross it out according to the instance
        variables.
        
        Args:
            painter: A QPainter; the painter to draw the tile
            option: A QStyleOptionGraphicsItem; controls the style of the painter, including 
            the level of detail.
            widget: A QWidget; the widget to draw the tile on. Since the tile will be painted
            on QGraphicsScene, the default argument will be None. 
        """
        super().paint(painter, option, widget)
        # If the self.draw_x flag is true, then cross out the tile
        if self.draw_x:
            pen = QPen(ERROR)
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(0, 0, self.size, self.size)
            painter.drawLine(0, self.size, self.size, 0)
        # If the tile has been pressed, then it has been exposed, and we should reveal how many bombs
        # neighbor this tile.
        elif self.is_pressed:
            painter.fillRect(0, 0, self.size, self.size, QBrush(self.exposed_color))
            # If the number of bombs is zero, don't display any text
            if self.num_bombs != 0:
                font = painter.font()
                font.setPixelSize(self.size)
                painter.setFont(font)
                # Used to color code the numbers
                painter.setPen(QPen(NUMBER_COLORS[self.num_bombs - 1]))
                painter.drawText(0, 0, self.size, self.size, Qt.AlignmentFlag.AlignCenter, str(self.num_bombs))
