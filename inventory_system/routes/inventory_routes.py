from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..models import (
    db, Product, Supplier, InventoryTransaction, PurchaseInvoice, 
    PurchaseInvoiceItem, InventoryAdjustment, InventoryAdjustmentItem
)
from sqlalchemy import func
from datetime import datetime
from functools import wraps

def non_cashier_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role == 'cashier':
            flash('No tienes permiso para acceder a esta página.', 'danger')
            return redirect(url_for('pos'))
        return f(*args, **kwargs)
    return decorated_function

def init_inventory_routes(app):
    @app.route('/inventory')
    @login_required
    @non_cashier_required
    def inventory():
        products = Product.query.filter_by(is_active=True).all()
        inventory_data = []
        
        for product in products:
            stock_in = db.session.query(func.sum(InventoryTransaction.quantity)).filter(
                InventoryTransaction.product_id == product.id,
                InventoryTransaction.type.in_(['purchase', 'adjustment_in', 'initial'])
            ).scalar() or 0
            
            stock_out = db.session.query(func.sum(InventoryTransaction.quantity)).filter(
                InventoryTransaction.product_id == product.id,
                InventoryTransaction.type.in_(['sale', 'adjustment_out'])
            ).scalar() or 0
            
            inventory_data.append({
                'product': product,
                'current_stock': stock_in - stock_out
            })
        
        suppliers = Supplier.query.filter_by(is_active=True).all()
        
        return render_template('inventory.html',
                             inventory=inventory_data,
                             suppliers=suppliers,
                             products=products)

    @app.route('/add_inventory_adjustment', methods=['POST'])
    @login_required
    @non_cashier_required
    def add_inventory_adjustment():
        try:
            adjustment_type = request.form['adjustment_type']
            
            if adjustment_type == 'purchase':
                # Create purchase invoice
                invoice = PurchaseInvoice(
                    supplier_id=request.form['supplier_id'],
                    invoice_number=request.form['invoice_number'],
                    control_number=request.form['control_number'],
                    invoice_date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                    due_date=datetime.strptime(request.form['due_date'], '%Y-%m-%d').date() if request.form['due_date'] else None,
                    subtotal=float(request.form['subtotal']),
                    tax_amount=float(request.form['tax_amount']),
                    total_amount=float(request.form['total_amount']),
                    notes=request.form['notes'],
                    created_by=current_user.id
                )
                db.session.add(invoice)
                db.session.flush()

                # Process invoice items
                products = request.form.getlist('products[]')
                quantities = request.form.getlist('quantities[]')
                unit_prices = request.form.getlist('unit_prices[]')
                tax_rates = request.form.getlist('tax_rates[]')
                expiry_dates = request.form.getlist('expiry_dates[]')

                for i in range(len(products)):
                    quantity = float(quantities[i])
                    unit_price = float(unit_prices[i])
                    tax_rate = float(tax_rates[i])
                    
                    subtotal = quantity * unit_price
                    tax_amount = subtotal * (tax_rate / 100)
                    total = subtotal + tax_amount

                    # Create invoice item
                    item = PurchaseInvoiceItem(
                        invoice_id=invoice.id,
                        product_id=int(products[i]),
                        quantity=quantity,
                        unit_price=unit_price,
                        tax_rate=tax_rate,
                        tax_amount=tax_amount,
                        subtotal=subtotal,
                        total=total,
                        expiry_date=datetime.strptime(expiry_dates[i], '%Y-%m-%d').date() if expiry_dates[i] else None
                    )
                    db.session.add(item)

                    # Create inventory transaction
                    transaction = InventoryTransaction(
                        product_id=int(products[i]),
                        type='purchase',
                        reference_id=invoice.id,
                        reference_type='purchase_invoice',
                        quantity=quantity,
                        unit_cost=unit_price,
                        total_cost=total,
                        date=invoice.invoice_date,
                        expiry_date=item.expiry_date,
                        created_by=current_user.id
                    )
                    db.session.add(transaction)

                flash('Factura de compra registrada exitosamente.', 'success')

            else:
                # Create inventory adjustment
                adjustment = InventoryAdjustment(
                    type=adjustment_type,
                    date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                    reason=request.form['reason'],
                    notes=request.form['notes'],
                    created_by=current_user.id
                )
                db.session.add(adjustment)
                db.session.flush()

                # Process adjustment items
                products = request.form.getlist('products[]')
                quantities = request.form.getlist('quantities[]')
                unit_costs = request.form.getlist('unit_costs[]') if adjustment_type == 'initial' else None
                expiry_dates = request.form.getlist('expiry_dates[]')
                lot_numbers = request.form.getlist('lot_numbers[]')

                for i in range(len(products)):
                    quantity = float(quantities[i])
                    unit_cost = float(unit_costs[i]) if unit_costs else None

                    # Create adjustment item
                    item = InventoryAdjustmentItem(
                        adjustment_id=adjustment.id,
                        product_id=int(products[i]),
                        quantity=quantity,
                        unit_cost=unit_cost,
                        expiry_date=datetime.strptime(expiry_dates[i], '%Y-%m-%d').date() if expiry_dates[i] else None,
                        lot_number=lot_numbers[i] if lot_numbers[i] else None
                    )
                    db.session.add(item)

                    # Create inventory transaction
                    transaction = InventoryTransaction(
                        product_id=int(products[i]),
                        type=f'adjustment_{adjustment_type}',
                        reference_id=adjustment.id,
                        reference_type='adjustment',
                        quantity=quantity,
                        unit_cost=unit_cost,
                        total_cost=quantity * unit_cost if unit_cost else None,
                        date=adjustment.date,
                        expiry_date=item.expiry_date,
                        lot_number=item.lot_number,
                        created_by=current_user.id
                    )
                    db.session.add(transaction)

                flash('Ajuste de inventario registrado exitosamente.', 'success')

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar movimiento de inventario: {str(e)}', 'danger')
        
        return redirect(url_for('inventory'))

    return app
