import time
import cv2
import os
import os.path
import numpy as np
from vidgear.gears import VideoGear

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

class Camera(object):
    def __init__(self, source):
        self.vcap = cv2.VideoCapture(source)

    def get_frame(self):
        if not self.vcap:
            return None
        ret, frame = self.vcap.read()
        if ret == False:
            return None
        return frame

    def release(self):
        if self.vcap:
            self.vcap.release()

class VideoStream(object):
    def __init__(self, rtspurl):
        self.rtspurl = rtspurl
        self.stream = VideoGear(source=self.rtspurl).start()

    def stop(self):
        if self.stream:
            self.stream.stop()

    def get_frame(self):
        if not self.stream:
            return None
        frame = self.stream.read()
        return frame