from flask import Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies


from App.views.index import index_views

from App.controllers import (
    login,
    create_user
)

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')




'''
Page/Action Routes
'''    

@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id} - {current_user.username}")
    

@auth_views.route('/login', methods=['POST'])
def login_action():
    data = request.form
    token = login(data['username'], data['password'])
    response = redirect(request.referrer)
    if not token:
        flash('Bad username or password given'), 401
    else:
        flash('Login Successful')
        set_access_cookies(response, token) 
    return response

@auth_views.route('/logout', methods=['GET'])
def logout_action():
    response = redirect(request.referrer) 
    flash("Logged Out!")
    unset_jwt_cookies(response)
    return response

'''
API Routes
'''

@auth_views.route('/api/signup', methods=['POST'])
def user_signup_api():
    data = request.json

    if not data or not 'username' in data or not 'password' in data or not 'role' in data:
        return jsonify({'message': 'Missing data required!'}), 400
    
    user = create_user(data['username'], data['password'], data['role'])

    if not user:
        return jsonify({'message': 'User already exists!'}), 401
   
   
    token = login(data['username'], data['password'])

    response = jsonify({'message': f'User {user.username} created successfully!', 'access_token': token, 'id':user.id})
    set_access_cookies (response, token)
    return response, 201

@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
    data = request.json
    token = login(data['username'], data['password'])

    if not token:
        return jsonify({'message':'Bad username or password given!'}), 401

    response = jsonify({'message': 'Login successful!', 'access_token': token})
    set_access_cookies(response, token)
    return response, 200

@auth_views.route('/api/logout', methods=['POST'])
def logout_api():
    response = jsonify({'message':"Logged out!"})
    unset_jwt_cookies(response)
    return response, 200

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user():
    return jsonify({'message': f"username: {current_user.username}, id : {current_user.id}"})

