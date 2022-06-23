
import json

import uuid

from django.db.utils import IntegrityError
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import celery
from app.models import Category, Item
from app.tasks import classify_similar, extract_features
from app.utils import delete_embeddings
from celery.result import AsyncResult

from . import minio_storage

url = 'http://project_tf_serving_1:8501/v1/models/soda_classifier:predict'

BUCKET_NAME = 'thumbnail-images'
SUFFIX = '.jpg'


class ListItems(APIView):

    def post(self, request):
        data = request.data

        if 'itemName' in data.keys():

            item_name = data['itemName']
            base64img = data['imageBase64']
            category_name = data['categoryName']

            try:
                category = Category.objects.get(name = category_name)
            except Category.DoesNotExist:
                return JsonResponse({'message': 'Category does not exist.'}, status = status.HTTP_404_NOT_FOUND)

            extract_features_task = extract_features.delay(base64img, item_name)

            while True:
                if extract_features_task.status == celery.states.FAILURE:
                    return Response('Model error.', status = 500)
                elif extract_features_task.status == celery.states.SUCCESS:

                    item_uuid = str(uuid.uuid1())
                    img_name = item_uuid + '.jpg'

                    item = Item.objects.create(uuid = item_uuid, name = item_name, category = category)
                    item.save()
                    minio_storage.post(base64img, img_name, BUCKET_NAME)

                    return Response(status = 201)
        
        elif 'n' in data.keys():

            n = int(data['n'])
            base64img = data['imageBase64']

            classify_similar_task = classify_similar.delay(base64img, n)

            while True:
                if classify_similar_task.status == celery.states.FAILURE:
                    return Response(status = 500)
                
                elif classify_similar_task.status == celery.states.SUCCESS:
                    
                    predictions = AsyncResult(classify_similar_task.id).get()

            
                    return Response(predictions, status = status.HTTP_200_OK)

        else:
            return Response(status = 404)
        

    def get(self, request):

        items = Item.objects.all()
        data = []

        for item in items:
            #thumbnail_url = minio_storage.get_url(item.uuid + SUFFIX)
            data.append({'name': item.name, 'uuid': item.uuid, 'category': item.category.name}) 
        return Response(data)

    def delete(self, request):
        
        data = request.data
        if 'uuid' in data.keys():

            try:
                item = Item.objects.get(uuid = data['uuid'])
            except Item.DoesNotExist:
                    return JsonResponse({'message': 'Item does not exist.'}, status = status.HTTP_404_NOT_FOUND)

            file_name = item.uuid + SUFFIX
            minio_storage.delete_photo(file_name)
            item.delete()
            return JsonResponse({'message': 'Item was deleted successfully.'}, status = status.HTTP_204_NO_CONTENT)
                
        elif 'name' in data.keys():
            item_name = data['name']
            try:
                items = Item.objects.filter(name = item_name)
            except Item.DoesNotExist:
                return JsonResponse({'message': 'Item does not exist.'}, status = status.HTTP_404_NOT_FOUND)

            for item in items:
                file_name = item.uuid + SUFFIX
                minio_storage.delete_photo(file_name)
            items.delete()
            delete_embeddings(item_name)

            return JsonResponse({'message': 'Item(s) were deleted successfully.'}, status = status.HTTP_204_NO_CONTENT)
        
        return Response(status = 400)

    def put(self, request):
        data = request.data
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

    def post(self, request):

        data = request.data

        category_name = data['categoryName']
        category_uuid = uuid.uuid1()

        try:
            Category.objects.create(uuid = category_uuid, name = category_name)

        except IntegrityError:
            return JsonResponse({'message': 'The category already exists.'}, status = status.HTTP_400_BAD_REQUEST)

        
        return JsonResponse({'message': 'Category added.'}, status = 201)
