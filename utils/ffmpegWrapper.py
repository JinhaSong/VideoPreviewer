import os

class FFmpegWrapper:
    video_path = None
    video_name = None
    output_dir = None
    file_keyframes = None

    def __init__(self):
        self.video_path = os.path.join(os.getcwd(), "test", "test.mp4")
        self.output_dir_root = os.path.join(os.getcwd(), "frames")

    def getOutputDir(self):
        return self.output_dir

    def getKeyframesPathFile(self):
        return self.file_keyframes

    def setOptions(self, video_path=video_path):
        self.video_path = video_path
        self.video_name = video_path.split("\\")[-1]
        self.output_dir = os.path.join(self.output_dir_root, self.video_name)
        self.file_keyframes = os.path.join(self.output_dir, "frames.txt")


    def runFFmpeg(self):
        print(self.output_dir)
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)
        os.system("D:\\Packages\\ffmpeg-4.2.2-win64-static\\bin\\ffmpeg -skip_frame nokey -i {} -vsync 0 -frame_pts true {}\\%d.jpg"
                  .format(self.video_path, self.output_dir))
        keyframes = os.listdir(self.output_dir)
        for i in range(len(keyframes)) :
            keyframes[i] = os.path.join(self.output_dir, keyframes[i])
        with open(self.file_keyframes, "w") as file:
            for keyframe in keyframes :
                if keyframe.split("\\")[-1] != "frames.txt":
                    file.write(keyframe + "\n")
            file.close
