from app.minio_client import MinioThumbnailStorage
from .celery import app

from . import settings
from minio import Minio

__all__ = ['app']

BUCKET_NAME = 'thumbnail-images'

minio_cli = Minio(endpoint = settings.MINIO_ENDPOINT,
    access_key = settings.MINIO_ACCESS_KEY,
    secret_key = settings.MINIO_SECRET_KEY,
    secure = settings.MINIO_SECURE)

if not minio_cli.bucket_exists(BUCKET_NAME):
    minio_cli.make_bucket(BUCKET_NAME)

minio_storage = MinioThumbnailStorage(minio_cli)
