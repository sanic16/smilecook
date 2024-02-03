from flask import request
from flask_restful import Resource
from http import HTTPStatus
from models.recipe import Recipe
from flask_jwt_extended import get_jwt_identity, jwt_required
from decorators import admin_required
from schemas.recipe import RecipeSchema, RecipePaginationSchema
from marshmallow import ValidationError
from utils import generate_presigned_url, get_object_url
from webargs.flaskparser import use_args
from webargs import fields, validate 

recipe_schema = RecipeSchema()

recipe_list_schema = RecipeSchema(many=True)

recipe_pagination_schema = RecipePaginationSchema()

class RecipeListResource(Resource):
    # def get(self):
    #     recipes = Recipe.get_all_published()
    #     return recipe_list_schema.dump(recipes), HTTPStatus.OK    
    @use_args({
        'page': fields.Integer(missing=1),
        'per_page': fields.Integer(missing=5),
    },
    location='query'
    )
    def get(self, args):
        page = args.get('page')
        per_page = args.get('per_page')

        paginated_recipes = Recipe.get_all_published(page=page, per_page=per_page)
      
        return recipe_pagination_schema.dump(paginated_recipes), HTTPStatus.OK


    @jwt_required()
    # @admin_required
    def post(self):
        json_data = request.get_json()
        current_user = get_jwt_identity()
        try:
            data = recipe_schema.load(data=json_data)
        except ValidationError as err:
            return {
                'message': 'Validation Errors',
                'errors': err.messages
            }, HTTPStatus.BAD_REQUEST
        
        recipe = Recipe(**data)
        recipe.user_id = current_user
        recipe.save()

        return recipe_schema.dump(recipe), HTTPStatus.CREATED

class RecipeResource(Resource):
    @jwt_required(optional=True)
    def get(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND
        
        current_user = get_jwt_identity()

        if recipe.is_publish == False and recipe.user_id != current_user:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN
        
        return recipe_schema.dump(recipe), HTTPStatus.OK

    @jwt_required()
    def patch(self, recipe_id):
        json_data = request.get_json()
        try:
            data = recipe_schema.load(data=json_data, partial=('name',))
        except ValidationError as err:
            return {
                'message': 'Validation Errors',
                'errors': err.messages
            }, HTTPStatus.BAD_REQUEST
        
        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND
        
        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN
        
        recipe.name = data.get('name') or recipe.name
        recipe.description = data.get('description') or recipe.description
        recipe.num_of_servings = data.get('num_of_servings') or recipe.num_of_servings
        recipe.cook_time = data.get('cook_time') or recipe.cook_time
        recipe.directions = data.get('directions') or recipe.directions

        recipe.save()

        return recipe_schema.dump(recipe), HTTPStatus.OK

    @jwt_required()
    def delete(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND
        
        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN
        
        recipe.delete()

        return {}, HTTPStatus.NO_CONTENT


class RecipePublishResource(Resource):
    @jwt_required()
    def put(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND
        
        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN
        
        recipe.is_publish = True

        recipe.save()

        return {}, HTTPStatus.NO_CONTENT

    @jwt_required()
    def delete(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND
        
        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN
        
        recipe.is_publish = False

        recipe.save()

        return {}, HTTPStatus.NO_CONTENT

class RecipeCoverUploadResource(Resource):
    @jwt_required()
    def put(self, recipe_id):
        
        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND
        
        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN
        
        if recipe.cover_image:
            # recipe.cover_image format: https://{bucket_name}.s3.amazonaws.com/uploads_cover_image/{object_key}
            # return uploads_cover_image/{object_key} to the client
            object_key_index = recipe.cover_image.find('uploads_cover_image')
            object_key = recipe.cover_image[object_key_index:]
            res = generate_presigned_url(operation='delete_and_upload', object_key=object_key, resource='recipe')

            if not res:
                return {'message': 'Error occurred while uploading image'}, HTTPStatus.INTERNAL_SERVER_ERROR
            
            object_key, presigned_url = res

            image = get_object_url(bucket_name='flask-react-gt-aws-bucket', object_key=object_key)
            recipe.cover_image = image

        else:
            res = generate_presigned_url(operation='upload', resource='recipe')
            if not res:
                return {'message': 'Error occurred while uploading image'}, HTTPStatus.INTERNAL_SERVER_ERROR
            
            object_key, presigned_url = res

            recipe.cover_image = get_object_url(bucket_name='flask-react-gt-aws-bucket', object_key=object_key)

        recipe.save()

        return {'presigned_url': presigned_url}, HTTPStatus.OK
