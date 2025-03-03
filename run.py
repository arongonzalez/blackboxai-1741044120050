from inventory_system.app import create_app
from inventory_system.models import db, User, Staff
from werkzeug.security import generate_password_hash

app = create_app()

def create_demo_data():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")

        # Create admin user if it doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                email='admin@example.com',
                role='admin'
            )
            db.session.add(admin)
            db.session.flush()  # Get admin.id before committing

            # Create admin staff profile
            staff = Staff(
                user_id=admin.id,
                first_name='Admin',
                last_name='User',
                staff_type='admin',
                phone='1234567890',
                email='admin@example.com',
                is_active=True
            )
            db.session.add(staff)
            db.session.commit()
            print("Admin user created successfully!")

            # Create demo staff
            demo_staff = User(
                username='cashier',
                password=generate_password_hash('cashier123'),
                email='cashier@example.com',
                role='cashier',
                created_by=admin.id
            )
            db.session.add(demo_staff)
            db.session.flush()

            staff = Staff(
                user_id=demo_staff.id,
                first_name='Demo',
                last_name='Cashier',
                staff_type='cashier',
                phone='0987654321',
                email='cashier@example.com',
                is_active=True
            )
            db.session.add(staff)
            db.session.commit()
            print("Demo staff created successfully!")

if __name__ == '__main__':
    create_demo_data()
    app.run(debug=True, host='0.0.0.0')
