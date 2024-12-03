from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import request
from flask_restx import Api, Resource, fields
import jwt
from .models import db, User, JWTTokenBlocklist, IrisData
from .config import BaseConfig

rest_api = Api(version="1.0", title="Dashboard API")


"""
    Flask-Restx models for api request and response data
"""

signup_model = rest_api.model('SignUpModel', {"email": fields.String(required=True, min_length=4, max_length=64),
                                              "password": fields.String(required=True, min_length=4, max_length=16),
                                              "variety": fields.String(required=True, min_length=2, max_length=32)
                                              })

login_model = rest_api.model('LoginModel', {"email": fields.String(required=True, min_length=4, max_length=64),
                                            "password": fields.String(required=True, min_length=4, max_length=16)
                                            })


"""
   Helper function for JWT token required
"""

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if "authorization" in request.headers:
            token = request.headers["authorization"]
        if not token:
            return {"success": False, "msg": "Valid JWT token is missing"}, 401
        try:
            data = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=["HS256"])
            current_user = User.get_by_email(data["email"])
            if not current_user:
                return {"success": False,
                        "msg": "The entered user does not exist."}, 401
            token_expired = db.session.query(JWTTokenBlocklist.id).filter_by(jwt_token=token).scalar()
            if token_expired is not None:
                return {"success": False, "msg": "Token revoked."}, 401
            if not current_user.check_jwt_auth_active():
                return {"success": False, "msg": "Token expired."}, 401
        except Exception as e:
            return {"success": False, "msg": "Token is invalid"}, 401
        return f(current_user, *args, **kwargs)
    return decorator


"""
    Flask-Restx routes
"""
@rest_api.route('/api/users/register')
class Register(Resource):
    """
       Creates a new user by taking 'signup_model' input
    """
    @rest_api.expect(signup_model, validate=True)
    def post(self):
        req_data = request.get_json()
        email = req_data.get("email")
        password = req_data.get("password")
        variety = req_data.get("variety")
        user_exists = User.get_by_email(email)
        if user_exists:
            return {"success": False,
                    "msg": "Email already taken"}, 400
        new_user = User(email=email, variety=variety)
        new_user.set_password(password)
        new_user.save()
        return {"success": True,
                "user_id": new_user.id,
                "msg": "The user was successfully registered"}, 200


@rest_api.route('/api/users/login')
class Login(Resource):
    """
       Login user by taking 'login_model' input and return JWT token
    """
    @rest_api.expect(login_model, validate=True)
    def post(self):
        req_data = request.get_json()
        email = req_data.get("email")
        password = req_data.get("password")
        user_exists = User.get_by_email(email)
        if not user_exists:
            return {"success": False,
                    "msg": "This email does not exist."}, 400
        if not user_exists.check_password(password):
            return {"success": False,
                    "msg": "Wrong credentials."}, 400
        # create access token uwing JWT
        token = jwt.encode({'email': email, 'exp': datetime.utcnow() + timedelta(minutes=30)}, BaseConfig.SECRET_KEY)
        user_exists.set_jwt_auth_active(True)
        user_exists.save()
        return {"success": True,
                "token": token,
                "user": user_exists.to_json()}, 200


@rest_api.route('/api/users/logout')
class LogoutUser(Resource):
    """
       Logs out User using 'logout_model' input
    """
    @token_required
    def post(self, current_user):
        jwt_token = request.headers["authorization"]
        jwt_block = JWTTokenBlocklist(jwt_token=jwt_token, created_at=datetime.now(timezone.utc))
        jwt_block.save()
        self.set_jwt_auth_active(False)
        self.save()
        return {"success": True}, 200
    

@rest_api.route('/api/dashboard')
class Dashboard(Resource):
    """
       Gets the graphs data based on the user's variety
    """
    @token_required
    def get(self, current_user):
        token = request.headers["authorization"]
        data = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=["HS256"])
        current_user = User.get_by_email(data["email"])
        iris_data = IrisData.filter_by_variety(current_user.variety)
        items_list = []
        for item in iris_data:
            items_list.append(item.to_dict())
        return {"success": True,
                "iris_data": items_list
                }, 200