import os
from distutils.log import Log, ERROR, INFO

import requests
from zipfile import ZipFile

def checkFFmpeg() :
    print("Info: Start to set ffmpeg")
    # Check if the ffmpeg directory exists.
    if not isFFmpegDir():
        print("Info: Is not ffmpeg... It will be start to check ffmpeg.zip!")
    else :
        return False

    # Check if the ffmpeg zip file exists.
    if not isFFmpegZip():
        print("Info: ffmpeg.zip is not exist... It will be start to download ffmpeg.zip!")
        downloadFFmpeg()
    else :
        print("Info: ffmpeg.zip is exist... It will be start to unzip ffmpeg.zip!")

    # Unzip ffmpeg zip file
    if not unzipFFmpeg():
        print("Info: Fail to unzip ffmpeg.zip... VideoPreviewer will be terminated")

    print("Info: Successfully completed the ffmpeg settings")
    return True

def isFFmpegDir() :
    return os.path.isdir(os.path.join(os.getcwd(), "ffmpeg"))

def isFFmpegZip() :
    return os.path.isfile(os.path.join(os.getcwd(), "ffmpeg.zip"))


def downloadFFmpeg() :
    try :
        url = "https://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-4.2.2-win64-static.zip"
        response = requests.get(url)
        with open("ffmpeg.zip", 'wb') as ffmpeg_zip:
            ffmpeg_zip.write(response.content)
        print("Info: Success to download ffmpeg.zip")
    except :
        print("Info: Fail to download ffmpeg.zip")

def unzipFFmpeg():
    try :
        with ZipFile(os.path.join(os.getcwd(), "ffmpeg.zip"), 'r') as zipObject:
            zipObject.extractall(os.path.join(os.getcwd(), "ffmpeg"))
        print("Info: Success to unzip ffmpeg.zip")
        return True
    except :
        print("Info: Fail to unzip ffmpeg.zip")
        return False
