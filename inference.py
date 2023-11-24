from model import CDWnet
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-v', '--video-path', help='Path to video folder', type=str, default='./data/3554032.mp4')
parser.add_argument('-d', '--detection-model', help='Path to YOLO detection model weights', type=str, default='./models/yolov8l_e20_b8_im720.pt')

args = parser.parse_args()

model = CDWnet(hard_model=args.detection_model)
class_res, image = model.predict(args.video_path)
print(f'CDW Class: {class_res}')