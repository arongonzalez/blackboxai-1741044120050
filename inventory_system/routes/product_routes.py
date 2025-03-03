from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from ..models import db, Product, Warehouse, Group, Subgroup
from functools import wraps

def non_cashier_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role == 'cashier':
            flash('No tienes permiso para acceder a esta página.', 'danger')
            return redirect(url_for('pos'))
        return f(*args, **kwargs)
    return decorated_function

def init_product_routes(app):
    @app.route('/products')
    @login_required
    @non_cashier_required
    def products():
        products = Product.query.filter_by(is_active=True).all()
        warehouses = Warehouse.query.filter_by(is_active=True).all()
        groups = Group.query.filter_by(is_active=True).all()
        subgroups = Subgroup.query.filter_by(is_active=True).all()
        return render_template('products.html', products=products, warehouses=warehouses, groups=groups, subgroups=subgroups)

    @app.route('/add_product', methods=['POST'])
    @login_required
    @non_cashier_required
    def add_product():
        try:
            product = Product(
                name=request.form['name'],
                description=request.form['description'],
                sku=request.form['sku'] if request.form['sku'] else None,
                barcode=request.form['barcode'] if request.form['barcode'] else None,
                unit=request.form['unit'],
                min_stock=float(request.form['min_stock']),
                max_stock=float(request.form['max_stock']),
                reorder_point=float(request.form['reorder_point']),
                is_perishable=bool(request.form.get('is_perishable')),
                warehouse_id=int(request.form['warehouse']) if request.form['warehouse'] else None,
                group_id=int(request.form['group']) if request.form['group'] else None,
                subgroup_id=int(request.form['subgroup']) if request.form['subgroup'] else None,
                created_by=current_user.id
            )
            db.session.add(product)
            db.session.commit()
            flash('Producto agregado exitosamente.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar producto: {str(e)}', 'danger')
        return redirect(url_for('products'))

    @app.route('/api/products/<int:product_id>/toggle-active', methods=['POST'])
    @login_required
    @non_cashier_required
    def toggle_product_active(product_id):
        try:
            product = Product.query.get_or_404(product_id)
            product.is_active = not product.is_active
            db.session.commit()
            return jsonify({'message': 'Product status updated successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/warehouses', methods=['GET'])
    @login_required
    @non_cashier_required
    def get_warehouses():
        warehouses = Warehouse.query.filter_by(is_active=True).all()
        return jsonify([{'id': w.id, 'name': w.name} for w in warehouses])

    @app.route('/api/groups', methods=['GET'])
    @login_required
    @non_cashier_required
    def get_groups():
        groups = Group.query.filter_by(is_active=True).all()
        return jsonify([{'id': g.id, 'name': g.name} for g in groups])

    @app.route('/api/subgroups', methods=['GET'])
    @login_required
    @non_cashier_required
    def get_subgroups():
        subgroups = Subgroup.query.filter_by(is_active=True).all()
        return jsonify([{'id': s.id, 'name': s.name, 'group_id': s.group_id} for s in subgroups])

    return app
