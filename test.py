from model import CDWnet
from os import listdir
from os.path import isfile, join
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-hd', '--hard-detection-model', help='Path to YOLO detection model weights', type=str, default='./models/yolov8l_e20_b8_im720.pt')
parser.add_argument('-t', '--test-path', help='Path to directory with videos', type=str, default='./videos')

args = parser.parse_args()

model = CDWnet(hard_model=args.hard_detection_model)

FILES = [f for f in listdir(args.test_path) if isfile(join(args.test_path, f))]

res = []

for path in FILES:
    class_res, image = model.predict(f'{args.test_path}/{path}')
    res.append([path, class_res])

for det in res:
    print(f'Video {det[0]}: {det[1]}')
