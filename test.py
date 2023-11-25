from model import CDWnet
from os import listdir
from os.path import isfile, join
import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-hd', '--hard-detection-model', help='Path to YOLO detection model weights', type=str, default='./models/yolov8l_e20_b8_im720.pt')
parser.add_argument('-t', '--test-path', help='Path to directory with videos', type=str, default='./videos')
parser.add_argument('-o', '--output-path', help='Save path for csv file', type=str, default='./result.csv')

args = parser.parse_args()

model = CDWnet(hard_model=args.hard_detection_model)

FILES = [f for f in listdir(args.test_path) if isfile(join(args.test_path, f))]

classes = {
    'Brick': 'кирпич',
    'Concrete': 'бетон',
    'priming': 'грунт',
    'Tree': 'дерево'
}

res = []

for path in FILES:
    class_res, image = model.predict(f'{args.test_path}/{path}')
    res.append([path, classes[class_res]])

with open(args.output_path, 'w') as f:
    writer = csv.writer(f, lineterminator='\n', delimiter=';')
    writer.writerows(res)
