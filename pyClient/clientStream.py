import asyncio
import json
import websockets
from model import CDWnet
import base64

H_MODEL_PATH = "weights/yolo8s_30ep.pt"
model = CDWnet(light_model=H_MODEL_PATH,)
 
async def sendFrames(ws):
    for i,f in model.process_light_stream("video/video.mp4"):
        if f is None:
            r = { 'result': "не найдено",'b64':"None"}
            jsonn = json.dumps(r)
            #print(r["result"])
            await ws.send(jsonn)
        else:    
        
            frame = str(f)[2:-1]
            r = { 'result': i,'b64':"data:image/jpeg;base64,"+frame}
            #print(r["result"])
            jsonn = json.dumps(r) # note i gave it a different name
            await ws.send(jsonn)
   
    
async def test():
    print("ws")
    async with websockets.connect("ws://localhost:8080/ws") as websocket:
        await sendFrames(websocket)
