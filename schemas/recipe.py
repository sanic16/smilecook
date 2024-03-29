from marshmallow import Schema, fields, post_dump, validate, validates, ValidationError
from schemas.user import UserSchema
from schemas.pagination import PaginationSchema

def validate_num_of_servings(n):
    if n < 1:
        raise ValidationError('Number of servings must be greater than 0.')
    
    if n > 50:
        raise ValidationError('Number of servings must not be greater than 50.')

class RecipeSchema(Schema):
    class Meta:
        ordered = True

    id = fields.Integer(dumm_only=True)
    name = fields.String(required=True, validate=[validate.Length(max=100)])
    description = fields.String(validate=[validate.Length(max=200)])
    num_of_servings = fields.Integer(validate=validate_num_of_servings)
    cook_time = fields.Integer()
    directions = fields.String(validate=[validate.Length(max=1000)])
    is_publish = fields.Boolean(dump_only=True)
    author = fields.Nested(UserSchema, attribute='user', dump_only=True, 
                        #    only=['id', 'username']
                           exclude=('email', 'is_admin', )
                           )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    cover_image = fields.Method(serialize='dump_recipe_image')

    @validates('cook_time')
    def validate_cook_time(self, value):
        if value < 1:
            raise ValidationError('Cook time must be greater than 0.')
        if value > 300:
            raise ValidationError('Cook time must not be greater than 300.')

    # @post_dump(pass_many=True)
    # def wrap(self, data, many, **kwargs):
    #     if many:
    #         return {'data': data}
    #     return data

    
    def dump_recipe_image(self, recipe):
        if recipe.cover_image:
            return recipe.cover_image
        else:
            return 'https://flask-react-gt-aws-bucket.s3.amazonaws.com/uploads_recipe/assets/no-image.jpg'
        
class RecipePaginationSchema(PaginationSchema):
    data = fields.Nested(RecipeSchema, attribute='items', many=True)
    