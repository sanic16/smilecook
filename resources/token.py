from http import HTTPStatus
from flask import request, make_response
from flask_restful import Resource
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, get_jwt_identity, get_jwt)
from utils import check_password
from models.user import User
from datetime import datetime
from datetime import timezone
from models.token import TokenBlocklist
from extensions import db
from schemas.user import UserSchema

user_schema = UserSchema()

black_list = set()

class TokenResource(Resource):
    def post(self):
        json_data = request.get_json()
        email = json_data.get('email')
        password = json_data.get('password')
        user = User.get_by_email(email=email)

        if not user or not check_password(password, user.password):
            return {'message': 'email or password is incorrect'}, HTTPStatus.UNAUTHORIZED
        
        if user.is_active is False:
            return {'message': 'The user account is not activated yet'}, HTTPStatus.FORBIDDEN

        access_token = create_access_token(identity=user.id, fresh=True)

        refresh_token = create_refresh_token(identity=user.id)

        user = user_schema.dump(user)

        response = make_response(user, HTTPStatus.OK)
        response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='None', secure=False)
        response.set_cookie('access_token', access_token, httponly=True, samesite='None', secure=False)
        return response
    
class RefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user, fresh=False)

        
        response = make_response({}, HTTPStatus.OK)
        response.set_cookie('access_token', access_token, httponly=True, samesite='None', secure=False)
        return response
    

class RevokeResource(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        now = datetime.now(timezone.utc)
        db.session.add(TokenBlocklist(jti=jti, created_at=now))
        db.session.commit()

        return {'message': 'Successfully logged out'}, HTTPStatus.OK
    
