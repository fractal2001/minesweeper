import sys
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QApplication, QPushButton

WORST_TIME = 1000

class WinDialog(QDialog):
    def __init__(self, cur_time, best_time, time_icon, trophy_icon, icon_size = 30, text_size = 15, num_digits = 3):
        super().__init__()

        self.setWindowTitle("Minesweeper")

        format_string = '{:0' + str(num_digits) + 'd}'

        hourglass = QLabel()
        hourglass.setPixmap(QPixmap(time_icon).scaled(icon_size, icon_size))
        current_time_label = QLabel()
        if isinstance(cur_time, int):
            current_time_label.setText(format_string.format(cur_time))
        else:
            current_time_label.setText(cur_time)

        trophy = QLabel()
        trophy.setPixmap(QPixmap(trophy_icon).scaled(icon_size, icon_size))
        best_time_label = QLabel()
        
        if best_time == WORST_TIME:
            best_time_label.setText('___')
        else:
            best_time_label.setText(format_string.format(best_time))

        font = QFont()
        font.setPointSize(text_size)

        for label in [hourglass, current_time_label, trophy, best_time_label]:
            label.setFont(font)

        current_score_layout = QVBoxLayout()
        current_score_layout.setSpacing(0)
        current_score_layout.addWidget(hourglass)
        current_score_layout.addWidget(current_time_label)

        current_score_widget = QWidget()
        current_score_widget.setLayout(current_score_layout)

        best_time_layout = QVBoxLayout()
        best_time_layout.setSpacing(0)
        best_time_layout.addWidget(trophy)
        best_time_layout.addWidget(best_time_label)

        best_time_widget = QWidget()
        best_time_widget.setLayout(best_time_layout)

        side_layout = QHBoxLayout()
        side_layout.addWidget(current_score_widget)
        side_layout.addWidget(best_time_widget)

        self.repeat = self.repeat_button()
        self.repeat.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addLayout(side_layout)
        layout.addWidget(self.repeat)

        # self.setStyleSheet("background-color: gray;")
        self.setAutoFillBackground(True)
        self.setLayout(layout)
    
    def repeat_button(self):
        button = QPushButton()
        button.setText(u"\u21BA" + " Play again")
        return button 
    
class LoseDialog(WinDialog):
    def __init__(self, best_time, time_icon, trophy_icon, icon_size = 30, text_size = 15, num_digits = 3):
        super().__init__("___", best_time, time_icon, trophy_icon, icon_size, text_size, num_digits)
    
    def setWindowTitle(self, window_title):
        super().setWindowTitle(window_title)
        
    # override 
    def repeat_button(self):
        button = QPushButton()
        button.setText(u"\u21BA" + " Try again")
        return button

