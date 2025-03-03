from flask import render_template, jsonify
from flask_login import login_required, current_user
from ..models import db, Product, Group, Subgroup, Payment, InventoryTransaction
from sqlalchemy import func
from datetime import datetime, date

def init_report_routes(app):
    @app.route('/reports')
    @login_required
    def reports():
        return render_template('reports.html')

    @app.route('/reports/inventory')
    @login_required
    def inventory_report():
        products = Product.query.filter_by(is_active=True).all()
        low_stock = [p for p in products if p.stock_level < p.reorder_point]
        return render_template('inventory_report.html', products=products, low_stock=low_stock)

    @app.route('/reports/profit')
    @login_required
    def profit_report():
        # Get profit data by product
        profits = db.session.query(
            Product.name,
            func.sum(InventoryTransaction.total_cost).label('total_cost'),
            func.sum(InventoryTransaction.quantity * Product.selling_price).label('total_revenue')
        ).join(Product).group_by(Product.id).all()
        
        return render_template('profit_report.html', profits=profits)

    @app.route('/reports/groups')
    @login_required
    def groups_report():
        groups = Group.query.filter_by(is_active=True).all()
        subgroups = Subgroup.query.filter_by(is_active=True).all()
        products = Product.query.filter_by(is_active=True).all()
        
        return render_template('groups_report.html', 
                             groups=groups, 
                             subgroups=subgroups, 
                             products=products)

    @app.route('/reports/daily-sales')
    @login_required
    def daily_sales_report():
        today = date.today()
        
        # Get all payments for today
        payments = Payment.query.filter(
            func.date(Payment.payment_date) == today
        ).all()
        
        # Calculate totals
        bs_income = sum(p.amount_bs for p in payments if p.status == 'completed')
        usd_income = sum(p.amount_usd for p in payments if p.status == 'completed')
        bs_change = sum(p.change_bs for p in payments if p.status == 'completed' and p.change_bs)
        usd_change = sum(p.change_usd for p in payments if p.status == 'completed' and p.change_usd)
        
        return render_template('daily_sales_report.html',
                             payments=payments,
                             bs_income=bs_income,
                             usd_income=usd_income,
                             bs_change=bs_change,
                             usd_change=usd_change)

    @app.route('/reports/z')
    @login_required
    def z_report():
        today = date.today()
        
        # Get all payments for today
        payments = Payment.query.filter(
            func.date(Payment.payment_date) == today
        ).all()
        
        return render_template('z_report.html', payments=payments)

    return app
