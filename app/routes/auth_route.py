from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.services.auth_service import AuthService

auth_route = Blueprint('auth', __name__)
auth_service = AuthService()

@auth_route.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        user = auth_service.register_user(
            username=data.get('username'),
            password=data.get('password'),
            email=data.get('email')
        )
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user.user_id
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@auth_route.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        user = auth_service.authenticate_user(
            username=data.get('username'),
            password=data.get('password')
        )
        access_token = create_access_token(identity=user.username)
        return jsonify({
            'access_token': access_token,
            'user_id': user.user_id
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 401

@auth_route.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user = get_jwt_identity()
    user = auth_service.get_user_by_username(current_user)
    return jsonify({
        'username': user.username,
        'email': user.email
    }), 200