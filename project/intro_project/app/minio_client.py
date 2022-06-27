
import base64
import io
import os
from datetime import timedelta

from minio import Minio
from minio.deleteobjects import DeleteError


BUCKET_NAME = 'thumbnail-images'

class MinioThumbnailStorage:

    FORMAT = '.jpg'
    def __init__(self, client):
        if client is None:
            self.client = Minio(
                endpoint = f'{os.getenv("MINIO_IP")}:{os.getenv("MINIO_PORT")}',
                access_key = os.getenv('MINIO_ROOT_USER'),
                secret_key = os.getenv('MINIO_ROOT_PASSWORD'),
                secure = False)
        else:
            self.client = client

    def post(self, base64img, file_name, bucket_name = BUCKET_NAME):

        if not self.client.bucket_exists(bucket_name):
            raise RuntimeError('Bucket does not exist.')

        img_bytes = base64.b64decode(base64img.encode('utf-8'))
        img = io.BytesIO(img_bytes)

        res = self.client.put_object(bucket_name, file_name, data = img, length = img.getbuffer().nbytes)
        return res

    def get(self, file_name, bucket_name = BUCKET_NAME):
        if not self.client.bucket_exists(bucket_name):
            raise RuntimeError('Bucket does not exist.')

        try:
            response = self.client.get_object(bucket_name, file_name)
        
        finally:
            response.close()
            response.release_conn()

        return response

    def get_url(self, file_name, bucket_name = BUCKET_NAME):
        url = self.client.get_presigned_url('GET',
        bucket_name, 
        file_name,
        expires = timedelta(hours = 2))

        return url

    def delete_photo(self, file_name, bucket_name = BUCKET_NAME):
        try:
            self.client.remove_object(bucket_name = bucket_name, object_name = file_name)
        except DeleteError:
            print('Nothing to delete..')
