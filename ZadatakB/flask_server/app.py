import base64
import json
import pickle

import numpy as np
import requests
import tensorflow as tf
from flask import Flask, Response, jsonify, request
from PIL import Image
from sklearn.neighbors import KNeighborsClassifier
from tensorflow.keras.applications.inception_v3 import preprocess_input
from tensorflow.keras.preprocessing import image

app = Flask(__name__)

PICKLE_PATH = 'features_pickle.pkl'

url = 'http://zadatakb_tf_serving_1:8501/v1/models/soda_classifier:predict'

def process_image(img):
    img_data = image.img_to_array(img)
    img_data = preprocess_input(img_data)

    return img_data

#Extract features
def get_features(img):

    payload = {
            'instances': [{'image_input': img.tolist()}]
        }

    r = requests.post(url, json = payload)
    features = json.loads(r.content)['predictions'][0]
    return features

@app.route('/item', methods = ['POST'])
def add_item():
    if request.method == 'POST':

        item_name = request.get_json()['itemName']
        base64img = request.get_json()['imageBase64'].encode('utf-8')
        img = base64.b64decode(base64img)

        with open('img_temp.jpg', 'wb') as f:
            f.write(img)

        img = image.load_img('img_temp.jpg', target_size = (224, 224))
        processed_img = process_image(img)

        features = get_features(processed_img)

        #Save the extracted features in a pickled dictionary for future use. 
        with open(PICKLE_PATH, 'rb') as f:
            d = pickle.load(f)

        d[item_name] = features

        with open(PICKLE_PATH, 'wb') as f:
            pickle.dump(d, f)

        status_code = Response(status = 201)
        return status_code

@app.route('/similar', methods = ['POST'])
def find_similar():
    if request.method == 'POST':
        
        n = int(request.get_json()['n'])
        base64img = request.get_json()['imageBase64'].encode('utf-8')
        img = base64.b64decode(base64img)

        with open('img_temp.jpg', 'wb') as f:
            f.write(img)

        img = image.load_img('img_temp.jpg', target_size = (224, 224))
        processed_img = process_image(img)
        extracted_features = np.array(get_features(processed_img))
        

        with open(PICKLE_PATH, 'rb') as f:
            data = pickle.load(f)
        item_names = np.array(list(data.keys()))
        features = np.array(list(data.values()))

        neigh = KNeighborsClassifier(n_neighbors = n).fit(features, item_names)

        predictions = neigh.kneighbors(extracted_features.reshape(1, -1))
        distances = predictions[0][0]
        distances = [1/(1 + d) for d in distances]
        indexes = predictions[1][0]
        labels = [item_names[i] for i in indexes]
  
        response = [{labels[i]: str(distances[i])} for i in range(len(labels))]
     

        return jsonify(response)


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, debug = True)
