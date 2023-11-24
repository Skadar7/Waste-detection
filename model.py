import cv2
from ultralytics import YOLO
import torch
from utils import *

class CDWnet:
    def __init__(self, hard_model, light_model = None):
        self.light_model_path = light_model
        self.hard_model_path = hard_model
        self.cuda_flag = False
        self.detect_model_classes = None

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

    def get_class(self, result):
        for res in result:
            boxes = res.boxes.cpu().numpy()
            classes = []

            for box in boxes:
                class_name = self.detect_model_classes[int(box.cls)]
                classes.append(class_name)
        return classes

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
            detection_results[frame_id] = self.get_class(result)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id+frame_skip)
        cap.release()
        return detection_results

    def predict(self, video_path, mode = 'hard_mode'):
        if mode == 'hard_mode':
            result = self.process_hard(video_path)
            return post_process(result)