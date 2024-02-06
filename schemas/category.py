from marshmallow import Schema, fields

class CategorySchema(Schema):
    class Meta:
        ordered = True

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)

    
     