import json
import base64
import boto3
from io import BytesIO

s3 = boto3.client('s3')

def lambda_handler(event, context):
    try:
        # Extract the base64 encoded image from the event body
        base64_image = event['image']
        object_key = event['key']
        
        # Decode the base64 image
        image_data = base64.b64decode(base64_image)
        
        # Specify the bucket name and the key (path) where you want to store the image
        bucket_name = 'prova-reko4'
        
        # Upload the decoded image data to S3
        s3.put_object(Bucket=bucket_name, Key=object_key, Body=image_data)
        
        # Create a response
        return {
            'statusCode': 200,
            'body': json.dumps('Image uploaded successfully to S3')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing image: {str(e)}')
        }
