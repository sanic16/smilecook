from passlib.hash import pbkdf2_sha256
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
import uuid
from flask_reuploads import extension
from extensions import image_set
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

# def save_image(image, folder):
#     filename = '{}.{}'.format(uuid.uuid4(), extension(image.filename))
#     image_set.save(image, folder=folder, name=filename)
#     return filename

def generate_presigned_url(operation, object_key=None, expiration=30, ):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name='us-east-1'
    )
    BUCKET_NAME = 'flask-react-gt-aws-bucket'

    print('--- step 1 ---')

    if(operation == 'delete_and_upload'):
        try:
            res = s3_client.delete_object(Bucket=BUCKET_NAME, Key=object_key)
            print(res)
            print('object deleted')
        except Exception as e:
            print(e)
            return False
        
    new_object_key = f'uploads_avatar/{uuid.uuid4()}.jpeg' 

    print('--- step 2 ---')

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
    
    print('--- step 3 ---')
    
    return  new_object_key, response


def get_object_url(bucket_name, object_key):
    return f'https://{bucket_name}.s3.amazonaws.com/{object_key}'

# def upload_to_s3(file):
#     BUCKET_NAME = 'flask-react-gt-aws-bucket'
#     AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
#     AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
#     AWS_REGION = 'us-east-1'

#     client = boto3.client(
#         's3',
#         aws_access_key_id = AWS_ACCESS_KEY_ID,
#         aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
#         region_name = AWS_REGION
#     )
#     filename = '{}.{}'.format(uuid.uuid4(), file.filename.split('.')[-1])
#     print(filename)

#     try:
#         file.seek(0)
#         file_binary = file.read()
#         client.put_object(Bucket=BUCKET_NAME, Key=filename, Body=file_binary)
#     except Exception as e:
#         return False
    
#     return filename

# def delete_from_s3(object_key):
#     BUCKET_NAME = 'flask-react-gt-aws-bucket'
#     AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
#     AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
#     AWS_REGION = 'us-east-1'

#     client = boto3.client(
#         's3',
#         aws_access_key_id = AWS_ACCESS_KEY_ID,
#         aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
#         region_name = AWS_REGION
#     )

#     try:
#         client.delete_object(Bucket=BUCKET_NAME, Key=object_key)
#     except Exception as e:
#         return False
    
#     return True
