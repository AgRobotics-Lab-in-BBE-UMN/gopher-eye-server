from flask import current_app as app
from flask import request, jsonify, send_file, abort

from app.auth import login_required
# from application import Application

from .models import GroupType, Membership, User, UserGroup
from app import db

@app.route("/", methods=["GET"])
def index():
    return "Alive"

@app.route("/users", methods=["GET"])
@login_required()
def get_users():
    result = [user.serialize() for user in User.query.all()]
    return jsonify(jsonlist=result)

@app.route("/register", methods=["POST"])
@login_required(email=True, uid=True)
def register(email=None, uid=None):
    if User.query.filter_by(id=uid).first():
        return jsonify({"message": "User already exists"}), 409
    
    user = User(email=email, id=uid)
    db.session.add(user)

    group = UserGroup(name=uid, group_type_id=1, description="User Group") # 1 is the default (user) group type
    db.session.add(group)

    group_id = UserGroup.query.filter_by(name=uid).first().id
    membership = Membership(user_id=uid, group_id=group_id)
    db.session.add(membership)

    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201

@app.route("/group-types", methods=["GET"])
@login_required()
def get_group_types():
    return jsonify(jsonlist=[group_type.serialize() for group_type in GroupType.query.all()])

@app.route("/groups", methods=["GET"])
@login_required()
def get_groups():
    return jsonify(jsonlist=[group.serialize() for group in UserGroup.query.all()])

@app.route("/membership", methods=["GET"])
@login_required()
def get_members():
    return jsonify(jsonlist=[member.serialize() for member in Membership.query.all()])

# @app.route("/dl/segmentation", methods=["PUT"])
# def segment_plant():
#     if request.mimetype != "multipart/form-data":
#         print(f"{request.content_type} is not 'multipart/form-data'")
#         abort(400)
#     elif "image" not in request.files:
#         abort(400)
#     else:
#         return jsonify(
#             {
#                 "plant_id": application_layer.segment_plant(
#                     request.files["image"].read()
#                 )
#             }
#         )

# @app.route("/perf/segmentation", methods=["PUT"])
# def perf_test_segementation():
#     if request.mimetype != "multipart/form-data":
#         print(f"{request.content_type} is not 'multipart/form-data'")
#         abort(400)
#     elif "image" not in request.files:
#         abort(400)
#     else:
#         plant_id = application_layer.segment_plant(request.files["image"].read())
#         (image_data, mimetype) = application_layer.get_image(
#             plant_id, "segmentation"
#         )
#         return send_file(image_data, mimetype=mimetype)

# @app.route("/plant/status", methods=["GET"])
# def get_plant_status():
#     plant_id = request.args.get("plant_id")
#     return jsonify({"status": application_layer.plant_status(plant_id)})

# @app.route("/plant/data", methods=["GET"])
# def get_plant_data():
#     plant_id = request.args.get("plant_id")
#     return jsonify(application_layer.plant_data(plant_id))

# @app.route("/plant/image", methods=["GET"])
# def get_plant_item():
#     plant_id = request.args.get("plant_id")
#     image_name = request.args.get("image_name")
#     (image_data, mimetype) = application_layer.get_image(plant_id, image_name)
#     if image_data:
#         return send_file(image_data, mimetype=mimetype)
#     else:
#         abort(400)

# @app.route("/plot/ids", methods=["GET"])
# def get_plant_ids():
#     return jsonify({"plant_ids": application_layer.get_plant_ids()})

# @app.route("/register", methods=["POST"])
# def register():
#     if request.args.get("status") == "200":
#         return (
#             jsonify(
#                 {
#                     "status": 200,
#                     "message": "OTP sent successfully to your email please check your email!",
#                 }
#             ),
#             200,
#         )
#     elif request.args.get("status") == "201":
#         return (
#             jsonify(
#                 {
#                     "status": 201,
#                     "message": "OTP sent successfully to your email please check your email!",
#                 }
#             ),
#             201,
#         )
#     elif request.args.get("status") == "401":
#         return jsonify({"status": 401, "message": "Something went wrong"}), 401
#     else:
#         return (
#             jsonify(
#                 {
#                     "status": 200,
#                     "message": "OTP sent successfully to your email please check your email!",
#                 }
#             ),
#             200,
#         )

# @app.route("/otpVerification", methods=["POST"])
# def verify_otp():
#     if request.args.get("status") == "200":
#         return (
#             jsonify(
#                 {
#                     "status": 200,
#                     "message": "OTP verified successfully",
#                     "token": "test_token",
#                 }
#             ),
#             200,
#         )
#     elif request.args.get("status") == "201":
#         return (
#             jsonify(
#                 {
#                     "status": 201,
#                     "message": "OTP verified successfully",
#                     "token": "test_token",
#                 }
#             ),
#             201,
#         )
#     elif request.args.get("status") == "401":
#         return jsonify({"status": 401, "message": "OTP is not valid"}), 401
#     else:
#         return (
#             jsonify(
#                 {
#                     "status": 200,
#                     "message": "OTP verified successfully",
#                     "token": "test_token",
#                 }
#             ),
#             200,
#         )

# @app.route("/signin", methods=["POST"])
# def signin():
#     if request.args.get("status") == "200":
#         return (
#             jsonify(
#                 {
#                     "status": 200,
#                     "message": "login successfully",
#                     "token": "test_token",
#                 }
#             ),
#             200,
#         )
#     elif request.args.get("status") == "201":
#         return (
#             jsonify(
#                 {
#                     "status": 201,
#                     "message": "login successfully",
#                     "token": "test_token",
#                 }
#             ),
#             201,
#         )
#     elif request.args.get("status") == "401":
#         return (
#             jsonify(
#                 {
#                     "status": 401,
#                     "message": "email or password is wrong/something went wrong",
#                 }
#             ),
#             401,
#         )
#     else:
#         return (
#             jsonify(
#                 {
#                     "status": 200,
#                     "message": "login successfully",
#                     "token": "test_token",
#                 }
#             ),
#             200,
#         )
