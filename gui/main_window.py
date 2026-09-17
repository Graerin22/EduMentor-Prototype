from PyQt6.QtWidgets import QMainWindow, QTabWidget
from gui.chat_widget import ChatWidget
from gui.session_widget import SessionWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduMentor - AI Teaching Assistant")
        self.setGeometry(300, 60, 1000, 700)

        self.chat_widget = ChatWidget()
        self.session_widget = SessionWidget()

        self.session_widget.session_load_requested.connect(self.on_session_load_requested)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.chat_widget, '📖 Mentor')
        self.tabs.addTab(self.session_widget, '📚 Sessions')
        
        self.setCentralWidget(self.tabs)

    def on_session_load_requested(self, filepath):
        self.chat_widget.load_session(filepath)
        self.tabs.setCurrentIndex(0)
        self.session_widget.refresh_list()

    def closeEvent(self, event):
        self.chat_widget.save_session(silent=True)
        event.accept()