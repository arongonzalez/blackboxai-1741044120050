from flask import jsonify, request
from flask_login import login_required, current_user
from ..models import db, Warehouse
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.role == 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def init_warehouse_routes(app):
    @app.route('/api/config/warehouses', methods=['GET'])
    @login_required
    def get_config_warehouses():
        warehouses = Warehouse.query.filter_by(is_active=True).all()
        return jsonify([{
            'id': w.id,
            'name': w.name,
            'location': w.location,
            'description': w.description
        } for w in warehouses])

    @app.route('/api/config/warehouses', methods=['POST'])
    @login_required
    @admin_required
    def create_config_warehouse():
        data = request.get_json()
        warehouse = Warehouse(
            name=data['name'],
            location=data.get('location', ''),
            description=data.get('description', ''),
            created_by=current_user.id
        )
        db.session.add(warehouse)
        db.session.commit()
        return jsonify({'success': True, 'id': warehouse.id})

    @app.route('/api/config/warehouses/<int:warehouse_id>', methods=['DELETE'])
    @login_required
    @admin_required
    def delete_config_warehouse(warehouse_id):
        warehouse = Warehouse.query.get_or_404(warehouse_id)
        warehouse.is_active = False
        db.session.commit()
        return jsonify({'success': True})

    return app
