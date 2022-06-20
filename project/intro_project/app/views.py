import base64
import io
import json
import pickle
import uuid

import numpy as np
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from numpy.linalg import norm
from PIL import Image
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from sklearn.neighbors import KNeighborsClassifier

from app.db_serializers import ItemSerializer
from app.models import Category, Item
from app.utils import get_features, process_image

PICKLE_PATH = 'features_pickle.pkl'

url = 'http://project_tf_serving_1:8501/v1/models/soda_classifier:predict'


class ListItems(APIView):

    def post(self, request):
        data = json.loads(request.body)

        if 'itemName' in data.keys():

            item_name = data['itemName']
            base64img = data['imageBase64'].encode('utf-8')

            


            category_name = data['categoryName']

            try:
                category = Category.objects.get(name = category_name)
            except Category.DoesNotExist:
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

            status_code = Response(status = 201)
            return status_code
        
        elif 'n' in data.keys():
            n = int(data['n'])
            base64img = data['imageBase64'].encode('utf-8')
            img_bytes = base64.urlsafe_b64decode(base64img)
            img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
            processed_img = process_image(img)
            processed_img = process_image(img)
            extracted_features = np.array(get_features(processed_img)).flatten()
            normalized_features = extracted_features / norm(extracted_features)
            #extracted_features = np.array(get_features(file)).flatten()
            with open(PICKLE_PATH, 'rb') as f:
                data = pickle.load(f)
            item_uuids= np.array(list(data.keys()))
            features = np.array([i[0] for i in data.values()])
            #Find n closest neighbors based on the extracted features, convert distance to similarity score.
            neigh = KNeighborsClassifier(n_neighbors = n).fit(features, item_uuids)
            predictions = neigh.kneighbors(normalized_features.reshape(1, -1))
            distances = predictions[0][0]
            distances = [1/(1+d) for d in distances]
            indexes = predictions[1][0]
            labels = [Item.objects.get(uuid = item_uuids[i]) for i in indexes]

            response = [{str(labels[i]): str(distances[i])} for i in range(len(labels))]
            return HttpResponse(json.dumps(response))

        else:
            return Response(status = 404)
        

    def get(self, request):

        items = Item.objects.all()
        data = []

        for item in items:
            #item_serializer = ItemSerializer(item)
            data.append({'name': item.name, 'uuid': item.uuid, 'category': item.category.name}) 
        return Response(json.dumps(data))

    def delete(self, request):
        data = json.loads(request.body)
        try:
            item = Item.objects.get(uuid = data['uuid'])
        except Item.DoesNotExist:
                return JsonResponse({'message': 'Item does not exist.'}, status = status.HTTP_404_NOT_FOUND)

        item_name = item.name

        item.delete()
        return JsonResponse({'message': 'Item {0} was deleted successfully.'.format(item_name)}, status = status.HTTP_204_NO_CONTENT)

    def put(self, request):
        data = json.loads(request.body)
        try:
            item = Item.objects.get(uuid = data['uuid'])
        except Item.DoesNotExist:
            return JsonResponse({'message': 'Item does not exist.'}, status = status.HTTP_404_NOT_FOUND)

        if 'name' in data.keys():
            item.name = data['name']
            item.save()

        elif 'category' in data.keys():
            try:
                category = Category.objects.get(name = data['category'])
            
            except Category.DoesNotExist:
                return JsonResponse({'message': 'The category you are trying to update does not exist.'}, status = status.HTTP_404_NOT_FOUND)

            item.category = category
            item.save()

        return JsonResponse({'message': 'Item updated.'}, status = 201)



class ListCategories(APIView):

    def get(self, request):
        
        categories = Category.objects.all()
        data = []
        for ct in categories:
            data.append({'uuid': ct.uuid, 'name': ct.name})
        
        return Response(json.dumps(data))

