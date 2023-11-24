import cv2
from os import listdir
from os.path import isfile, join
import base64

def post_process(detetction_result):
    vals = list(detetction_result.values())
    final_class = max(vals,key=vals.count)
    return final_class

def crop_video(dir_path, save_path):
    files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]

    for path in files:
        cap = cv2.VideoCapture(f'{dir_path}/{path}')
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_number = 127 * fps 
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number-1)
        res, frame = cap.read()
        img_path = f"{save_path}/{path[:-4]}_tree.jpg"
        try:
            cv2.imwrite(img_path, frame)
        except:
            continue

def plot_boxes(frame, xyxy, label):
    x1 = int(xyxy[0])
    y1 = int(xyxy[1])
    x2 = int(xyxy[2])
    y2 = int(xyxy[3])

    (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    frame = cv2.rectangle(frame, (x1, y1 - 20), (x1 + w, y1), (0, 0, 255), -1)
    frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
    frame = cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return frame

def convert_to_base64(frame):
    success, buffer = cv2.imencode('.jpg', frame)
    base64_img = base64.b64encode(buffer)
    return base64_img
