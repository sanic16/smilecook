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
         