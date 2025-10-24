from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required, current_user as jwt_current_user
from  App.models import Student
from App.controllers.student import request_hours, get_student_logs, get_student_accolades, get_student
student_views = Blueprint('student_views', __name__, template_folder='../templates')

@student_views.route('/student/request_hours', methods=['POST'])
@jwt_required()
def request_student_hours():
    student_id = get_jwt_identity()
    student = get_student(student_id)

    if not student or student.role != 'student':
        return jsonify(message="Only students can request hours"), 403
    
    data = request.json
    log = request_hours(student.id, data['hours'])

    if not log:
        return jsonify(message="Failed to request hours"), 400
    return jsonify(message=f"Student {student.id}requested {data['hours']} hours successfully"), 201


@student_views.route('/student/logs', methods=['GET'])
@jwt_required()
def student_logs():
    student_id = get_jwt_identity()
    student = get_student(student_id)

    if not student or student.role != 'student':
        return jsonify(message="Only students can view their logs"), 403
    
    logs = get_student_logs(student.id)

    if not logs:
        return jsonify(message="No logs found"), 404
    
    for log in logs:
        if log.staff:
            staff_name = log.staff.username
        else:
            staff_name = "pending"

    return jsonify([{
        'id': log.id,
        'hours': log.hours,
        'status': log.status,
        'confirmed_by' :staff_name,
        'created_at' : log.format_created_time(),
        'reviewed_at': log.format_reviewed_time()

    } for log in logs]), 200


@student_views.route('/student/accolades', methods=['GET'])
@jwt_required()
def student_accolades():
    student_id = get_jwt_identity()
    student = get_student(student_id)

    if not student or student.role != 'student':
        return jsonify(message="Only students can view their accolades"), 403
    
    accolades = get_student_accolades(student.id)

   
    return jsonify([{
        "milestone": accolade.milestone,
        "name": accolade.milestone_name(),
        "awarded_at": accolade.format_awarded_time()
    } for accolade in accolades]), 200

