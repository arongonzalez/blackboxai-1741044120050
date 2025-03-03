from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from ..models import db, User, Staff, Customer, Supplier, PasswordPolicy
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.has_role('admin'):
            flash('No tienes permiso para acceder a esta página.', 'danger')
            return redirect(url_for('pos'))
        return f(*args, **kwargs)
    return decorated_function

def init_staff_routes(app):
    @app.route('/staff', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def staff():
        if request.method == 'POST':
            try:
                # Check if username already exists
                existing_user = User.query.filter_by(username=request.form['username']).first()
                if existing_user:
                    flash('El nombre de usuario ya existe.', 'danger')
                    return redirect(url_for('staff'))

                # Create new user
                user = User(
                    username=request.form['username'],
                    password=generate_password_hash(request.form['password']),
                    email=request.form['email'],
                    role=request.form['staff_type'],
                    created_by=current_user.id
                )
                db.session.add(user)
                db.session.flush()

                # Create staff profile
                staff = Staff(
                    user_id=user.id,
                    first_name=request.form['first_name'],
                    last_name=request.form['last_name'],
                    staff_type=request.form['staff_type'],
                    phone=request.form['phone'],
                    email=request.form['email'],
                    is_active=True
                )
                db.session.add(staff)
                db.session.commit()
                flash('Personal agregado exitosamente.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error al agregar personal: {str(e)}', 'danger')
            return redirect(url_for('staff'))

        staff_members = Staff.query.all()
        policy = PasswordPolicy.query.first() or PasswordPolicy()
        if not policy.id:
            db.session.add(policy)
            db.session.commit()

        return render_template('staff.html', staff_members=staff_members, policy=policy)

    @app.route('/add_customer', methods=['POST'])
    @login_required
    @admin_required
    def add_customer():
        try:
            customer = Customer(
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                document_type=request.form['document_type'],
                document_number=request.form['document_number'],
                address=request.form['address'],
                phone=request.form['phone'],
                email=request.form['email'],
                notes=request.form['notes'],
                created_by=current_user.id
            )
            db.session.add(customer)
            db.session.commit()
            flash('Cliente agregado exitosamente.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar cliente: {str(e)}', 'danger')
        return redirect(url_for('staff'))

    @app.route('/add_supplier', methods=['POST'])
    @login_required
    @admin_required
    def add_supplier():
        try:
            supplier = Supplier(
                company_name=request.form['company_name'],
                contact_name=request.form['contact_name'],
                document_type=request.form['document_type'],
                document_number=request.form['document_number'],
                address=request.form['address'],
                phone=request.form['phone'],
                email=request.form['email'],
                notes=request.form['notes'],
                created_by=current_user.id
            )
            db.session.add(supplier)
            db.session.commit()
            flash('Proveedor agregado exitosamente.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar proveedor: {str(e)}', 'danger')
        return redirect(url_for('staff'))

    return app
