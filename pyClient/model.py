import cv2
from ultralytics import YOLO, RTDETR
import torch
from utils import *
import numpy as np


class CDWnet:
    """
    Класс-обертка для модели детекции
    """

    def __init__(self, hard_model_path: str = None, light_model_path: str = None):
        """
        __init__ Конструктор

        Args:
            hard_model_path (str, optional): Путь к модели для статического режима работы. Defaults to None.
            light_model_path (str, optional): Путь к модели для динамического режима работы. Defaults to None.
        """
        self.light_model_path = light_model_path
        self.hard_model_path = hard_model_path
        self.light_model = None
        self.hard_model = None

        self.cuda_flag = False
        self.detect_model_classes = None
        self.detection_mode = None
        self.model_conf = 0.5

        if torch.cuda.is_available():
            self.cuda_flag = True
        self.prepare_model()

    def prepare_model(self):
        """
        prepare_model Инициализация моделей детекции
        """
        if self.light_model_path is not None:
            self.light_model = YOLO(self.light_model_path)
            self.detect_model_classes = self.light_model.names
            if self.cuda_flag:
                self.light_model.to("cuda")

        if self.hard_model_path is not None:
            self.hard_model = RTDETR(self.hard_model_path)
            self.detect_model_classes = self.hard_model.names
            if self.cuda_flag:
                self.hard_model.to("cuda")

    def handle_result(self, result: list, frame: np.ndarray) -> list:
        """
        handle_result Обработка результатов предсказания

        Args:
            result (list): список результатов детекции
            frame (np.ndarray): обработанное изображение в формете numpy

        Returns:
            list: результат обработки
        """
        for res in result:
            boxes = res.boxes.cpu().numpy()
            images_data = []

            for box in boxes:
                class_name = self.detect_model_classes[int(box.cls)]
                xyxy = box.xyxy[0]
                confidence = str(round(box.conf[0].item(), 2))
                label = f"{class_name}: {confidence}"

                images_data.append([class_name, confidence, xyxy, label, frame])

        if images_data:
            most_conf_class = max(images_data, key=lambda x: x[1])
            return most_conf_class
        return None

    def post_process(self, detection_results: dict) -> tuple:
        """
        post_process обработка результатов предсказания видео

        Args:
            detection_results (dict): Словарь предсказаний

        Returns:
            tuple: кортеж, в котором храним метку класса видео и демонстрационный кадр, зашифрованный в base64
        """
        # если у нас режим обработки цельного видео, то detection_results хранит результаты для каждого кадра
        # где ключами словаря являются порядковые номера кадров
        if self.detection_mode == "hard_mode":
            vals = list(detection_results.values())
            cls_list = [i[0] for i in vals]

            final_class = max(cls_list, key=cls_list.count)
            cnf_list = [i for i in vals if i[0] == final_class]

            max_conf = max(cnf_list, key=lambda x: x[1])
            frame_num = list(detection_results.keys())[vals.index(max_conf)]

            frame = plot_boxes(max_conf[4], max_conf[2], max_conf[3])
        # иначе detection_results хранит результ только для одного кадра
        else:
            final_class = detection_results[0]
            frame = plot_boxes(
                detection_results[4], detection_results[2], detection_results[3]
            )

        base64_img = convert_to_base64(frame)
        return final_class, base64_img

    def process_hard(self, video_path: str) -> dict:
        """
        process_hard Предсказание по видео

        Args:
            video_path (str): путь к видео для обработки

        Returns:
            dict: результат обработки
        """
        cap = cv2.VideoCapture(video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_number = 120 * fps  # 2:00 - 2:15
        last_frame_number = 135 * fps
        frame_skip = 11

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number - 1)
        detection_results = dict()

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            frame_id = cap.get(cv2.CAP_PROP_POS_FRAMES)

            if frame_id == last_frame_number:
                break
            # предсказание модели
            result = self.hard_model(frame, verbose=False, conf=self.model_conf)
            # обработка предсказания
            handled_res = self.handle_result(result, frame)
            # сохраняем результаты обработки
            if handled_res:
                detection_results[frame_id] = handled_res
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id + frame_skip)

        cap.release()
        return detection_results

    def process_light(self, image_path: str) -> list:
        """
        process_light Предсказание по кадру

        Args:
            image_path (str): путь к кадру

        Returns:
            list: результат предсказания
        """
        result = self.light_model(image_path, verbose=False, conf=self.model_conf)
        frame = cv2.imread(image_path)
        detection_results = self.handle_result(result, frame)
        return detection_results

    def process_light_stream(self, stream_path: str) -> dict:
        """
        process_light_stream Покадровое предсказание для стримов

        Args:
            stream_path (str): адрес стрима (rtsp-адрес, ссылка на стрим, путь до видео)

        Returns:
            dict: Предсказание для каждого кадра

        Yields:
            Iterator[dict]: Генератор предсказаний для стрима
        """
        cap = cv2.VideoCapture(stream_path)
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            result = self.light_model(frame, verbose=False, conf=self.model_conf)
            detection_results = self.handle_result(result, frame)

            if detection_results:
                yield self.post_process(detection_results)
            else:
                yield None, convert_to_base64(frame)

    def predict(self, path: str, mode: str = "hard_mode") -> tuple:
        """
        predict Запуск предсказания

        Args:
            path (str): путь/ссылка до объекта предсказания (видео, кадр, стрим и т.п.)
            mode (str, optional): Режим работы: hard_mode - предсказание по видео, light_mode - предсказание по стриму. Defaults to 'hard_mode'.

        Returns:
            tuple: Кортеж, хранящий метку класса и демонстрационный кадр
        """
        self.detection_mode = mode

        if self.detection_mode == "hard_mode" and self.hard_model:
            result = self.process_hard(path)
        elif self.detection_mode == "light_mode" and self.light_model:
            result = self.process_light(path)
        if result:
            return self.post_process(result)
        else:
            return "No class", "https://static.wikia.nocookie.net/memes9731/images/4/4e/Pepe-the-frog-internet-meme-sadness-know-your-meme-sad.jpg/revision/latest/thumbnail/width/360/height/360?cb=20200605055540&path-prefix=ru"