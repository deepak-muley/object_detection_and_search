import os
import time
import json
import cv2

from flask import Flask, request, render_template, Response
from redis import Redis
from json_tricks import dump, dumps, load, loads, strip_comments

from camera import Camera, RTSPVideoStream, YoutTubeVideoStream

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = Flask(__name__)

redis = Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'])
bind_port = int(os.environ['BIND_PORT'])

@app.route('/')
def hello():
    redis.incr('hits')
    total_hits = redis.get('hits').decode()
    return f'Hello from Redis! I have been seen {total_hits} times.'


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    rtspurl = request.args.get('rtspurl')
    if rtspurl is None:
        return "Please provide ?rtspurl=<rtsp url> parameter"
    log.debug("Received rtspurl %s", rtspurl)

    return Response(gen(Camera(rtspurl)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def create_message(frame):
    return json.dumps(frame.tolist())

@app.route('/read_rtsp_frame')
def read_rtsp_frame():
    # here we want to get the value of rtsp url (i.e. ?rtspurl=rtsp://u:p/url)
    rtspurl = request.args.get('rtspurl')
    if rtspurl is None:
        return "Please provide ?rtspurl=<rtsp url> parameter"
    log.debug("Received rtspurl %s", rtspurl)
    cam = Camera(rtspurl)

    #Read one frame
    # while True:
    frame = cam.get_frame()
    cam.release()
    if frame is None:
        return "Frame is None"
    else:
        width = 416
        height = 416
        dim = (width, height)
        frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
        log.debug("Frame data : %s %s", type(frame), frame)
        redis.publish('channel-input-video-frame', create_message(frame))
    return "Published the first frame to redis successfully"

@app.route('/read_youtube_video')
def read_youtube_video():
    # here we want to get the value of rtsp url (i.e. ?rtspurl=rtsp://u:p/url)
    url = request.args.get('url')
    if url is None:
        return "Please provide ?url=<youtube url> parameter"
    log.debug("Received rtspurl %s", url)
    yt_video_stream = YoutTubeVideoStream(url)

    #Read one frame
    while True:
        frame = yt_video_stream.get_frame()
        #yt_video_stream.stop()
        if frame is None:
            return "Frame is None"
        else:
            # width = 416
            # height = 416
            width = 50
            height = 50
            dim = (width, height)
            frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
            log.debug("Frame data : %s %s", type(frame), frame)
            redis.publish('channel-input-video-frame', create_message(frame))
        time.sleep(5)
    return "Published the first frame to redis successfully"

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=bind_port)