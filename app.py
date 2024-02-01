from flask import Flask, send_from_directory
from flask_migrate import Migrate
from flask_restful import Api
from config import Config
from extensions import db, jwt, mail, image_set, cors

from resources.recipe import RecipeListResource, RecipeResource, RecipePublishResource
from resources.user import (UserListResource, UserResource, MeResource, UserRecipeListResource,
                             UserActivateResource, UserAvatarUploadResource) 
from resources.token import TokenResource, RefreshResource, RevokeResource, black_list 
from models.token import TokenBlocklist
from flask_uploads import configure_uploads


def create_app():
    app = Flask(__name__, static_folder='client/assets')
    app.config.from_object(Config)
    register_extensions(app)
    register_resources(app)
    return app


def register_extensions(app):
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt.init_app(app=app)
    mail.init_app(app=app)
    configure_uploads(app, image_set)
    cors.init_app(app)
    
    # patch_request_class(app, 5*1024*1024)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload: dict) -> bool:
        jti = jwt_payload['jti']
        token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
        return token is not None 
        


def register_resources(app):
    api = Api(app)
    api.add_resource(RecipeListResource, '/api/recipes')
    api.add_resource(RecipeResource, '/api/recipes/<int:recipe_id>')
    api.add_resource(RecipePublishResource, '/api/recipes/<int:recipe_id>/publish')

    api.add_resource(UserListResource, '/api/users')
    api.add_resource(UserResource, '/api/users/<string:username>')
    api.add_resource(MeResource, '/api/me')
    api.add_resource(UserRecipeListResource, '/api/users/<string:username>/recipes')
    api.add_resource(UserActivateResource, '/api/users/activate/<string:token>')
    api.add_resource(UserAvatarUploadResource, '/api/users/avatar')

    api.add_resource(TokenResource, '/api/token')
    api.add_resource(RefreshResource, '/api/refresh')
    api.add_resource(RevokeResource, '/api/revoke')

app = create_app()

@app.errorhandler(404)
def not_found(e):
    return serve()
@app.route('/')
def serve():
    return send_from_directory('client', 'index.html')
if __name__ == '__main__':
    app.run(debug=True)
