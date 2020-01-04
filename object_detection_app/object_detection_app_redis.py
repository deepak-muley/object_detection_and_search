import os
import time
import json

import cv2
import numpy as np

from flask import Flask, request, render_template, Response
from redis import Redis
from json_tricks import dump, dumps, load, loads, strip_comments

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

app = Flask(__name__)

redis = Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'])
bind_port = int(os.environ['BIND_PORT'])
p = redis.pubsub() # https://github.com/andymccurdy/redis-py/#publish--subscribe
    
def video_frame_message_handler(message):
    log.debug('MY HANDLER: ', message['data'])
    
def start_message_loop2():
    p.subscribe(**{'channel-input-video-frame': video_frame_message_handler})

def start_message_loop():
    p.subscribe('channel-input-video-frame')
    while True:
        message = p.get_message()
        # MY HANDLER:  {'type': 'subscribe', 'pattern': None, 'channel': b'channel-input-video-frame', 'data': 1}
        if message:
            log.debug('MY HANDLER type data: %s %s', type(message['data']), message)
            frame = message['data']
            if frame == 1:
                continue
            frame_string = json.loads(frame)
            frame = np.array(frame_string, dtype='float32')
            log.debug('MY HANDLER: %s', frame)
            processFrameOpenCV(frame)


def processFrameTF(frame):
    pass

def processFrameOpenCV(frame):
    # Load Yolo
    net = cv2.dnn.readNet("models/yolov3/weights/yolov3.weights", "models/yolov3/cfg/yolov3.cfg")
    classes = []
    with open("models/yolov3/coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    colors = np.random.uniform(0, 255, size=(len(classes), 3))

    font = cv2.FONT_HERSHEY_PLAIN
    height, width, channels = frame.shape

    # Detecting objects
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

    net.setInput(blob)
    outs = net.forward(output_layers)

    # Showing informations on the screen
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.2:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.8, 0.3)

    detected_features = {}
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = confidences[i]
            color = colors[class_ids[i]]
            # cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            # cv2.putText(frame, label + " " + str(round(confidence, 2)), (x, y + 30), font, 3, color, 3)
            detected_features["timestamp"] = time.time()
            detected_features["label"] = label
            detected_features["confidence"] = confidence
            detected_features["box"] = (x, y, w, h)
            detected_features["rectangle_top_left"] = (x, y)
            detected_features["rectangle_bottom_right"] = (x + w, y + h)
            detected_features_json = json.dumps(detected_features)
            redis.publish('channel-features', detected_features_json)

    #cv2.putText(frame, "FPS: " + "str(round(fps, 2))", (10, 50), font, 4, (0, 0, 0), 3)
    #cv2.imwrite(os.path.join("/", "data", "frame.jpg"), frame)  # save frame as JPEG file
    #cv2.imshow('frame', frame)
    #cv2.resizeWindow('frame', 600,600)

if __name__ == "__main__":
    start_message_loop()