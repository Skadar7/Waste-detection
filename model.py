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
        self.detection_mode = None
        self.model_conf = 0.5

        if torch.cuda.is_available():
            self.cuda_flag = True 
        self.prepare_model()

    def prepare_model(self):
        if self.light_model_path is not None:
            self.light_model = YOLO(self.light_model_path)
            self.detect_model_classes = self.light_model.names
            if self.cuda_flag:
                self.light_model.to('cuda') 

        if self.hard_model_path is not None:
            self.hard_model = YOLO(self.hard_model_path)
            self.detect_model_classes = self.hard_model.names
            if self.cuda_flag:
                self.hard_model.to('cuda') 

    def handle_result(self, result, frame):
        for res in result:
            boxes = res.boxes.cpu().numpy()
            images_data = []

            for box in boxes:
                class_name = self.detect_model_classes[int(box.cls)]
                xyxy = box.xyxy[0]
                confidence = str(round(box.conf[0].item(), 2))
                label = f'{class_name}: {confidence}'

                images_data.append([class_name, confidence, xyxy, label, frame])

        if images_data:
            most_conf_class = max(images_data, key = lambda x: x[1])
            return most_conf_class
        return None

    def post_process(self, detection_results):
        if self.detection_mode == 'hard_mode':
            vals = list(detection_results.values())
            cls_list = [i[0] for i in vals]

            final_class = max(cls_list, key=cls_list.count)
            cnf_list = [i for i in vals if i[0] == final_class]

            max_conf = max(cnf_list, key = lambda x: x[1])
            frame_num = list(detection_results.keys())[vals.index(max_conf)]

            frame = plot_boxes(max_conf[4], max_conf[2], max_conf[3])
        else:
            final_class = detection_results[0]
            frame = plot_boxes(detection_results[4], detection_results[2], detection_results[3])

        success, buffer = cv2.imencode('.jpg', frame)
        base64_img = base64.b64encode(buffer)

        return final_class, base64_img

    def process_hard(self, video_path):
        cap = cv2.VideoCapture(video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_number = 120 * fps # 2:00 - 2:15
        last_frame_number = 135 * fps
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
            result = self.hard_model(frame, verbose=False, conf = self.model_conf)
            handled_res = self.handle_result(result, frame)
            if handled_res:
                detection_results[frame_id] = handled_res
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id+frame_skip)

        cap.release()
        return detection_results

    def process_light(self, image_path):
        result = self.light_model(image_path, verbose=False, conf = self.model_conf)
        frame = cv2.imread(image_path)
        detection_results = self.handle_result(result, frame)
        return detection_results

    def process_light_stream(self, stream_path):
        cap = cv2.VideoCapture(stream_path)
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            result = self.light_model(frame, verbose=False, conf = self.model_conf)
            detection_results = self.handle_result(result, frame)
            
            if detection_results:
                yield self.post_process(detection_results)
            else:
                yield None, None

    def predict(self, path, mode = 'hard_mode'):
        self.detection_mode = mode

        if self.detection_mode == 'hard_mode':
            result = self.process_hard(path)
        elif self.detection_mode == 'light_mode':
            result = self.process_light(path)
        if result:
            return self.post_process(result)
        else:
            return None, None
