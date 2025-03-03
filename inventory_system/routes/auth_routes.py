from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from ..models import db, User
from datetime import datetime, timedelta

def init_auth_routes(app):
    @app.route('/')
    def home():
        if current_user.is_authenticated:
            return redirect(url_for('pos'))
        return render_template('home.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('pos'))
        
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            
            if user and check_password_hash(user.password, password):
                if user.is_account_locked():
                    flash('Cuenta bloqueada. Contacte al administrador.', 'danger')
                    return render_template('home.html')
                
                if user.is_password_expired():
                    flash('Su contraseña ha expirado. Debe cambiarla.', 'warning')
                    return redirect(url_for('change_password'))
                
                login_user(user)
                user.failed_login_attempts = 0
                db.session.commit()
                return redirect(url_for('pos'))
            else:
                if user:
                    user.failed_login_attempts += 1
                    if user.failed_login_attempts >= 3:
                        user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                    db.session.commit()
                flash('Login fallido. Por favor verifique usuario y contraseña', 'danger')
        
        return render_template('home.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Has cerrado sesión exitosamente.', 'info')
        return redirect(url_for('home'))

    return app
