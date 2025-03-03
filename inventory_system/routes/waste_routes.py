from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps

def non_cashier_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role == 'cashier':
            flash('No tienes permiso para acceder a esta página.', 'danger')
            return redirect(url_for('pos'))
        return f(*args, **kwargs)
    return decorated_function

def init_waste_routes(app):
    @app.route('/waste')
    @login_required
    @non_cashier_required
    def waste():
        # Initialize waste statistics
        waste_records = []
        monthly_waste_value = 0.00
        affected_products = 0
        waste_percentage = 0.00
        
        return render_template('waste.html',
                             waste_records=waste_records,
                             monthly_waste_value=monthly_waste_value,
                             affected_products=affected_products,
                             waste_percentage=waste_percentage)

    @app.route('/contracts')
    @login_required
    @non_cashier_required
    def contracts():
        # Initialize contract statistics
        contracts_data = []
        active_contracts = 0
        total_value = 0.00
        expiring_soon = 0
        
        return render_template('contracts.html',
                             contracts=contracts_data,
                             active_contracts=active_contracts,
                             total_value=total_value,
                             expiring_soon=expiring_soon)

    return app
