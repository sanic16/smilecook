from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_reuploads import IMAGES, UploadSet
from flask_cors import CORS

db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
image_set = UploadSet('images', IMAGES)
cors = CORS()
