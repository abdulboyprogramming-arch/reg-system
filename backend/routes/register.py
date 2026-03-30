"""Registration route handlers"""
import json
import hashlib
import re
import secrets
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

class RegisterRoutes:
    def __init__(self, pg_db, mongo_db):
        self.pg_db = pg_db
        self.mongo_db = mongo_db
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def handle_register(self, handler, data):
        """Handle registration POST request"""
        # Validate required fields
        required_fields = ['email', 'username', 'password', 'confirm_password']
        for field in required_fields:
            if field not in data:
                handler.send_json_response({'success': False, 'error': f'Missing field: {field}'}, 400)
                return
        
        # Validate email
        if not self.validate_email(data['email']):
            handler.send_json_response({'success': False, 'error': 'Invalid email format'}, 400)
            return
        
        # Check if email exists
        if self.pg_db.get_user_by_email(data['email']):
            handler.send_json_response({'success': False, 'error': 'Email already registered'}, 400)
            return
        
        # Check if username exists
        if self.pg_db.get_user_by_username(data['username']):
            handler.send_json_response({'success': False, 'error': 'Username already taken'}, 400)
            return
        
        # Validate password
        if len(data['password']) < 6:
            handler.send_json_response({'success': False, 'error': 'Password must be at least 6 characters'}, 400)
            return
        
        if data['password'] != data['confirm_password']:
            handler.send_json_response({'success': False, 'error': 'Passwords do not match'}, 400)
            return
        
        # Hash password
        password_hash = self.hash_password(data['password'])
        
        # Prepare user data
        user_data = {
            'email': data['email'],
            'username': data['username'],
            'password_hash': password_hash,
            'full_name': data.get('full_name', ''),
            'phone': data.get('phone', ''),
            'date_of_birth': data.get('date_of_birth', None),
            'gender': data.get('gender', ''),
            'country': data.get('country', ''),
            'city': data.get('city', ''),
            'postal_code': data.get('postal_code', '')
        }
        
        # Insert into PostgreSQL
        user_id = self.pg_db.insert_user(user_data)
        
        if not user_id:
            handler.send_json_response({'success': False, 'error': 'Failed to create user'}, 500)
            return
        
        # Save additional dynamic data to MongoDB
        dynamic_data = {k: v for k, v in data.items() if k not in required_fields and k not in user_data}
        if dynamic_data:
            self.mongo_db.save_form_submission('registration_extra', dynamic_data, user_id)
        
        # Log registration activity
        self.mongo_db.log_activity(
            user_id=user_id,
            action='register',
            ip_address=handler.client_address[0],
            user_agent=handler.headers.get('User-Agent'),
            details={'registration_data': {k: v for k, v in user_data.items() if k != 'password_hash'}}
        )
        
        # Create session
        session_token = secrets.token_urlsafe(32)
        import datetime
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        self.mongo_db.create_session(user_id, session_token, expires_at)
        
        handler.send_header('Set-Cookie', f'session_token={session_token}; HttpOnly; Path=/; Max-Age=86400')
        handler.send_json_response({
            'success': True,
            'message': 'Registration successful',
            'redirect': '/dashboard'
        })
    
    def handle_check_availability(self, handler, data):
        """Check username/email availability"""
        field = data.get('field')
        value = data.get('value')
        
        if field == 'username':
            user = self.pg_db.get_user_by_username(value)
            available = user is None
        elif field == 'email':
            user = self.pg_db.get_user_by_email(value)
            available = user is None
        else:
            available = True
        
        handler.send_json_response({'available': available})
    
    def handle_login(self, handler, data):
        """Handle login"""
        username_or_email = data.get('username_or_email', '')
        password = data.get('password', '')
        
        # Try to find user by email or username
        user = self.pg_db.get_user_by_email(username_or_email)
        if not user:
            user = self.pg_db.get_user_by_username(username_or_email)
        
        if not user or self.hash_password(password) != user['password_hash']:
            handler.send_json_response({'success': False, 'error': 'Invalid credentials'}, 401)
            return
        
        if not user['is_active']:
            handler.send_json_response({'success': False, 'error': 'Account is deactivated'}, 403)
            return
        
        # Log login
        self.mongo_db.log_activity(
            user_id=user['id'],
            action='login',
            ip_address=handler.client_address[0],
            user_agent=handler.headers.get('User-Agent')
        )
        
        # Create session
        import datetime
        import secrets
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        self.mongo_db.create_session(user['id'], session_token, expires_at)
        
        handler.send_header('Set-Cookie', f'session_token={session_token}; HttpOnly; Path=/; Max-Age=86400')
        handler.send_json_response({
            'success': True,
            'message': 'Login successful',
            'redirect': '/dashboard'
        })
