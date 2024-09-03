# Idea:
# 1. Create a presigned URL for the S3 bucket
# 2. Get the image from the URL
# 3. Return the image to the client

import os
import logging
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

s3_signature = {
    'v4': 's3v4',
    'v2': 's3'
}


def get_thumbnail_url(bucket_key, expiration=604800, signature_version=s3_signature['v4']):
    s3_client = boto3.client('s3',
                             aws_access_key_id=os.getenv('AWS_S3_CLIENT_ACCESS_KEY'),
                             aws_secret_access_key=os.getenv("AWS_S3_CLIENT_SECRET_KEY"),
                             config=Config(signature_version=signature_version),
                             region_name=os.getenv('AWS_REGION')
                             )
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': os.getenv('AWS_THUMBNAILS_BUCKET_NAME'),
                                                            'Key': bucket_key},
                                                    ExpiresIn=expiration
                                                    )
    except ClientError as e:
        logging.error(e)
        return None
        # The response contains the presigned URL
    return response
