#!/usr/bin/env python
"""Create an admin user for the system"""
from app import create_app, db
from app.models import User, Department

app = create_app('development')

def create_admin():
    """Create an admin user"""
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Admin user already exists!")
            return
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@college.edu',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        
        print("Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print("\nYou can now log in at: http://127.0.0.1:5500/login")

if __name__ == '__main__':
    create_admin()
