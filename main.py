import sys
from canvas import *
from tiles import *
from utils import *
from dialog import *
from stopwatch import *
from PyQt6.QtGui import QFont

MODES = {
    'Hard' : (24, 20, 32, 99),
    'Medium' : (18, 14, 46, 40),
    'Easy' : (10, 8, 50, 10), 
}
ICON_SIZE = 30
TEXT_SIZE = 15
SCORES_FILE_PATH = "cache/high_scores.txt"
FLAG_FILE_PATH = "images/flag.png"
TIME_FILE_PATH = "images/hourglass.png"
TROPHY_FILE_PATH = "images/trophy.png"
HIGH_SCORES = read_high_scores(SCORES_FILE_PATH)

class MainWindow(QMainWindow):
    def __init__(self, mode):
        """Create a MainWindow object for user interaction"""
        super(MainWindow, self).__init__()
        self.mode = mode
        self.dialog_displayed = False
        self.width, self.height, self.tile_size, self.total_bombs = MODES[mode]
        self.setWindowTitle("Minesweeper")
        self.scene = Canvas(self.width, self.height, self.tile_size, self.total_bombs)
        self.view = QGraphicsView(self.scene)
        self.scores = read_high_scores(SCORES_FILE_PATH)

        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Vectorizes graphics
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.watch = StopWatch(999, TIME_FILE_PATH, ICON_SIZE, TEXT_SIZE)
        self.timer_active = False 

        flag_icon = QLabel()
        flag_icon.setPixmap(QPixmap(FLAG_FILE_PATH).scaled(ICON_SIZE, ICON_SIZE))

        self.flag_count = QLabel()
        self.flag_count.setText("0/" + str(self.total_bombs))
        font = QFont()
        font.setPointSize(TEXT_SIZE)
        self.flag_count.setFont(font)

        flag_layout = QHBoxLayout()
        flag_layout.addWidget(flag_icon)
        flag_layout.addWidget(self.flag_count)
        flag_layout.setSpacing(8)

        flag_widget = QWidget()
        flag_widget.setLayout(flag_layout)

        self.difficulty_box = QComboBox()
        font.setPointSize(TEXT_SIZE - 2)
        self.difficulty_box.setFont(font)
        self.difficulty_box.setMaximumWidth(120)
        self.difficulty_box.addItems(MODES.keys())
        self.difficulty_box.setCurrentIndex(list(MODES.keys()).index(mode))
        self.difficulty_box.currentTextChanged.connect(self.difficulty_setter)

        button_layout = QGridLayout()
        button_layout.setSpacing(0)
        button_layout.addWidget(self.difficulty_box, 0, 4, Qt.AlignmentFlag.AlignRight)
        button_layout.addWidget(self.watch, 0, 5, Qt.AlignmentFlag.AlignCenter)
        button_layout.addWidget(flag_widget, 0, 6, Qt.AlignmentFlag.AlignLeft)

        full_layout = QVBoxLayout()
        full_layout.addLayout(button_layout)
        full_layout.addWidget(self.view)

        interface = QWidget()
        interface.setLayout(full_layout)
        self.setCentralWidget(interface)
    
    def flag_count_update(self):
        self.flag_count.setText(str(Tile.num_flagged_cells) + "/" + str(self.total_bombs))
        self.flag_count.update()
    
    def _customize_win_dialog(self):
        cur_time = self.watch.get_time()
        best_time = HIGH_SCORES[self.mode]
        if cur_time >= best_time:
            return WinDialog(cur_time, best_time, TIME_FILE_PATH, TROPHY_FILE_PATH)
        return WinDialog(cur_time, cur_time, TIME_FILE_PATH, TROPHY_FILE_PATH)
    
    def _save_best_time(self):
        cur_time = self.watch.get_time()
        HIGH_SCORES[self.mode] = min(cur_time, HIGH_SCORES[self.mode])
        write_high_scores(HIGH_SCORES, SCORES_FILE_PATH)
        
    def mousePressEvent(self, event):
        self.flag_count_update()
        if not self.timer_active and Tile.first_move_made:
            self.watch.start()
            self.timer_active = True
        if self.scene.game_finished() and not self.dialog_displayed:
            self.watch.stop()
            self.difficulty_box.setEnabled(False)
            if self.scene.game_is_won():
                self.dialog = self._customize_win_dialog()
                self._save_best_time()
            else:
                self.dialog = LoseDialog(HIGH_SCORES[self.mode], TIME_FILE_PATH, TROPHY_FILE_PATH)
            self.dialog_displayed = True
            self.dialog.show()
            self.dialog.accepted.connect(self.reset_game)
        super().mousePressEvent(event)
    
    def reset_game(self):
        self.difficulty_box.setEnabled(True)
        self.difficulty_setter(self.mode)
    
    def difficulty_setter(self, new_mode):
        # reset number of flagged cells, since new instance of Canvas
        Tile.num_flagged_cells = 0
        Tile.first_move_made = False

        self.timer_active = False 
        self.dialog_displayed = False
        self.watch.reset()

        self.width, self.height, self.tile_size, self.total_bombs = MODES[new_mode]
        self.mode = new_mode
        self.flag_count_update()
        self.scene = Canvas(self.width, self.height, self.tile_size, self.total_bombs)
        self.view.setScene(self.scene)
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow('Medium')
    window.show()
    app.exec()