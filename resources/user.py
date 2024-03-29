from flask import request, url_for, redirect
from flask_restful import Resource
from http import HTTPStatus
from utils import generate_token, verify_token, generate_presigned_url, get_object_url
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from webargs import fields, validate
from webargs.flaskparser import use_args

from models.recipe import Recipe
from models.user import User

from schemas.user import UserSchema
from schemas.recipe import RecipeSchema

from emails import send_email






user_schema = UserSchema()
user_public_schema = UserSchema(exclude=('email', 'is_admin'))
user_avatar_schema = UserSchema(only=('avatar_url',))

recipe_list_schema = RecipeSchema(many=True)




class UserListResource(Resource):
    def post(self):
        json_data = request.get_json()
        
        try:
            data = user_schema.load(data=json_data)
        except ValidationError as err:
            return {
                'message': 'Validation error', 
                'errors': err.messages 
            }, HTTPStatus.BAD_REQUEST

        if User.get_by_username(data.get('username')):
            return {'message': 'username already used'}, HTTPStatus.BAD_REQUEST

        if User.get_by_email(data.get('email')):
            return {'message': 'email already used'}, HTTPStatus.BAD_REQUEST


        user = User(**data)
        user.save()

        token = generate_token(email=user.email, salt='activate')
        subject = 'Please confirm your registration'
        link = url_for('useractivateresource', token=token, _external=True)
        text = 'Hi, Thanks for using this API. Please click on the link below to verify your account: {}'.format(link)
        send_email(subject=subject, body=text, recipient=user.email)
        return user_schema.dump(user), HTTPStatus.CREATED

class UserResource(Resource):
    @jwt_required(optional=True)
    def get(self, username):
        user = User.get_by_username(username=username)

        if user is None:
            return {'message': 'user not found'}, HTTPStatus.NOT_FOUND
        
        current_user = get_jwt_identity()

        if current_user == user.id:
            data = user_schema.dump(user)
        
        else:
            data = user_public_schema.dump(user)

        return data, HTTPStatus.OK
    
class MeResource(Resource):
    @jwt_required()
    def get(self):
        user = User.get_by_id(id=get_jwt_identity())
        
        return user_schema.dump(user), HTTPStatus.OK
    
class UserRecipeListResource(Resource):
    @jwt_required(optional=True)
    @use_args(
        {
            'visibility': fields.Str(missing='public', validate=validate.OneOf(['public', 'private', 'all']))
        },
        location='query'
    )
    def get(self, args, username):

        visibility = args['visibility']

        user = User.get_by_username(username=username)
        

        if user is None:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND
        
        current_user = get_jwt_identity()

        if current_user == user.id and visibility in ['all', 'private']:
            pass
        else:
            visibility = 'public'
        
        recipes = Recipe.get_all_by_user(user_id=user.id, visibility=visibility)

        return recipe_list_schema.dump(recipes), HTTPStatus.OK
    
    
class UserActivateResource(Resource):
    def get(self, token):
        email = verify_token(token=token, salt='activate')
        if email is False:
            return {'message': 'Invalid token or token expired'}, HTTPStatus.BAD_REQUEST

        user = User.get_by_email(email=email)

        if not user:
            return {
                'message': 'User not found'
            }, HTTPStatus.NOT_FOUND
        if user.is_active is True:
            return {
                'message': 'The user account is already activated'
            }, HTTPStatus.BAD_REQUEST
        
        user.is_active = True

        user.save()

        # redirect to login page
        return redirect('/')




class UserAvatarUploadResource(Resource):
    @jwt_required()
    def put(self):
        
        user = User.get_by_id(id=get_jwt_identity())

        if user.avatar_image:
            # user.avatar_image format: https://{bucket_name}.s3.amazonaws.com/uploads_avatar/{object_key}
            # return uplodas_avatar/{object_key}
            object_key_index = user.avatar_image.find('uploads_avatar')
            object_key = user.avatar_image[object_key_index:]
            res = generate_presigned_url(operation='delete_and_upload', object_key=object_key)
            if not res:
                return {'message': 'Error occurred while uploading image'}, HTTPStatus.INTERNAL_SERVER_ERROR
            
            object_key, presigned_url = res
            
            image = get_object_url(bucket_name='flask-react-gt-aws-bucket', object_key=object_key)
            user.avatar_image = image 
        else:
            res = generate_presigned_url(operation='upload')
            if not res:
                return {'message': 'Error occurred while uploading image'}, HTTPStatus.INTERNAL_SERVER_ERROR
           
            object_key, presigned_url = res

            user.avatar_image = get_object_url(bucket_name='flask-react-gt-aws-bucket', object_key=object_key) 

        user.save()
        

        return {'presigned_url': presigned_url}, HTTPStatus.OK
       
            




            
    