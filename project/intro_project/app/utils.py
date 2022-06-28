import base64
import io
import json


import numpy as np
import requests
import pickle
from numpy.linalg import norm
from PIL import Image
from tensorflow.keras.applications.inception_v3 import preprocess_input
from tensorflow.keras.preprocessing import image
import tensorflow as tf

URL = 'http://project_tf_serving_1:8501/v1/models/soda_classifier:predict'
URL_DETECTION = 'http://project_tf_serving_1:8501/v1/models/soda_detection:predict'

PICKLE_PATH = 'features_pickle.pkl'

BOTTLE_LABEL = 44

def process_image(img):
    img_data = image.img_to_array(img)
    img_data = preprocess_input(img_data)
    return img_data

def call_tf_serving(img, url, name):
    payload = {
        'instances': [{name: img.tolist()}]
    }

    r = requests.post(url, json = payload)

    features = json.loads(r.content)['predictions'][0]

    return features

def get_embeddings(base64img):
    img_bytes = base64.b64decode(base64img.encode('utf-8'))

    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    detection_bbox = run_detector(img)
    w, h = img.size
    if detection_bbox:
        x, y = detection_bbox[1] * w, detection_bbox[0] * h
        n_w, n_h = (detection_bbox[3] * w - detection_bbox[1] * w), (detection_bbox[2] * h - detection_bbox[0] * h)
        area = (x, y, x + n_w, y + n_h)
        img = img.crop(area)
        #img.save('cropped.jpg') 

    processed_img = process_image(img)
    embeddings = np.array(call_tf_serving(processed_img, URL, 'image_input')).flatten()
 
    embeddings = embeddings / norm(embeddings)

    return embeddings

def delete_embeddings(item_name):
    with open(PICKLE_PATH, 'rb') as f:
        d = pickle.load(f)

    del d[item_name]

    with open(PICKLE_PATH, 'wb') as f:
        pickle.dump(d, f)

def run_detector(img):
    img_np = np.array(img)

    payload = {
        'instances': [{'input_tensor': img_np.tolist()}]}

    r = requests.post(URL_DETECTION, json = payload)
    result = json.loads(r.content)['predictions'][0]

    detection_bbox = None
    for i in range(len(result)):
        detections_class = int(result['detection_classes'][i])
        detection_score = result['detection_scores'][i]
        if detections_class == BOTTLE_LABEL and detection_score > 0.25:
            detection_bbox = result['detection_boxes'][i]
            break
    

    return detection_bbox

