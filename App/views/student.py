from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required, current_user as jwt_current_user

from App.controllers.student import request_hours, get_student_logs, get_student_accolades
student_views = Blueprint('student_views', __name__, template_folder='../templates')

@student_views.route('/student/request_hours', methods=['POST'])
@jwt_required()
def request_student_hours():
    current_user = get_jwt_identity()
    if current_user['role'] != 'student':
        return jsonify(message="Only students can request hours"), 403
    
    data = request.form
    log = request_hours(current_user['id'], data['hours'])

    if not log:
        return jsonify(message="Failed to request hours"), 400
    return jsonify(message=f"Requested {data['hours']} hours successfully"), 201


@student_views.route('/student/logs', methods=['GET'])
@jwt_required()
def student_logs():
    current_user = get_jwt_identity()
    if current_user['role'] != 'student':
        return jsonify(message="Only students can view their logs"), 403
    
    logs = get_student_logs(current_user['id'])
    return jsonify([{
        'id': log.id,
        'hours': log.hours,
        'status': log.status,
        'confirmed_by' :log.staff.username,
        'created_at' : log.format_created_time(),
        'reviewed_at': log.format_reviwed_time()

    } for log in logs]), 200


@student_views.route('/student/accolades', methods=['GET'])
@jwt_required()
def student_accolades():
    current_user = get_jwt_identity()

    if current_user['role'] != 'student':
        return jsonify(message="Only students can view their accolades"), 403
    
    accolades = get_student_accolades(current_user['id'])

   
    return jsonify([{
        "milestone": accolade.milestone,
        "name": accolade.name,
        "awarted_at": accolade.format_awarded_time()
    } for accolade in accolades]), 200

