from flask import request
from flask_restful import Resource
from http import HTTPStatus
from models.recipe import Category
from flask_jwt_extended import get_jwt_identity, jwt_required
from decorators import admin_required

class CategoryListResource(Resource):
    def get(self):
        categories = Category.get_all_categories()
        data = []
        for category in categories:
            data.append({
                'id': category.id,
                'name': category.name
            })

        return {
            'categories': data
        }, HTTPStatus.OK



    @jwt_required()
    @admin_required
    def post(self):
        json_data = request.get_json()
        category = json_data.get('category')
        
        category = Category(name=category)
        category.save()

        return {
            'id': category.id,
            'name': category.name
        }, HTTPStatus.CREATED
         

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