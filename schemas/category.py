from marshmallow import Schema, fields
from schemas.recipe import RecipeSchema

class CategorySchema(Schema):
    class Meta:
        ordered = True

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    recipes = fields.Nested(
        RecipeSchema, 
        dump_only=True,
        many=True, 
        only=('id', 'name', 'description', 'num_of_servings', 'cook_time', 'cover_image')
    )



     