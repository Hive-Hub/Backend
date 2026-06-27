import logging
import boto3
from django.conf import settings
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class StorageService:
    """
    Service to interact with Supabase Storage via boto3 S3 interface.
    """

    @staticmethod
    def get_s3_client():
        """
        Initializes boto3 S3 client using the configuration defined in settings.STORAGES['default']['OPTIONS'].
        """
        try:
            s3_options = settings.STORAGES['default']['OPTIONS']
            return boto3.client(
                's3',
                aws_access_key_id=s3_options['access_key'],
                aws_secret_access_key=s3_options['secret_key'],
                endpoint_url=s3_options['endpoint_url'],
                region_name=s3_options['region_name']
            )
        except Exception as e:
            logger.error(f"Failed to create S3 client: {str(e)}")
            return None

    @staticmethod
    def upload_file_to_supabase(file_name, file_bytes, mime_type="application/octet-stream", bucket_name=None):
        """
        Uploads a raw bytes payload to the designated Supabase bucket.
        """
        s3_options = settings.STORAGES['default']['OPTIONS']
        bucket = bucket_name or s3_options['bucket_name']
        s3_client = StorageService.get_s3_client()
        
        if not s3_client:
            # Return a mock successful state in test/development environments lacking keys
            mock_url = f"https://mock-supabase-storage.co/{bucket}/{file_name}"
            return {
                "success": True,
                "file_url": mock_url,
                "bucket_name": bucket,
                "size": len(file_bytes),
                "is_mock": True
            }

        try:
            s3_client.put_object(
                Bucket=bucket,
                Key=file_name,
                Body=file_bytes,
                ContentType=mime_type
            )
            
            # Form public URL path
            endpoint = s3_options['endpoint_url'].rstrip('/')
            file_url = f"{endpoint}/{bucket}/{file_name}"
            
            return {
                "success": True,
                "file_url": file_url,
                "bucket_name": bucket,
                "size": len(file_bytes),
                "is_mock": False
            }
        except ClientError as e:
            logger.error(f"S3 PutObject error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "is_mock": False
            }

    @staticmethod
    def generate_signed_url(file_key, expiration=3600, bucket_name=None):
        """
        Generates a pre-signed URL to view a private storage asset.
        """
        s3_options = settings.STORAGES['default']['OPTIONS']
        bucket = bucket_name or s3_options['bucket_name']
        s3_client = StorageService.get_s3_client()
        
        if not s3_client:
            return f"https://mock-supabase-storage.co/{bucket}/{file_key}?token=mock_signed_token"

        try:
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': file_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"S3 Generate Presigned URL error: {str(e)}")
            return None
