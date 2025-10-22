from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user

from.index import index_views

from App.controllers import (
    create_user,
    get_all_users,
    get_all_users_json,
    get_leaderboard,
    jwt_required
)

user_views = Blueprint('user_views', __name__, template_folder='../templates')


@user_views.route('/leaderboard', methods=['GET'])
def leaderboard_page():
    leaderboard = get_leaderboard()
    return jsonify(leaderboard), 200



@user_views.route('/users', methods=['GET'])
def get_user_page():
    users = get_all_users()
    return render_template('users.html', users=users)

@user_views.route('/users', methods=['POST'])
def create_user_action():
    data = request.form
    flash(f"User {data['username']} created!")
    create_user(data['username'], data['password'], data['role'])
    return redirect(url_for('user_views.get_user_page'))

@user_views.route('/api/users', methods=['GET'])
def get_users_action():
    users = get_all_users_json()
    return jsonify(users)

@user_views.route('/api/users', methods=['POST'])
def create_user_endpoint():
    data = request.json
    user = create_user(data['username'], data['password'], data['role'])
    return jsonify({'message': f"user {user.username} created with id {user.id} and role {user.role}"})

@user_views.route('/static/users', methods=['GET'])
def static_user_page():
  return send_from_directory('static', 'static-user.html')

@user_views.route('/signup', methods = ['POST'])
def signup():
    data = request.json
    
    if not data or not 'username' in data or not 'password' in data or not 'role' in data:
        return jsonify({'message': 'Missing data required'}), 400
    
    user = create_user(data['username'], data['password'], data['role'])

    if not user:
        return jsonify({'message': 'User already exists'}), 409 
    
    return jsonify({'message': f'User {user.username} created successfully'}), 201