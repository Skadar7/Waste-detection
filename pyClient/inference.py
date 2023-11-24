from model import CDWnet
import argparse

parser = argparse.ArgumentParser()

# parser.add_argument('-i', '--input', help='Path to video folder', type=str, default='./data')
# parser.add_argument('-o', '--output', help='Output csv-file', type=str, default='results.csv')
# parser.add_argument('-d', '--detection-weights', help='Path to YOLO detection model weights', type=str, default='models/yolo_best.pt')

args = parser.parse_args()

H_MODEL_PATH = './models/yolov8l_e20_b8_im720.pt'
VIDEO_PATH = './data/3554032.mp4'

model = CDWnet(hard_model=H_MODEL_PATH)
res_class = model.predict(VIDEO_PATH)