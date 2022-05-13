import base64
import json

import cv2
import numpy as np
import requests
import tensorflow as tf
from flask import Flask, request
from PIL import Image
from tensorflow.keras.preprocessing import image

app = Flask(__name__)

url = 'http://zadataka_tf_serving_1:8501/v1/models/digit_classifier:predict'


@app.route('/classify', methods = ['POST'])
def predict():
    if request.method == 'POST':
        base64img = request.get_json()['imageBase64'].encode('utf-8')

        img = base64.b64decode(base64img)
        with open('img_temp.jpg', 'wb') as f:
            f.write(img)
        
        img = cv2.imread('img_temp.jpg', 1)
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.resize(img, (28, 28))
     
        img = np.expand_dims(img, -1)

        payload = {
            'instances': [{'image_input': img.tolist()}]
        }

        r = requests.post(url, json = payload)
        pred = json.loads(r.content.decode('utf-8'))
        class_ = np.argmax(pred['predictions'])
        score = pred['predictions'][0][class_]

        return {'class': str(class_), 'score': score}
    


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, debug = True)
