import random
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PyQt6.QtCore import *

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
    num_flagged_cells = 0
    first_move_made = False
    def __init__(self, normal_color, hover_color, size, is_bomb = False):
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
        self.is_pressed = True
        if self.flagged():
            self.is_flagged = False
            Tile.num_flagged_cells -= 1
        self.update()
        
    def is_exposed(self):
        return self.is_pressed
    
    def flagged(self):
        return self.is_flagged
    
    def hoverEnterEvent(self, event):
        self.is_hovering = True 
        self.update()
    
    def hoverLeaveEvent(self, event):
        self.is_hovering = False
        self.update()

    def boundingRect(self):
        return QRectF(0, 0, self.size, self.size)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.is_hovering:
            painter.fillRect(0, 0, self.size, self.size, QBrush(self.hover_color))
        else: 
            painter.fillRect(0, 0, self.size, self.size, QBrush(self.normal_color))
        
        if self.is_flagged:
            painter.drawPixmap(0, 0, self.size, self.size, QPixmap(FLAG_FILE_PATH))        
    
    def mousePressEvent(self, event):
        """Handler for mouse press events. Left clicking a cell makes it alive
        and right clicking a cell kills it

        e -- A QGraphicsSceneMouseEvent to handle
        """
        if event.button() == Qt.MouseButton.RightButton and not self.is_exposed():
            self.is_flagged = not self.is_flagged
            # fancy value manipulation to basically subtract 1 if it is flagged, and add 1 if it is unflagged
            Tile.num_flagged_cells += 2 * self.is_flagged - 1
            self.update()
        elif event.button() == Qt.MouseButton.LeftButton and self.is_flagged:
            return 

class BombTile(Tile):
    def __init__(self, normal_color, highlight_color, size):
        super().__init__(normal_color, highlight_color, size, True)
        self.bomb_color = random.choice(BOMB_COLORS)
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton and not self.is_flagged and not self.is_pressed:
            Tile.first_move_made = True
            self.is_pressed = True
            self.update()
    
    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        if self.is_pressed:
            painter.fillRect(0, 0, self.size, self.size, QBrush(self.bomb_color))
            painter.setBrush(QBrush(self.bomb_color.darker()))
            painter.setPen(QPen(self.bomb_color.darker()))
            painter.drawEllipse(QPoint(self.size // 2, self.size // 2), self.size // 3, self.size // 3)

class SafeTile(Tile):
    def __init__(self, normal_color, highlight_color, exposed_color, size):
        super().__init__(normal_color, highlight_color, size)
        self.num_bombs = 0 # number of neighboring bombs
        self.exposed_color = exposed_color
        self.draw_x = False
    
    def get_num_bombs(self):
        return self.num_bombs
    
    def set_num_bombs(self, num_bombs):
        self.num_bombs = num_bombs
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton and not self.is_flagged \
            and not self.is_pressed and not self.draw_x:
            Tile.first_move_made = True
            self.is_pressed = True
            self.update()
    
    def draw_X(self):
        self.draw_x = True
        self.is_flagged = False
        self.update()
            
    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        if self.draw_x:
            pen = QPen(ERROR)
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(0, 0, self.size, self.size)
            painter.drawLine(0, self.size, self.size, 0)
        if self.is_pressed:
            painter.fillRect(0, 0, self.size, self.size, QBrush(self.exposed_color))

            if self.num_bombs != 0:
                font = painter.font()
                font.setPixelSize(self.size)
                painter.setFont(font)

                painter.setPen(QPen(NUMBER_COLORS[self.num_bombs - 1]))
                painter.drawText(0, 0, self.size, self.size, Qt.AlignmentFlag.AlignCenter, str(self.num_bombs))
