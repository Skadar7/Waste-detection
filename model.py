import cv2
from ultralytics import YOLO
import torch
from utils import *
import base64

class CDWnet:
    def __init__(self, hard_model, light_model = None):
        self.light_model_path = light_model
        self.hard_model_path = hard_model
        self.cuda_flag = False
        self.detect_model_classes = None
        self.video_path = None

        if torch.cuda.is_available():
            self.cuda_flag = True 
        self.prepare_model()

    def prepare_model(self):
        if self.light_model_path is not None:
            self.light_model = YOLO(self.light_model_path)
            self.detect_model_classes = self.light_model.names
            self.light_model.to('cuda') 

        if self.hard_model_path is not None:
            self.hard_model = YOLO(self.hard_model_path)
            self.detect_model_classes = self.hard_model.names
            self.hard_model.to('cuda') 

    def handle_result(self, result):
        for res in result:
            boxes = res.boxes.cpu().numpy()
            images_data = []

            for box in boxes:
                class_name = self.detect_model_classes[int(box.cls)]
                xyxy = box.xyxy[0]
                confidence = str(round(box.conf[0].item(), 2))
                label = f'{class_name}: {confidence}'

                images_data.append([class_name, confidence, xyxy, label])
        
        most_conf_class = max(images_data, key = lambda x: x[1])
        return most_conf_class

    def post_process(self, detection_results):
        vals = list(detection_results.values())
        cls_list = [i[0] for i in vals]

        final_class = max(cls_list, key=cls_list.count)
        cnf_list = [i for i in vals if i[0] == final_class]

        max_conf = max(cnf_list, key = lambda x: x[1])
        frame_num = list(detection_results.keys())[vals.index(max_conf)]


        cap = cv2.VideoCapture(self.video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num-1) # -1?
        success, frame = cap.read()

        frame = plot_boxes(frame, max_conf[2], max_conf[3])

        success, buffer = cv2.imencode('.jpg', frame)
        base64_img = base64.b64encode(buffer)

        return final_class, base64_img

    def process_hard(self, video_path):
        cap = cv2.VideoCapture(video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_number = 120 * fps # 2:05 - 2:15
        last_frame_number = 135 * fps
        conf = 0.5
        frame_skip = 11

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number-1)
        detection_results = dict()

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            frame_id = cap.get(cv2.CAP_PROP_POS_FRAMES)

            if frame_id == last_frame_number:
                break
            result = self.hard_model(frame, verbose=False, conf = conf)
            detection_results[frame_id] = self.handle_result(result)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id+frame_skip)

        cap.release()
        return detection_results # dict { frame_number : [class_mark1, class_mark2, ...]}

    def predict(self, video_path, mode = 'hard_mode'):
        self.video_path = video_path
        if mode == 'hard_mode':
            result = self.process_hard(video_path)
            return self.post_process(result)