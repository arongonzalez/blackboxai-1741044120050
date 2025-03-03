from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Staff, Payment
from sqlalchemy import func
from datetime import date
from functools import wraps

def non_cashier_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role == 'cashier':
            flash('No tienes permiso para acceder a esta página.', 'danger')
            return redirect(url_for('pos'))
        return f(*args, **kwargs)
    return decorated_function

def get_today_payments():
    today = date.today()
    payments = Payment.query.filter(func.date(Payment.payment_date) == today).all()
    total_bs = sum(payment.amount_bs for payment in payments)
    total_usd = sum(payment.amount_usd for payment in payments)
    payment_methods = db.session.query(
        Payment.payment_method,
        func.count(Payment.id)
    ).filter(
        func.date(Payment.payment_date) == today
    ).group_by(Payment.payment_method).all()
    return payments, total_bs, total_usd, payment_methods

def init_dashboard_routes(app):
    @app.route('/dashboard')
    @login_required
    @non_cashier_required
    def dashboard():
        today = date.today()
        
        if current_user.has_role('admin'):
            staff_count = Staff.query.filter_by(is_active=True).count()
            payments, total_bs, total_usd, payment_methods = get_today_payments()
            return render_template('dashboard.html',
                                staff_count=staff_count,
                                today_payments=payments,
                                total_sales_bs=total_bs,
                                total_sales_usd=total_usd,
                                payment_methods=payment_methods,
                                today=today)
        return render_template('dashboard.html', today=today)

    return app
