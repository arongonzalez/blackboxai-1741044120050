from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from ..models import db, Group, Subgroup
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.role == 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def init_config_routes(app):
    @app.route('/configuration')
    @login_required
    def configuration():
        return render_template('configuration.html')

    @app.route('/api/config/groups', methods=['GET'])
    @login_required
    def get_config_groups():
        groups = Group.query.filter_by(is_active=True).all()
        return jsonify([{
            'id': g.id,
            'name': g.name,
            'description': g.description
        } for g in groups])

    @app.route('/api/groups', methods=['POST'])
    @login_required
    @admin_required
    def create_group():
        data = request.get_json()
        group = Group(
            name=data['name'],
            description=data.get('description', ''),
            created_by=current_user.id
        )
        db.session.add(group)
        db.session.commit()
        return jsonify({'success': True, 'id': group.id})

    @app.route('/api/groups/<int:group_id>', methods=['DELETE'])
    @login_required
    @admin_required
    def delete_group(group_id):
        group = Group.query.get_or_404(group_id)
        group.is_active = False
        db.session.commit()
        return jsonify({'success': True})

    @app.route('/api/subgroups', methods=['GET'])
    @login_required
    def get_subgroups():
        subgroups = Subgroup.query.filter_by(is_active=True).all()
        return jsonify([{
            'id': s.id,
            'name': s.name,
            'description': s.description,
            'group_id': s.group_id,
            'group_name': s.group.name
        } for s in subgroups])

    @app.route('/api/subgroups', methods=['POST'])
    @login_required
    @admin_required
    def create_subgroup():
        data = request.get_json()
        subgroup = Subgroup(
            name=data['name'],
            description=data.get('description', ''),
            group_id=data['group_id'],
            created_by=current_user.id
        )
        db.session.add(subgroup)
        db.session.commit()
        return jsonify({'success': True, 'id': subgroup.id})

    @app.route('/api/subgroups/<int:subgroup_id>', methods=['DELETE'])
    @login_required
    @admin_required
    def delete_subgroup(subgroup_id):
        subgroup = Subgroup.query.get_or_404(subgroup_id)
        subgroup.is_active = False
        db.session.commit()
        return jsonify({'success': True})
