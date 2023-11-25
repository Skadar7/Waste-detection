from flask import Flask,render_template,Response, stream_with_context
import cv2
import os

from model import CDWnet 

app=Flask(__name__)
model = CDWnet(light_model_path="weights/yolo8s_30ep.pt")


@app.route('/video')
def video():
    return Response(model.process_light_stream("video/video.mp4"),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port=7000)

