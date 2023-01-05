from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QLabel, QWidget, QHBoxLayout
from PyQt6.QtGui import QFont, QPixmap

class Watch(QLabel):
    """A Watch object that provides the text for the StopWatch object. 
    The text displayed is updated every second to display the current time.

    Attributes:
        current_time -- the current time to display
        timeout -- the time up to which the stopwatch goes
        timer -- a QTimer object used to update self.current_time each second
        format -- the format to use when displaying the time
    """
    def __init__(self, timeout, text_size, parent = None):
        """Create a Watch that stops at TIMEOUT and displays the time using font size equal to 
        TEXT_SIZE. Text is formatted to use up as many digits as TIMEOUT. For example, if
        TIMEOUT is 567, the object will display three digits (i.e. if the current time is 7 seconds, 
        '007' will be displayed)

        timeout -- An integer; the value at which the Watch will stop
        text_size -- An integer; the size at which to display the text
        """
        super().__init__(parent)
        self.current_time = 0
        self.timeout = timeout
        # If self.timeout has N digits, the code below sets the format to {:0Nd}
        self.format = '{:0' + str(len(str(self.timeout))) + 'd}' 
        
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._update_time)

        font = QFont()
        font.setPointSize(text_size)
        self.setFont(font)
        self.setText(self.format.format(self.current_time))
    
    def _start_time(self):
        """Starts time by starting the QTimer"""
        self.timer.start()
    
    def _stop_time(self):
        """Stops time by freezing the display"""
        self.timer.stop()
    
    def _reset_time(self):
        """Resets the watch, updates the displayed text and stops time."""
        # Necessary to set self.current_time to -1, since 1 is added to 
        # self.current_time before updating display in self._update_time()
        self.current_time = -1
        self._update_time()
        self.timer.stop()
    
    def _get_time(self):
        """Returns the current time displayed."""
        return self.current_time
    
    def _update_time(self):
        """Adds 1 second to the current time and updates the display"""
        # Stop the watch once it reaches the timeout
        if self.current_time == self.timeout:
            self.timer.stop() 
            return

        self.current_time += 1
        self.setText(self.format.format(self.current_time))
        self.update() 

class StopWatch(QWidget):
    """A StopWatch object that displays the text provided in the Watch object 
    next to a graphical icon.

    Attributes:
        watch -- A watch object to display
    """
    def __init__(self, timeout, icon, icon_size = 30, text_size = 15):
        """Create a StopWatch that stops at TIMEOUT and displays the time using font size equal to 
        TEXT_SIZE next to the provided ICON after rescaling to ICON_SIZE

        timeout -- An integer; the value at which the watch will stop
        text_size -- An integer; the size at which to display the text
        icon -- A string; the filepath to the icon represented as a string
        icon_size -- An integer; the size at which to display ICON
        """
        super().__init__()
        self.watch = Watch(timeout, text_size)

        icon_widget = QLabel()
        icon_widget.setPixmap(QPixmap(icon).scaled(icon_size, icon_size))

        layout = QHBoxLayout()
        layout.addWidget(icon_widget)
        layout.addWidget(self.watch)
        layout.setSpacing(0)
        self.setLayout(layout)
    
    def start(self):
        """Starts time"""
        self.watch._start_time()
    
    def stop(self):
        """Stops time"""
        self.watch._stop_time()
    
    def reset(self):
        """Resets time"""
        self.watch._reset_time()
    
    def get_time(self):
        """Return current time"""
        return self.watch._get_time()
