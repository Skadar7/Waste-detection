from model import CDWnet

H_MODEL_PATH = './models/yolov8l_e20_b8_im720.pt'
VIDEO_PATH = './data/3554032.mp4'

model = CDWnet(hard_model=H_MODEL_PATH)
res_class = model.predict(VIDEO_PATH)
print(res_class)