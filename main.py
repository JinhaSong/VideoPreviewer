from utils.ffmpegChecker import *
from app import MainWindow


if __name__ == '__main__':
    # Check ffmpeg
    checkFFmpeg()

    # Show MainWindow
    MainWindow.startApp()