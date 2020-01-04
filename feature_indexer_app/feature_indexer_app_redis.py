import os
import time
import json

import cv2
import numpy as np

from redis import Redis
from elasticsearch_client import ElasticSearchWrapper

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

redis = Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'])
bind_port = int(os.environ['BIND_PORT'])
p = redis.pubsub()  # https://github.com/andymccurdy/redis-py/#publish--subscribe

es = ElasticSearchWrapper(os.environ['ES_HOST'], os.environ['ES_PORT'])
feature_timeline_index_name = "feature_timeline"
features_doc_type = "features"

def prepareElasticSearch():
    # index settings
    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "members": {
                "dynamic": "strict",
                "properties": {
                    "timestamp": {
                        "type": "date"
                    },
                    "label": {
                        "type": "text"
                    },
                    "confidence": {
                        "type": "float"
                    },
                    "box": {
                        "type": "dense_vector",
                        "dims": 4
                    },
                    "rectangle_top_left": {
                        "type": "dense_vector",
                        "dims": 2
                    },
                    "rectangle_bottom_right": {
                        "type": "dense_vector",
                        "dims": 2
                    }
                }
            }
        }
    }
    es.create_index(feature_timeline_index_name, settings)
    log.info("Connected to es: %s", es.connect())

def feature_message_handler(message):
    log.debug('MY HANDLER: ', message['data'])
    
def start_message_loop2():
    p.subscribe(**{'channel-features': feature_message_handler})

def start_message_loop():
    p.subscribe('channel-features')
    while True:
        message = p.get_message()
        if message:
            log.debug('MY HANDLER type data: %s %s', type(message['data']), message)
            detected_features_json = message['data']
            if detected_features_json == 1:
                continue
            log.debug('MY HANDLER: %s', detected_features_json)
            #b'{"timestamp": 1578174786.095568, "label": "person", "confidence": [0.996425986289978, 0.7918809652328491, 0.26725688576698303], "box": [-6, 20, 370, 373], "rectangle_top_left": [-6, 20], "rectangle_bottom_right": [364, 393]}'
            #detected_features = json.loads(detected_features_json)
            processFeatures(detected_features_json)

def processFeatures(detected_features_json):
    # dump the features as a document in the elastic search
    log.info("Processing detected_features: %s", detected_features_json)
    es.store_record(feature_timeline_index_name, features_doc_type, detected_features_json)

if __name__ == "__main__":
    prepareElasticSearch()
    start_message_loop()