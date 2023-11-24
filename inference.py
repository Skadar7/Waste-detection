from model import CDWnet
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-v', '--video-path', help='Path to video', type=str, default='./data/A832OX790_09_19_2023 20_13_22.mp4')
parser.add_argument('-i', '--image-path', help='Path to image', type=str, default='./data/3340659_concrete.jpg')
parser.add_argument('-hd', '--hard-detection-model', help='Path to YOLO detection model weights', type=str, default='./models/yolov8l_e20_b8_im720.pt')
parser.add_argument('-ld', '--light-detection-model', help='Path to YOLO detection model weights', type=str, default='./models/yolov8l_e20_b8_im720.pt')

args = parser.parse_args()

model = CDWnet(hard_model=args.hard_detection_model, light_model=args.light_detection_model)

class_res, image = model.predict(args.video_path)
# class_res, image = model.predict(args.image_path, mode='light_mode')

print(f'CDW Class: {class_res}')