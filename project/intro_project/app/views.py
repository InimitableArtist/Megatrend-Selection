
import json
import uuid
from email.charset import BASE64

from django.db import transaction
from django.db.utils import IntegrityError
from django.http.response import JsonResponse
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

BASE64IMG = 'imageBase64'
ITEM_NAME = 'itemName'
CATEGORY_NAME = 'categoryName'


class ListItems(APIView):

    def post(self, request):
        data = request.data
        params = data.keys()
        if ITEM_NAME in params and CATEGORY_NAME in params:

            item_name = data[ITEM_NAME]
            category_name = data[CATEGORY_NAME]

            try:
                category = Category.objects.get(name = category_name)
            except Category.DoesNotExist:
                return JsonResponse({'message': 'Category does not exist.'}, status = status.HTTP_404_NOT_FOUND)

            

            if BASE64IMG in params:
                base64img = data[BASE64IMG]
                extract_features_task = extract_features.delay(base64img, item_name)
                while True:
                    if extract_features_task.status == celery.states.FAILURE:
                        return Response('Model error.', status = 500)
                    elif extract_features_task.status == celery.states.SUCCESS:
                        if extract_features_task.get() == 'FAILED':
                            return Response('Invalid image was inputted.', status = status.HTTP_400_BAD_REQUEST) 

                        item_uuid = str(uuid.uuid1())
                        img_name = item_uuid + '.jpg'

                        item = Item.objects.create(uuid = item_uuid, name = item_name, category = category)
                        item.save()
                        minio_storage.post(base64img, img_name, BUCKET_NAME)

                        return Response(status = 201)
                        
            #Creating a new entry without an image     
            else:
                item_uuid = str(uuid.uuid1())
                item = Item.objects.create(uuid = item_uuid, name = item_name, category = category)
                item.save()
                return Response(status = 201)
            
        
        elif 'n' in data.keys():

            n = int(data['n'])
            base64img = data[BASE64IMG]

            classify_similar_task = classify_similar.delay(base64img, n)

            while True:
                if classify_similar_task.status == celery.states.FAILURE:
                    return Response(status = 500)
                
                elif classify_similar_task.status == celery.states.SUCCESS:
                    if classify_similar_task.get() == 'FAILED':
                            return Response('The requested num of neighbors is greater than max', status = status.HTTP_400_BAD_REQUEST)
                    predictions = AsyncResult(classify_similar_task.id).get()

            
                    return Response(predictions, status = status.HTTP_200_OK)

        else:
            return Response(status = 400)
        

    def get(self, item_name):
        item_name = self.request.GET.get(ITEM_NAME, None)
        if item_name:
            items = Item.objects.filter(name = item_name)
            if items.count() == 0:
                return Response('No entries found.', status = status.HTTP_404_NOT_FOUND)
         
        else: 
            items = Item.objects.all() 
        
        response_data = []
        
        

        for item in items:
            #thumbnail_url = minio_storage.get_url(item.uuid + SUFFIX)
            response_data.append({'name': item.name, 'uuid': item.uuid, 'category': item.category.name}) 
        return Response(response_data, status = status.HTTP_200_OK)

    def delete(self, request):
        
        data = request.data
        params = data.keys()
        if 'uuid' in params:

            try:
                item = Item.objects.get(uuid = data['uuid'])
            except Item.DoesNotExist:
                    return JsonResponse({'message': 'Item does not exist.'}, status = status.HTTP_404_NOT_FOUND)

            file_name = item.uuid + SUFFIX
            minio_storage.delete_photo(file_name)

            item.delete()
            return JsonResponse({'message': 'Item was deleted successfully.'}, status = status.HTTP_204_NO_CONTENT)
                
        elif ITEM_NAME in params:
            item_name = data[ITEM_NAME]
            try:
                items = Item.objects.filter(name = item_name)
            except Item.DoesNotExist:
                return JsonResponse({'message': 'Item does not exist.'}, status = status.HTTP_404_NOT_FOUND)

            for item in items:
                file_name = item.uuid + SUFFIX
                minio_storage.delete_photo(file_name)
            items.delete()
            try:
                delete_embeddings(item_name)
            except KeyError:
                #No embeddings saved
                pass

            return JsonResponse({'message': 'Item(s) were deleted successfully.'}, status = status.HTTP_204_NO_CONTENT)
        
        return Response(status = 400)

    def put(self, request):
        data = request.data
        params = data.keys()
        try:
            item = Item.objects.get(uuid = data['uuid'])
        except Item.DoesNotExist:
            return JsonResponse({'message': 'Item does not exist.'}, status = status.HTTP_404_NOT_FOUND)

        if ITEM_NAME in params:
            item.name = data[ITEM_NAME]
            item.save()

        elif CATEGORY_NAME in params:
            try:
                category = Category.objects.get(name = data[CATEGORY_NAME])
            
            except Category.DoesNotExist:
                return JsonResponse({'message': 'The category you are trying to update does not exist.'}, status = status.HTTP_404_NOT_FOUND)

            item.category = category
            item.save()

        elif BASE64IMG in params:
            base64img = data[BASE64IMG]
            extract_features_task = extract_features.delay(base64img, item.name)
            while True:
                if extract_features_task.status == celery.states.FAILURE:
                    return Response(status = 500)
                
                elif extract_features_task.status == celery.states.SUCCESS:
                    
                    if extract_features_task.get() == 'FAILED':
                        return Response('Invalid image was inputted.', status = status.HTTP_400_BAD_REQUEST) 
                    
                    img_name = item.uuid + '.jpg'

                    minio_storage.delete_photo(img_name, BUCKET_NAME)
                    minio_storage.post(base64img, img_name, BUCKET_NAME)
                    return Response(status = 201)
                        



            
        return JsonResponse({'message': 'Item updated.'}, status = 201)



class ListCategories(APIView):

    def get(self, request):

        categories = Category.objects.all()
        response_data = []
        for ct in categories:
            response_data.append({'uuid': ct.uuid, 'name': ct.name})
        
        return Response(response_data, status = status.HTTP_200_OK)

    def post(self, request):

        data = request.data

        category_name = data[CATEGORY_NAME]
        category_uuid = uuid.uuid1()

        try:
            with transaction.atomic():
                Category.objects.create(uuid = category_uuid, name = category_name)
            
        except IntegrityError:
            return JsonResponse({'message': 'The category already exists.'}, status = status.HTTP_400_BAD_REQUEST)

        
        return JsonResponse({'message': 'Category added.'}, status = 201)
