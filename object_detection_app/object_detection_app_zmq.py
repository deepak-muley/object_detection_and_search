import os
import time
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

import cv2
import numpy as np

from flask import Flask, request, render_template, Response
from vidgear.gears import NetGear

app = Flask(__name__)

bind_port = int(os.environ['BIND_PORT'])
client = NetGear(address=os.environ['ZMQ_SERVER_HOST'],
                port=os.environ['ZMQ_SERVER_PORT'],
                protocol="tcp",
                pattern=0,
                receive_mode=True,
                logging=True)

def start_message_loop():
    while True:
        frame = client.recv()
        log.debug('Image received')
        image_np = np.copy(frame)
        # check if frame is None
        if image_np is None:
            # if True break the infinite loop
            break
        processFrame(image_np)

def processFrame(frame):
    # Load Yolo
    net = cv2.dnn.readNet("weights/yolov3.weights", "cfg/yolov3.cfg")
    classes = []
    with open("coco.names", "r") as f:
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

    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = confidences[i]
            color = colors[class_ids[i]]
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, label + " " + str(round(confidence, 2)), (x, y + 30), font, 3, color, 3)

    cv2.putText(frame, "FPS: " + str(round(fps, 2)), (10, 50), font, 4, (0, 0, 0), 3)
    cv2.imwrite(os.path.join("/", "frame.jpg"), frame)  # save frame as JPEG file


if __name__ == "__main__":
    start_message_loop()
    #app.run(host="0.0.0.0", debug=True, port=bind_port)