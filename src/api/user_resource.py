from flask import request, current_app
from flask_restful import Resource, reqparse, abort, marshal_with
from ..models import User
from .schemas import UserSchema
from ..utils import generate_filename
from flask_login import login_required, current_user
from ..database import db
import os

user_schema = UserSchema()
users_schema = UserSchema(many=True)


class UserResource(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        if user:
            return user_schema.dump(user), 200
        else:
            return {"error": "User not found"}, 404

#     @marshal_with(user_schema)
#     def put(self, user_id):
#         user = User.query.get(user_id)
#         if not user:
#             abort(404, message="User not found")

#         parser = reqparse.RequestParser()
#         parser.add_argument("username", type=str)
#         parser.add_argument("email", type=str)
#         parser.add_argument("password", type=str)
#         parser.add_argument("role", type=str)
#         parser.add_argument("gender", type=str)
#         parser.add_argument("dob", type=str)
#         parser.add_argument("mobile_number", type=str)
#         args = parser.parse_args()

#         if args["username"] and User.query.filter_by(username=args["username"]).first():
#             abort(409, message="Username already exists")

#         if args["email"] and User.query.filter_by(email=args["email"]).first():
#             abort(409, message="Email already exists")

#         user.username = args["username"] or user.username
#         user.email = args["email"] or user.email
#         user.password = args["password"] or user.password
#         user.role = args["role"] or user.role
#         user.gender = args["gender"] or user.gender
#         user.dob = args["dob"] or user.dob
#         user.mobile_number = args["mobile_number"] or user.mobile_number

#         db.session.commit()
#         return user

#     def delete(self, user_id):
#         user = User.query.get(user_id)
#         if not user:
#             abort(404, message="User not found")

#         db.session.delete(user)
#         db.session.commit()
#         return "", 204


# class UserListResource(Resource):
#     @marshal_with(users_schema)
#     def get(self):
#         users = User.query.all()
#         return users

#     @marshal_with(user_schema)
#     def post(self):
#         parser = reqparse.RequestParser()
#         parser.add_argument("username", type=str, required=True)
#         parser.add_argument("email", type=str, required=True)
#         parser.add_argument("password", type=str, required=True)
#         parser.add_argument("role", type=str, required=True)
#         parser.add_argument("gender", type=str, required=True)
#         parser.add_argument("dob", type=str)
#         parser.add_argument("mobile_number", type=str, required=True)
#         args = parser.parse_args()

#         if User.query.filter_by(username=args["username"]).first():
#             abort(409, message="Username already exists")

#         if User.query.filter_by(email=args["email"]).first():
#             abort(409, message="Email already exists")

#         user = User(
#             username=args["username"],
#             email=args["email"],
#             password=args["password"],
#             role=args["role"],
#             gender=args["gender"],
#             dob=args["dob"],
#             mobile_number=args["mobile_number"],
#         )
#         db.session.add(user)
#         db.session.commit()

#         return user, 201


# # class CurrentUserResource(Resource):
# #     @login_required
# #     @marshal_with(user_schema)
# #     def get(self):
# #         return current_user

# #     @login_required
# #     @marshal_with(user_schema)
# #     def put(self):
# #         parser = reqparse.RequestParser()
# #         parser.add_argument("username", type=str)
# #         parser.add_argument("email", type=str)
# #         parser.add_argument("password", type=str)
# #         parser.add_argument("gender", type=str)
# #         parser.add_argument("dob", type=str)
# #         parser.add_argument("mobile_number", type=str)
# #         args = parser.parse_args()

# #         if args["username"] and User.query.filter_by(username=args["username"]).first():
# #             abort(409, message="Username already exists")

# #         if args["email"] and User.query.filter_by(email=args["email"]).first():
# #             abort(409, message="Email already exists")

# #         current_user.username = args["username"] or current_user.username
# #         current_user.email = args["email"] or current_user.email
# #         current_user.password = args["password"] or current_user.password
# #         current_user.gender = args["gender"] or current_user.gender
# #         current_user.dob = args["dob"] or current_user.dob
# #         current_user.mobile_number = args["mobile_number"] or current_user.mobile_number

# #         db.session.commit()
# #         return current_user


# # class UserImageUploadResource(Resource):
# #     @login_required
# #     def post(self):
# #         if "image" not in request.files:
# #             abort(400, message="No image file provided")

# #         image = request.files["image"]
# #         if image.filename == "":
# #             abort(400, message="No image file selected")

# #         filename = generate_filename(image.filename)
# #         image_path = os.path.join(current_app.config["IMAGE_FOLDER"], filename)
# #         image.save(image_path)

# #         current_user.image_path = image_path
# #         db.session.commit()

# #         return {"message": "Profile image uploaded successfully"}, 200
