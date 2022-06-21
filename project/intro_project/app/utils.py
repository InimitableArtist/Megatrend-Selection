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

URL = 'http://project_tf_serving_1:8501/v1/models/soda_classifier:predict'

PICKLE_PATH = 'features_pickle.pkl'

def process_image(img):
    img_data = image.img_to_array(img)
    img_data = preprocess_input(img_data)
    return img_data

def call_tf_serving(img):
    payload = {
        'instances': [{'image_input': img.tolist()}]
    }

    r = requests.post(URL, json = payload)

    features = json.loads(r.content)['predictions'][0]

    return features

def get_embeddings(base64img):
    img_bytes = base64.urlsafe_b64decode(base64img.encode('utf-8'))
    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')

    processed_img = process_image(img)
    embeddings = np.array(call_tf_serving(processed_img)).flatten()
 
    embeddings = embeddings / norm(embeddings)

    return embeddings

def delete_embeddings(item_name):
    with open(PICKLE_PATH, 'rb') as f:
        d = pickle.load(f)

    del d[item_name]

    with open(PICKLE_PATH, 'wb') as f:
        pickle.dump(d, f)
