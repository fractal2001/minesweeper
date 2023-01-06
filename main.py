import sys
from canvas import *
from tiles import *
from utils import *
from dialog import *
from stopwatch import *
from PyQt6.QtGui import QFont

"""Global Variables:

MODES: Contains three different difficulties "Easy", "Medium" and "Hard". Each tuple is of the form
(number of tiles wide, number of tiles high, tile size, number of bombs)
ICON_SIZE: Controls the size of all images displayed in the UI
TEXT_SIZE: Controls the size of the font of text in the UI
SCORES_FILE_PATH: The filepath to the high_scores.txt file
FLAG_FILE_PATH: The filepath to the flag icon (to be used for displaying the number of flagged tiles)
TROPHY_FILE_PATH: The filepath to the trophy icon (to be used to display user's best score)
HIGH_SCORES: The current user's high scores, that were stored in SCORES_FILE_PATH
MAX_TIME: The timeout for the timer. This is the worst possible time a player can take. 
"""

MODES = {
    "Easy": (10, 8, 50, 10),
    "Medium" : (18, 14, 46, 40),
    "Hard" : (24, 20, 32, 99),
}
ICON_SIZE = 30
TEXT_SIZE = 15
SCORES_FILE_PATH = "cache/high_scores.txt"
FLAG_FILE_PATH = "images/flag.png"
TIME_FILE_PATH = "images/hourglass.png"
TROPHY_FILE_PATH = "images/trophy.png"
HIGH_SCORES = read_high_scores(SCORES_FILE_PATH)
MAX_TIME = 999

