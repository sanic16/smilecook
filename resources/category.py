from flask import request
from flask_restful import Resource
from http import HTTPStatus
from models.recipe import Category
from flask_jwt_extended import get_jwt_identity, jwt_required
from decorators import admin_required
from schemas.category import CategorySchema
from marshmallow import ValidationError

category_schema = CategorySchema()
category_list_schema = CategorySchema(many=True)

class CategoryListResource(Resource):
    def get(self):
        categories = Category.get_all_categories()
        
        return category_list_schema.dump(categories), HTTPStatus.OK



    @jwt_required()
    @admin_required
    def post(self):
        json_data = request.get_json()
        
        try:
            data = category_schema.load(data=json_data)
        except ValidationError as err:
            return {
                'message': 'Validation errors',
                'errors': err.messages
            }, HTTPStatus.BAD_REQUEST

        if Category.get_by_name(data.get('name')):
            return {'message': 'Category already exists'}, HTTPStatus.BAD_REQUEST

        category = Category(**data)
        category.save()

        return category_schema.dump(Category), HTTPStatus.CREATED
         

class CategoryResource(Resource):
    def get(self, category_id):
        category = Category.get_by_id(category_id=category_id)

        if category is None:
            return {'message': 'Category not found'}, HTTPStatus.NOT_FOUND
        
        return {
            'id': category.id,
            'name': category.name
        }, HTTPStatus.OK
    
    @jwt_required()
    @admin_required
    def delete(self, category_id):
        category = Category.get_by_id(category_id=category_id)

        if category is None:
            return {'message': 'Category not found'}, HTTPStatus.NOT_FOUND

        category.delete()

        return {}, HTTPStatus.NO_CONTENT
    
    @jwt_required()
    @admin_required
    def put(self, category_id):
        json_data = request.get_json()
        

        category = Category.get_by_id(category_id=category_id)

        if category is None:
            return {'message': 'Category not found'}, HTTPStatus.NOT_FOUND
        
        category.name = json_data.get('name')
        category.save()

        return {
            'id': category.id,
            'name': category.name
        }, HTTPStatus.OK