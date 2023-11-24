def post_process(detetction_result):
    vals = list(detetction_result.values())
    final_class = max(vals,key=vals.count)[0]
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