class MainWindow(QMainWindow):
    """A MainWindow object that contains the minesweeper game along with
    a timer, difficulty-setter, and a win/lose dialog box. 
    
    mode -- the difficulty; "Easy", "Medium" or "Hard".
    dialog_displayed -- a boolean that checks if the dialog box is displayed or not. 
    This was used to fix a bug, where when the dialog box was displayed, the user could click
    on the minesweeper game to make the dialog box redraw itself. 
    total_bombs -- the total number of bombs in the game
    scene -- A canvas object containing the minesweeper game
    view -- A QGraphicsView object, which renders self.scene
    scores -- the user's highest scores stored as a dictionary, with times for each category
    watch -- A stopwatch object to track how much time the user has elapsed since the start
    timer_active -- A boolean which checks if self.watch is currently running
    flag_count -- A QLabel object, which displays the number of currently flagged cells
    difficulty_box -- A QComboBox object, which contains the different difficulty modes for 
    the user to select from
    """
    def __init__(self, mode):
        """Create a MainWindow object with difficulty MODE
        
        mode -- the desired difficulty; "Easy", "Medium" or "Hard". 
        """
        super().__init__()
        self.setWindowTitle("Minesweeper")
        self.mode = mode
        self.dialog_displayed = False
        width, height, tile_size, self.total_bombs = MODES[mode]
        self.scene = Canvas(width, height, tile_size, self.total_bombs)
        self.view = QGraphicsView(self.scene)
        self.scores = read_high_scores(SCORES_FILE_PATH)

        # Vectorizes graphics
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)        
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.watch = StopWatch(MAX_TIME, TIME_FILE_PATH, ICON_SIZE, TEXT_SIZE)
        # Don't start the timer immediately
        self.timer_active = False 

        flag_icon = QLabel()
        flag_icon.setPixmap(QPixmap(FLAG_FILE_PATH).scaled(ICON_SIZE, ICON_SIZE))

        # An updating display of the number of flags put down by the user
        font = QFont()
        font.setPointSize(TEXT_SIZE)
        self.flag_count = QLabel()
        self.flag_count.setText("0/" + str(self.total_bombs))
        self.flag_count.setFont(font)

        # The flag_widget consists of the flag icon next to the flag count
        flag_layout = QHBoxLayout()
        flag_layout.addWidget(flag_icon)
        flag_layout.addWidget(self.flag_count)
        flag_layout.setSpacing(8)
        flag_widget = QWidget()
        flag_widget.setLayout(flag_layout)

        # Customizes the difficulty setter box
        self.difficulty_box = QComboBox()
        font.setPointSize(TEXT_SIZE - 2)
        self.difficulty_box.setFont(font)
        self.difficulty_box.setMaximumWidth(120)
        self.difficulty_box.addItems(MODES.keys())
        self.difficulty_box.setCurrentIndex(list(MODES.keys()).index(mode))
        self.difficulty_box.currentTextChanged.connect(self.difficulty_setter)

        # Sets the layout of all the widgets 
        button_layout = QGridLayout()
        button_layout.setSpacing(0)
        button_layout.addWidget(self.difficulty_box, 0, 4, Qt.AlignmentFlag.AlignRight)
        button_layout.addWidget(self.watch, 0, 5, Qt.AlignmentFlag.AlignCenter)
        button_layout.addWidget(flag_widget, 0, 6, Qt.AlignmentFlag.AlignLeft)
        full_layout = QVBoxLayout()
        full_layout.addLayout(button_layout)
        full_layout.addWidget(self.view)

        # Pack the full layout into a widget to display
        interface = QWidget()
        interface.setLayout(full_layout)
        self.setCentralWidget(interface)
    
    def flag_count_update(self):
        """Updates the text for the number of flagged cells"""
        self.flag_count.setText(str(Tile.num_flagged_cells) + "/" + str(self.total_bombs))
        self.flag_count.update()
    
    def _customize_win_dialog(self):
        """Returns a WinDialog object with the user's time for the current game as well as their 
        best time for that game mode. 
        
        Returns:
            A WinDialog object containing their current and best times
        """
        cur_time = self.watch.get_time()
        best_time = HIGH_SCORES[self.mode]
        # If their cur_time is greater than their best_time, their best_time is still best_time
        if cur_time >= best_time:
            return WinDialog(cur_time, best_time, TIME_FILE_PATH, TROPHY_FILE_PATH)
        return WinDialog(cur_time, cur_time, TIME_FILE_PATH, TROPHY_FILE_PATH)
    
    def _save_best_time(self):
        """Updates the HIGH_SCORES dictionary and saves the dictionary to SCORES_FILE_PATH"""
        cur_time = self.watch.get_time()
        HIGH_SCORES[self.mode] = min(cur_time, HIGH_SCORES[self.mode])
        write_high_scores(HIGH_SCORES, SCORES_FILE_PATH)
        
    def mousePressEvent(self, event):
        """Handler for mouse press events. Mouse events are handled here in order to reset the timer
        and update the number of flagged tiles. 

        Args:
            event -- A QGraphicsSceneMouseEvent to handle
        """
        # Every time the user clicks something, update the flag count
        self.flag_count_update()
        # Start the timer if the first move has been made, and the timer
        # has not already been started
        if not self.timer_active and Tile.first_move_made:
            self.watch.start()
            self.timer_active = True
        # Display dialog if the game is over and dialog has not been displayed yet
        if self.scene.game_finished() and not self.dialog_displayed:
            # Stop watch and disable the difficulty chooser once game ends
            self.watch.stop()
            self.difficulty_box.setEnabled(False)
    
            if self.scene.game_is_won():
                # If the game is won, save the times
                self.dialog = self._customize_win_dialog()
                self._save_best_time()
            else:
                self.dialog = LoseDialog(HIGH_SCORES[self.mode], TIME_FILE_PATH, TROPHY_FILE_PATH)
            # If the user wants to try again, reset the game and allow them to try again.
            # Otherwise, allow them to view the endgame_sequence, and they can choose another
            # difficulty from the difficulty chooser. 
            self.dialog_displayed = True
            self.dialog.show()
            self.dialog.accepted.connect(self.reset_game)
            self.dialog.rejected.connect(self.allow_endgame_sequence)
    
    def difficulty_setter(self, new_mode):
        """Switches the difficulty of the game by setting it to NEW_MODE and starts
        a new blank game in that new mode.
        
        Args:
            new_mode -- the new difficulty that the user selects
        """
        self.timer_active = False 
        self.dialog_displayed = False
        self.watch.reset()
        width, height, tile_size, self.total_bombs = MODES[new_mode]
        # Re-initializing the canvas automatically resets the Tile.first_move_made
        # and the Tile.num_flagged_cells attributes 
        self.scene = Canvas(width, height, tile_size, self.total_bombs)
        self.mode = new_mode
        # Re-enable the difficulty box
        self.difficulty_box.setEnabled(True)
        # Resets the flag count display to 0
        self.flag_count_update()
        self.view.setScene(self.scene)
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def reset_game(self):
        """Resets the current game in the same difficulty setting"""
        self.difficulty_setter(self.mode)
    
    def allow_endgame_sequence(self):
        """Re-enables the difficulty-chooser after the dialog box is closed out"""
        self.difficulty_box.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow('Medium')
    window.show()
    app.exec()
