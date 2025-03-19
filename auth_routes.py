from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import logging
import bcrypt
import boto3
import os

auth_routes = Blueprint("auth_routes", __name__)
logger = logging.getLogger(__name__)

# ✅ AWS DynamoDB Users Table
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
users_table = dynamodb.Table("RealtyEnrichUsers")

# ✅ User Registration
@auth_routes.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    # Hash password
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Store user in DynamoDB
    try:
        users_table.put_item(Item={"username": username, "password": hashed_pw})
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        return jsonify({"error": "Registration failed"}), 500

# ✅ User Login & JWT Token Generation
@auth_routes.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    # Retrieve user from DynamoDB
    response = users_table.get_item(Key={"username": username})
    user = response.get("Item")

    if not user or not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=username)
    return jsonify({"access_token": token})

# ✅ Secure Route Example
@auth_routes.route("/secure-data", methods=["GET"])
@jwt_required()
def secure_data():
    current_user = get_jwt_identity()
    return jsonify({"message": f"Hello {current_user}, this is secured data!"})
