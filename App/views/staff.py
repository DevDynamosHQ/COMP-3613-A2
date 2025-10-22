from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required, current_user as jwt_current_user

from App.controllers.staff import get_pending_logs, confirm_hours, deny_hours


staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

@staff_views.route('/staff/pending', methods=['GET'])
@jwt_required()
def pending_logs():
    current_user = get_jwt_identity()
    if current_user['role'] != 'staff':
        return jsonify(message="Only staff can view pending logs"), 403
    
    logs = get_pending_logs()
   
    return jsonify([{
        'id': log.id,
        'student': log.student.username,
        'hours': log.hours,
        'status': log.status,
        'created_at': log.format_created_time()
    } for log in logs]), 200



@staff_views.route('/staff/log_hours', methods=['POST'])
@jwt_required()
def log_hours():
    current_user = get_jwt_identity()
    if current_user['role'] != 'staff':
        return jsonify(message="Only staff can log hours"), 403
    
    data = request.json
    student_id = data.get('student_id')
    hours = data.get('hours')
    
    if not student_id or not hours or hours <= 0:
        return jsonify(message="Invalid student_id or hours"), 400
    
    log = log_hours(current_user['id'], student_id, hours)

    if not log:
        return jsonify(message="Failed to log hours"), 400
    
    return jsonify({
        'message': f"Logged {hours} hours for student {student_id} successfully",
        'log': {
            'id': log.id,
            'student_id': log.student_id,
            'student_name': log.student.username,
            'hours': log.hours,
            'status': log.status,
            "reviewed_at": log.format_reviewed_time(),
            'reviewed_by': current_user['username']
        }
    }), 201

@staff_views.route('/staff/confirm/<int:log_id>', methods=['PUT'])
@jwt_required()
def confirm_log(log_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'staff':
        return jsonify(message="Only staff can confirm logs"), 403
    
    log = confirm_hours(current_user['id'], log_id)

    if not log:
        return jsonify(message="Failed to confirm log"), 400
    
    return jsonify({
        'message': "Log confirmed successfully",
        'log': {
        'id': log.id,
        'student_id': log.student_id,
        'hours': log.hours,
        'status': log.status,
        "reviewed_at": log.format_reviewed_time()
        }
    }), 200



@staff_views.route('/staff/deny/<int:log_id>', methods=['PUT'])
@jwt_required()
def deny_log(log_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'staff':
        return jsonify(message="Only staff can deny logs"), 403

    log = deny_hours(current_user['id'], log_id)

    if not log:
        return jsonify(message="Failed to deny log"), 400

    return jsonify({
        'message': "Log denied successfully",
        'log': {
            'id': log.id,
            'student_id': log.student_id,
            'hours': log.hours,
            'status': log.status,
            "reviewed_at": log.format_reviewed_time()
        }
    }), 200
    

    