import os
import sys
import time

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QUrl, pyqtSlot, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QMainWindow, QAction, QApplication, QFileDialog, QLabel, QWidget, QFrame, \
    QGridLayout, QSizePolicy, QSlider, QStyle, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem, \
    QAbstractItemView, QListWidget, QListWidgetItem

from utils.darknetDetectorWrapper import darknetDetectorWrapper
from utils.ffmpegWrapper import FFmpegWrapper


class MainWindow(QMainWindow):
    directory_path = ""
    video_paths = []
    video_infos = []
    main_width = 1500
    main_height = 800
    key_frame_dir = ""

    def __init__(self):
        super().__init__()
        self.tabs = []
        self.tab_names = []

        self.__initUI()

    def __initUI(self):
        # Create a widget for window contents
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create new action
        open_action = QAction(QIcon('open.png'), '&Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open movie')
        open_action.triggered.connect(self.__openDownloadDirectory)

        # Create exit action
        exit_action = QAction(QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)

        # Create menu bar and add action
        menu_bar = self.menuBar()
        menu = menu_bar.addMenu('&메뉴')
        menu.addAction(open_action)
        menu.addAction(exit_action)

        self.statusBar()
        self.setFrameViewWidget()
        self.setVideoWidget()
        self.setVideoControlWidget()
        self.setTabWidget()
        self.setMainLayout()
        # Set widget to contain window contents
        self.central_widget.setLayout(self.main_layout)
        self.setGeometry(300, 300, self.main_width, self.main_height)
        self.setWindowTitle('Video Previewer')
        self.show()

    def setFrameViewWidget(self):
        self.frame = QLabel(self)
        self.frame.setFrameShape(QFrame.Panel)
        self.frame.setFixedHeight(self.main_height / 2)
        self.frame.setFixedWidth(self.main_width / 3)
        self.frame.setStyleSheet("background: white; border:1px solid gray;")
        self.frame.setAlignment(Qt.AlignCenter)

    def setVideoWidget(self):
        self.videoWidget = QVideoWidget()
        self.videoWidget.setStyleSheet("background: white; border:1px solid rgb(0, 0, 0);")
        self.videoWidget.setFixedWidth(self.main_width / 3)
        self.videoWidget.setFixedHeight(self.main_height / 2)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def setVideoControlWidget(self):
        self.play_button = QPushButton()
        self.play_button.setEnabled(False)
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.play)
        self.play_button.setFixedWidth(50)

        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.setPosition)
        self.position_slider.setFixedWidth(self.main_width / 3 - 55)

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        self.controlLayout = QGridLayout()
        self.controlLayout.setAlignment(Qt.AlignLeft)
        self.controlLayout.setAlignment(Qt.AlignTop)
        self.controlLayout.addWidget(self.videoWidget, 0, 0, 1, 2)
        self.controlLayout.addWidget(self.play_button, 1, 0)
        self.controlLayout.addWidget(self.position_slider, 1, 1)

    def setMainLayout(self):
        self.main_layout = QGridLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.addLayout(self.controlLayout, 1, 0)
        self.main_layout.addWidget(self.frame, 2, 0)
        self.main_layout.addWidget(self.tabWidget, 0, 1, 3, 3)
        # self.main_layout.addWidget(self.errorLabel)

    def setVideoTab(self, row_count):
        column_headers = ['Thumbnail', 'Name', 'Size', 'Created Date', 'Modified Date']
        self.tab_videos = QTableWidget()
        self.tab_videos.resize(290, 290)
        self.tab_videos.setRowCount(row_count)
        self.tab_videos.setColumnCount(5)
        self.tab_videos.setHorizontalHeaderLabels(column_headers)
        self.tabWidget.addTab(self.tab_videos, "Videos")

    def setVideoTabItems(self, videos):
        for video in videos:
            video_info = os.path.join(self.directory_path, video)
            self.video_paths.append(video_info)
            self.video_infos.append([
                "",
                video,
                "%.2f MB" % (os.path.getsize(video_info) / (1024.0 * 1024.0)),
                time.ctime(os.path.getctime(video_info)),
                time.ctime(os.path.getmtime(video_info))
            ])

        for row, video_infos in enumerate(self.video_infos):
            for col, video_info in enumerate(video_infos):
                self.tab_videos.setItem(row, col, QTableWidgetItem(str(video_infos[col])))

        self.tab_videos.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tab_videos.cellClicked.connect(self.videoCellClicked)
        self.tab_videos.cellDoubleClicked.connect(self.videoCellDoubleClicked)

        header = self.tab_videos.horizontalHeader()
        for idx in range(len(videos)):
            header.setSectionResizeMode(idx, QtWidgets.QHeaderView.ResizeToContents)

    @pyqtSlot(int, int)
    def videoCellClicked(self, row, col):
        self.tab_videos.selectRow(row)
        cell = self.tab_videos.item(row, 1)

    @pyqtSlot(int, int)
    def videoCellDoubleClicked(self, row, col):
        self.openFile(self.video_paths[row])
        self.tab_videos.selectRow(row)

    def setFrameTab(self):
        self.tab_keyframes = QListWidget()
        self.tab_keyframes.setViewMode(QListWidget.IconMode)
        self.tab_keyframes.setIconSize(QSize(225, 225))
        self.tab_keyframes.itemDoubleClicked.connect(self.frameCellDoubleClicked)
        self.tabWidget.addTab(self.tab_keyframes, "Key frames")

    def frameCellDoubleClicked(self, item=None):
        self.frame.setStyleSheet("background: black")
        pixmap = QPixmap(os.path.join(self.key_frame_dir, item.text()))
        self.frame.setPixmap(pixmap)

    def setTabWidget(self):
        self.tabWidget = QTabWidget()



    def __openDownloadDirectory(self):
        directory_path = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if directory_path:
            self.directory_path = directory_path
            videos = os.listdir(self.directory_path)
            self.setVideoTab(len(videos))
            self.setFrameTab()
            self.setVideoTabItems(videos)

        else :
            print("Info: You didn't select directory. current directory path is \"{}\"".format(self.directory_path))

    def openFile(self, fileName):
        if fileName != '':
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(fileName)))
            self.play_button.setEnabled(True)

            ffmpeg = FFmpegWrapper()
            ffmpeg.setOptions(video_path=fileName)
            if not os.path.isdir(ffmpeg.getOutputDir()):
                ffmpeg.runFFmpeg()

            keyframelist_file = ffmpeg.getKeyframesPathFile()

            detector = darknetDetectorWrapper()
            detector.setInputPath(input_paths=keyframelist_file)
            detector.setOutputPath(ffmpeg.getOutputDir())
            detector.runDarknetDetector()

            frame_names = self.readFrames(keyframelist_file)

            self.tab_keyframes.clear()
            self.key_frame_dir = frame_names[0].replace(frame_names[0].split("\\")[-1],"")
            for frame_name in frame_names:
                item = QListWidgetItem(QIcon(frame_name), frame_name.split("\\")[-1])
                self.tab_keyframes.addItem(item)

    def readFrames(self, keyframelist_file):
        frame_names = []
        with open(keyframelist_file, 'r') as file:
            for frame in file:
                frame_names.append(frame.split("\n")[0])

        return frame_names

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.position_slider.setValue(position)

    def durationChanged(self, duration):
        self.position_slider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.play_button.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())

def startApp():
    app = QApplication(sys.argv)
    main_window = MainWindow()

    sys.exit(app.exec_())