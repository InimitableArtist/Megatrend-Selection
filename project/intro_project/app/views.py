from django.shortcuts import render
from django.http import HttpResponse
import base64
import json
import pickle
import numpy as np
from numpy.linalg import norm
import requests
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.inception_v3 import preprocess_input
from django.views.decorators.csrf import csrf_exempt
from sklearn.neighbors import KNeighborsClassifier

PICKLE_PATH = 'features_pickle.pkl'

url = 'http://project_tf_serving_1:8501/v1/models/soda_classifier:predict'

def process_image(img):
    img_data = image.img_to_array(img)
    img_data = preprocess_input(img_data)
    return img_data

def get_features(img):
    payload = {
        'instances': [{'image_input': img.tolist()}]
    }

    r = requests.post(url, json = payload)
    features = json.loads(r.content)['predictions'][0]

    return features

@csrf_exempt
def add_item(request):
    if request.method == 'POST':

        data = json.loads(request.body)

        item_name = data['itemName']
        base64img = data['imageBase64'].encode('utf-8')
        img = base64.b64decode(base64img)

        with open('img_temp.jpg', 'wb') as f:
            f.write(img)

        img = image.load_img('img_temp.jpg', target_size = (224, 224))
        processed_img = process_image(img)

        features = np.array(get_features(processed_img)).flatten()
        normalized_features = features / norm(features)

        #Save the extracted features in a pickled dictionary for future use. 
        with open(PICKLE_PATH, 'rb') as f:
            d = pickle.load(f)
        
        if item_name not in d.keys():
            d[item_name] = [normalized_features, 1]
        else:
            saved_examples = d[item_name][1]
            f = (d[item_name][0] * saved_examples + normalized_features) / (saved_examples + 1)
            d[item_name][0] = f
            d[item_name][1] = saved_examples + 1

        with open(PICKLE_PATH, 'wb') as f:
            pickle.dump(d, f)

        status_code = HttpResponse(status = 201)
        return status_code

@csrf_exempt
def find_similar(request):
    if request.method == 'POST':
        
        data = json.loads(request.body)
        n = int(data['n'])
        base64img = data['imageBase64'].encode('utf-8')
        img = base64.b64decode(base64img)

        with open('img_temp.jpg', 'wb') as f:
            f.write(img)

        img = image.load_img('img_temp.jpg', target_size = (224, 224))
        processed_img = process_image(img)
        extracted_features = np.array(get_features(processed_img)).flatten()
        normalized_features = extracted_features / norm(extracted_features)
        #extracted_features = np.array(get_features(file)).flatten()
        

        with open(PICKLE_PATH, 'rb') as f:
            data = pickle.load(f)
        item_names = np.array(list(data.keys()))
        features = np.array([i[0] for i in data.values()])


        #Find n closest neighbors based on the extracted features, convert distance to similarity score.
        neigh = KNeighborsClassifier(n_neighbors = n).fit(features, item_names)

        predictions = neigh.kneighbors(normalized_features.reshape(1, -1))
        distances = predictions[0][0]
        distances = [1/(1+d) for d in distances]

        indexes = predictions[1][0]
        labels = [item_names[i] for i in indexes]
  
        response = [{labels[i]: str(distances[i])} for i in range(len(labels))]

        return HttpResponse(json.dumps(response))
