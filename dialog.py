from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QApplication, QPushButton

"""Global Variables:

WORST_TIME: In "main.py", the worst time achievable by the player is 999.
However, before the player has set a high score, their time is saved in 
cache/high_scores.txt as WORST_TIME for each difficulty mode. When displaying
the dialog, if the user's best time is WORST_TIME, then instead of displaying 
the time, three dashes are displayed instead (this is equivalent to saying
that their best score is N/A).  

RETRY_STRING: A unicode string encoding the "refresh" symbol
"""

WORST_TIME = 1000
RETRY_STRING = u"\u21BA"

class WinDialog(QDialog):
    """A WinDialog object displays the user's time taken for the current game
    as well as their best time in that category next to a timer icon and a trophy
    icon, respectively.
    """
    def __init__(self, cur_time, best_time, time_icon, trophy_icon, \
        icon_size = 30, text_size = 15, num_digits = 3):
        """Create a LoseDialog with times CUR_TIME and BEST_TIME, displayed next to TIME_ICON, and 
        TROPHY_ICON, respectively, which are scaled to ICON_SIZE. The user's times are formatted
        according to TEXT_SIZE and NUM_DIGITS

        cur_time -- An integer; the amount of time the user took for the current game
        best_time -- An integer; the user's best time for the current game mode
        time_icon -- A string; the filepath to the icon to use for displaying the user's
                    current time
        trophy_icon -- A string; the filepath to the icon to use for displaying the user's
                    best time
        icon_size -- An integer; the size of the icon
        text_size -- An integer; the size of the text
        num_digits -- An integer; the number of digits to display for cur_time and best_time
        """
        super().__init__()
        self.setWindowTitle("Minesweeper")
        format_string = "{:0" + str(num_digits) + "d}"

        hourglass = QLabel()
        trophy = QLabel()
        current_time_label = QLabel()
        best_time_label = QLabel()

        # Icon for the user's current time and best time, respectively 
        hourglass.setPixmap(QPixmap(time_icon).scaled(icon_size, icon_size))
        trophy.setPixmap(QPixmap(trophy_icon).scaled(icon_size, icon_size))

        if isinstance(cur_time, int):
            current_time_label.setText(format_string.format(cur_time))
        else:
            current_time_label.setText(cur_time)

        # If the user's best_time is WORST_TIME, they haven't played that gamemode
        # yet, so don't display best_time.
        if best_time == WORST_TIME:
            best_time_label.setText('___')
        else:
            best_time_label.setText(format_string.format(best_time))

        # Set each of the labels to have the same font
        font = QFont()
        font.setPointSize(text_size)
        for label in [current_time_label, best_time_label]:
            label.setFont(font)

        # Code below is for setting up the layout of the icons and text
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

        # Add a button to allow the user to play the game again
        repeat = self._repeat_button()
        repeat.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addLayout(side_layout)
        layout.addWidget(repeat)

        self.setAutoFillBackground(True)
        self.setLayout(layout)
    
    def _repeat_button(self):
        """A repeat button that displays the text "Play Again" next to the refresh 
        symbol, inviting the user to play the game again.

        Returns:
            A QPushButton object that allows the user to play the game again
        """
        button = QPushButton()
        button.setText(RETRY_STRING + " Play again")
        return button 
    
class LoseDialog(WinDialog):
    """A LoseDialog object displays the user's best time in their current gamemode next
    to the trophy icon. Does not display the user's current time taken for the game, as
    it is assumed the user has lost the game, and therefore does not have a time to
    compare with. 
    """
    def __init__(self, best_time, time_icon, trophy_icon, \
        icon_size = 30, text_size = 15, num_digits = 3):
        """Create a LoseDialog with time BEST_TIME, displayed next to TIME_ICON, and 
        TROPHY_ICON which are scaled to ICON_SIZE. The user's best time is formatted
        according to TEXT_SIZE and NUM_DIGITS

        best_time -- An integer; the user's best time for the current game mode
        time_icon -- A string; the filepath to the icon to use for displaying the user's
                    current time
        trophy_icon -- A string; the filepath to the icon to use for displaying the user's
                    best time
        icon_size -- An integer; the size of the icon
        text_size -- An integer; the size of the text
        num_digits -- An integer; the number of digits to display for cur_time and best_time
        """
        super().__init__("___", best_time, time_icon, trophy_icon, \
            icon_size, text_size, num_digits)
            
    def _repeat_button(self):
        """A repeat button that displays the text "Try Again" next to the refresh 
        symbol, inviting the user to retry the game. Overrides the self._repeat_button()
        of WinDialog.

        Returns:
            A QPushButton object that allows the user to retry.
        """
        button = QPushButton()
        button.setText(RETRY_STRING + " Try again")
        return button
