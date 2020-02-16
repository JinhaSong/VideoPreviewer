import os
import cv2

class darknetDetectorWrapper:
    mode = None
    dataset = None
    cfg = None
    weight = None
    input_paths = None
    results = None
    output_path = None

    def __init__(self):
        self.mode = "test"
        self.dataset = os.path.join(os.getcwd(), "cfg/nsfw.data")
        self.cfg = os.path.join(os.getcwd(), "cfg/yolov3-nsfw.cfg")
        self.weight = os.path.join(os.getcwd(), "weights/yolov3-nsfw_10000.weights")
        self.input_paths = os.path.join(os.getcwd(), "test.txt")

    def setOptions(self, mode="test ", dataset=dataset, cfg=cfg, weight=weight):
        self.mode = mode
        self.dataset = dataset
        self.cfg = cfg
        self.weight = weight

    def setOutputPath(self, output_path):
        self.output_path = output_path

    def setInputPath(self, input_paths=input_paths):
        self.input_paths = input_paths

    def runDarknetDetector(self):
        if not os.path.isfile(os.path.join(self.output_path, "lock_file")) :
            self.command = "darknet detector {} {} {} {} -dont_show -ext_output < {}"\
                .format(self.mode, self.dataset, self.cfg, self.weight, self.input_paths)
            results_tmp = os.popen(self.command).read().strip().split("\n")[4:]
            start_points = []
            for idx, result in enumerate(results_tmp):
                if "Enter" in result :
                    start_points.append(idx)

            results = []

            for idx in range(len(start_points)-1) :
                file_name = results_tmp[start_points[idx]].replace("Enter Image Path: ", "").split(": Predicted")[0]
                obj_range = start_points[idx+1] - start_points[idx] - 1
                objects = []
                for obj_idx in range(obj_range):
                    obj_info = results_tmp[start_points[idx] + 1 + obj_idx].split("\t")
                    label_prob = obj_info[0]
                    bbox_info = obj_info[1].split("top_y:")
                    x = int(bbox_info[0].replace(" ", "").replace("(left_x:", ""))
                    bbox_info = bbox_info[1].split("width:")
                    y = int(bbox_info[0].replace(" ", "").replace("top_y:", ""))
                    bbox_info = bbox_info[1].split("height:")
                    width = int(bbox_info[0].replace(" ", "").replace("width:", ""))
                    bbox_info = bbox_info[1].split(")")
                    height = int(bbox_info[0].replace(" ", ""))
                    if x < 0: x = 0
                    if y < 0: y = 0
                    objects.append([label_prob, x, y, width, height])
                results.append([file_name, objects])
            self.results = results
            print("Info: Dection complete")
            self.drawBoundingBox()
            print("Info: BBox complete")

    def drawBoundingBox(self):
        for fnum, result in enumerate(self.results):
            if fnum % 50 == 0 :
                print("\r{} / {}".format(fnum, len(self.results)), end="")
            frame = cv2.imread(result[0], cv2.IMREAD_COLOR)

            colors = [(0, 0, 255), (0, 255, 0)]
            for idx, obj_info in enumerate(result[1]):
                label_prop = obj_info[0]
                x = obj_info[1]
                y = obj_info[2]
                width = obj_info[3]
                height = obj_info[4]
                color = ""
                if label_prop.split(": ")[0] == "woman" :
                    color = colors[0]
                else :
                    color = colors[1]
                cv2.rectangle(frame, (x, y), (x + width, y + height), color, 2)
                cv2.putText(frame, label_prop,(x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            cv2.imwrite(result[0], frame)
        print()
        lock_file = open(os.path.join(self.output_path, "lock_file"), "w")
        lock_file.close()

