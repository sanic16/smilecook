from passlib.hash import pbkdf2_sha256
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
import uuid
import dotenv
import os
import boto3

dotenv.load_dotenv()

def hash_password(password):
    return pbkdf2_sha256.hash(password)


def check_password(password, hashed):
    return pbkdf2_sha256.verify(password, hashed)

def generate_token(email, salt=None):
    serializer = URLSafeTimedSerializer(current_app.config.get('SECRET_KEY'))
    return serializer.dumps(email, salt=salt)

def verify_token(token, max_age=1800, salt=None):
    serializer = URLSafeTimedSerializer(current_app.config.get('SECRET_KEY'))
    try:
        email = serializer.loads(
            token,
            max_age=max_age,
            salt=salt
        )
    except:
        return False
    return email

def generate_presigned_url(operation, object_key=None, expiration=30, ):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name='us-east-1'
    )
    BUCKET_NAME = 'flask-react-gt-aws-bucket'


    if(operation == 'delete_and_upload'):
        try:
            res = s3_client.delete_object(Bucket=BUCKET_NAME, Key=object_key)
           
        except Exception as e:
           
            return False
        
    new_object_key = f'uploads_avatar/{uuid.uuid4()}.jpeg' 


    try:
        response = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': new_object_key,
                'ContentType': 'image/jpeg'
            },
            HttpMethod='PUT',
            ExpiresIn=expiration
        )
    except Exception as e:
        return False
    
    
    return  new_object_key, response


def get_object_url(bucket_name, object_key):
    return f'https://{bucket_name}.s3.amazonaws.com/{object_key}'

