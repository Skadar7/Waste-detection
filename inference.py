from model import CDWnet
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-v', '--video-path', help='Path to video folder', type=str, default='./data')
parser.add_argument('-d', '--detection-model', help='Path to YOLO detection model weights', type=str, default='models/yolo_best.pt')

args = parser.parse_args()

H_MODEL_PATH = './models/yolov8l_e20_b8_im720.pt'
VIDEO_PATH = './data/3554032.mp4'

model = CDWnet(hard_model=args.detection_model)
class_res, image = model.predict(args.video_path)
print(f'CDW Class: {class_res}')