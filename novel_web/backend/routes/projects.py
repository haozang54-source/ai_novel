from flask import Blueprint, request, jsonify
from ..services import project_service

bp = Blueprint('projects', __name__)

@bp.route('/projects', methods=['GET'])
def get_projects():
    projects = project_service.get_all()
    return jsonify([p.to_dict() for p in projects])

@bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = project_service.get(project_id)
    return jsonify(project.to_dict())

@bp.route('/projects', methods=['POST'])
def create_project():
    data = request.json
    project = project_service.create(data)
    return jsonify(project.to_dict()), 201

@bp.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    data = request.json
    project = project_service.update(project_id, data)
    return jsonify(project.to_dict())

@bp.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    project_service.delete(project_id)
    return '', 204
