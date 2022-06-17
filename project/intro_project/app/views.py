import base64
import io
import json
import pickle
import uuid

import numpy as np
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from app.utils import get_features, process_image
from numpy.linalg import norm
from PIL import Image
from sklearn.neighbors import KNeighborsClassifier
from tensorflow.keras.preprocessing import image

from app.models import Category, Item

PICKLE_PATH = 'features_pickle.pkl'

url = 'http://project_tf_serving_1:8501/v1/models/soda_classifier:predict'

@csrf_exempt
def add_item(request):
    if request.method == 'POST':

        data = json.loads(request.body)

        item_name = data['itemName']
        base64img = data['imageBase64'].encode('utf-8')
        category_name = data['categoryName']
        img = base64.b64decode(base64img)

        try:
            category = Category.objects.get(name = category_name)
        except:
            category_uuid = str(uuid.uuid1())
            category = Category.objects.create(name = category_name, uuid = category_uuid)
            category.save()



        item_uuid = str(uuid.uuid1())

        item = Item.objects.create(uuid = item_uuid, name = item_name, category = category)
        item.save()

        img_bytes = base64.urlsafe_b64decode(base64img)
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        processed_img = process_image(img)

        features = np.array(get_features(processed_img)).flatten()
        normalized_features = features / norm(features)

        #Save the extracted features in a pickled dictionary for future use. 
        with open(PICKLE_PATH, 'rb') as f:
            d = pickle.load(f)
        
        if item_uuid not in d.keys():
            d[item_uuid] = [normalized_features, 1]
        else:
            saved_examples = d[item_uuid][1]
            f = (d[item_uuid][0] * saved_examples + normalized_features) / (saved_examples + 1)
            d[item_uuid][0] = f
            d[item_uuid][1] = saved_examples + 1

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

@csrf_exempt
def get_items(request):
    print('todo...')
