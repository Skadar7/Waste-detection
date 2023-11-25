import base64
import os
from flask import Flask, request
#from clientModel import test
import asyncio
from model import CDWnet

H_MODEL_PATH = "weights/detr-l-10ep-3v.pt"
VIDEO_PATH = "video/video.mp4"
app = Flask(__name__)
model = CDWnet(hard_model_path=H_MODEL_PATH)


def treatmenImagetVideo(json):

    #json->video
    fh = open(VIDEO_PATH, "wb")
    fh.write(base64.b64decode(json["b64"]))
    fh.close()

    res_class,image = model.predict(VIDEO_PATH)

    image = str(image)[2:-1]

    answer = {"result":res_class,"b64":"data:image/jpeg;base64,"+image,"video_name":json["video_name"]}

    return answer


@app.route('/sendFromPyVideo', methods=['POST'])
def treatmentVideo():
    return treatmenImagetVideo(request.json)

# @app.route('/start')
# def index():
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     asyncio.get_event_loop().run_until_complete(test())
#     return 'STREAM START'

app.run(host='0.0.0.0', port=5000)