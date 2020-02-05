import sys
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication, QPushButton, QTableView, QToolBar
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        table = QTableView()
        self.setCentralWidget(table)

        exit_action = QAction(QIcon('system-shutdown.png'), 'Exit', self)
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)

        self.statusBar()

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(exit_action)

        toolbar_main = self.addToolBar('Exit')
        toolbar_main.addAction(exit_action)

        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('Video Previewer')
        self.show()

def startApp():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())