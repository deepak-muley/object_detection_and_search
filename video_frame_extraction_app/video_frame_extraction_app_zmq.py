import os
import time
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

from flask import Flask, request, render_template, Response

from vidgear.gears import NetGear
from camera import VideoStream

app = Flask(__name__)
bind_port = int(os.environ['BIND_PORT'])
server = NetGear(address=os.environ['ZMQ_SERVER_HOST'],
                port=os.environ['ZMQ_SERVER_PORT'],
                protocol="tcp",
                pattern=0,
                receive_mode=False,
                logging=True)

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

    return Response(gen(VideoStream(rtspurl)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/read_rtsp_frame')
def read_rtsp_frame():
    # here we want to get the value of rtsp url (i.e. ?rtspurl=rtsp://u:p/url)
    rtspurl = request.args.get('rtspurl')
    if rtspurl is None:
        return "Please provide ?rtspurl=<rtsp url> parameter"
    log.debug("Received rtspurl %s", rtspurl)
    cam = VideoStream(rtspurl)

    #Read one frame
    frame = cam.get_frame()
    if frame is None:
        return "Frame is None"
    else:
        log.debug("Frame data : %s %s", type(frame), frame)

        # send frame to server
        server.send(frame)
    return "Published the first frame to redis successfully"

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=bind_port)