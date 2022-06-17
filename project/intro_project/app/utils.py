import json

import requests
from tensorflow.keras.applications.inception_v3 import preprocess_input
from tensorflow.keras.preprocessing import image

URL = 'http://project_tf_serving_1:8501/v1/models/soda_classifier:predict'


def process_image(img):
    img_data = image.img_to_array(img)
    img_data = preprocess_input(img_data)
    return img_data

def get_features(img):
    payload = {
        'instances': [{'image_input': img.tolist()}]
    }

    r = requests.post(URL, json = payload)
    features = json.loads(r.content)['predictions'][0]

    return features
