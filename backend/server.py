#!/usr/bin/env python3
import http.server
import socketserver
import json
import urllib.parse
import urllib.request
import urllib.error
import os
import sys
import hashlib
import secrets
import datetime
import re
import tempfile
import shutil
from email.utils import formatdate
import cgi
import io

# Add backend directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from db_postgres import PostgresDB
from db_mongo import MongoDB

# Initialize databases
pg_db = PostgresDB()
mongo_db = MongoDB()

# Configuration
PORT = 8080
SESSION_TIMEOUT_HOURS = 24
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

class RegistrationHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler for registration system"""
    
    def __init__(self, *args, **kwargs):
        self.pg_db = pg_db
        self.mongo_db = mongo_db
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Static files (CSS, JS, images)
        if path.startswith('/css/') or path.startswith('/js/') or path.startswith('/uploads/'):
            self.serve_static_file(path[1:])
            return
        
        # Routes
        routes = {
            '/': self.serve_index,
            '/register': self.serve_register_page,
            '/dashboard': self.serve_dashboard_page,
            '/admin': self.serve_admin_page,
            '/verify-email': self.verify_email,
            '/logout': self.handle_logout,
            '/api/session': self.get_session_info
        }
        
        if path in routes:
            routes[path]()
        else:
            self.send_404()
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        routes = {
            '/api/register': self.api_register,
            '/api/login': self.api_login,
            '/api/upload': self.api_upload,
            '/api/save-form-data': self.api_save_form_data,
            '/api/check-availability': self.api_check_availability
        }
        
        if path in routes:
            routes[path]()
        else:
            self.send_404()
    
    def serve_static_file(self, filepath):
        """Serve static files safely"""
        try:
            full_path = os.path.join(os.path.dirname(__file__), '..', filepath)
            if os.path.exists(full_path) and not os.path.isdir(full_path):
                self.send_response(200)
                if filepath.endswith('.css'):
                    self.send_header('Content-type', 'text/css')
                elif filepath.endswith('.js'):
                    self.send_header('Content-type', 'application/javascript')
                elif filepath.endswith('.html'):
                    self.send_header('Content-type', 'text/html')
                else:
                    self.send_header('Content-type', 'application/octet-stream')
                self.end_headers()
                with open(full_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_404()
        except Exception as e:
            self.send_error(500, f"Error serving file: {str(e)}")
    
    def serve_index(self):
        """Serve index/home page"""
        session = self.get_session()
        if session:
            # User is logged in, redirect to dashboard
            self.send_response(302)
            self.send_header('Location', '/dashboard')
            self.end_headers()
        else:
            self.serve_html_file('index.html')
    
    def serve_register_page(self):
        """Serve registration page"""
        self.serve_html_file('register.html')
    
    def serve_dashboard_page(self):
        """Serve dashboard page (stub for now)"""
        session = self.get_session()
        if not session:
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
            return
        self.serve_html_file('dashboard.html')
    
    def serve_admin_page(self):
        """Serve admin page (stub for extensibility)"""
        session = self.get_session()
        if not session or not session.get('is_admin', False):
            self.send_response(403)
            self.wfile.write(b"Access denied")
            return
        self.serve_html_file('admin.html')
    
    def serve_html_file(self, filename):
        """Serve HTML file from frontend directory"""
        try:
            filepath = os.path.join(os.path.dirname(__file__), '..', 'frontend', filename)
            with open(filepath, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(404, f"File not found: {filename}")
    
    def send_404(self):
        """Send 404 error"""
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>404 Not Found</h1>")
    
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def get_post_data(self):
        """Parse POST data (supports both JSON and form-urlencoded)"""
        content_type = self.headers.get('Content-Type', '')
        content_length = int(self.headers.get('Content-Length', 0))
        raw_data = self.rfile.read(content_length)
        
        if 'application/json' in content_type:
            return json.loads(raw_data.decode('utf-8'))
        elif 'multipart/form-data' in content_type:
            # Parse multipart form data
            form = cgi.FieldStorage(
                fp=io.BytesIO(raw_data),
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            return {key: form[key].value for key in form.keys()}
        else:
            # URL-encoded form data
            return urllib.parse.parse_qs(raw_data.decode('utf-8'))
    
    def get_session(self):
        """Retrieve session from cookie"""
        cookie_header = self.headers.get('Cookie', '')
        cookies = {}
        for cookie in cookie_header.split(';'):
            if '=' in cookie:
                key, value = cookie.strip().split('=', 1)
                cookies[key] = value
        
        session_token = cookies.get('session_token')
        if session_token:
            session = self.mongo_db.get_session(session_token)
            if session:
                # Also fetch user data from PostgreSQL
                user = self.pg_db.get_user_by_id(session['user_id'])
                if user:
                    return {
                        'user_id': session['user_id'],
                        'session_token': session_token,
                        'username': user['username'],
                        'email': user['email'],
                        'is_admin': user['is_admin']
                    }
        return None
    
    def set_session(self, user_id):
        """Create new session and set cookie"""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=SESSION_TIMEOUT_HOURS)
        self.mongo_db.create_session(user_id, session_token, expires_at)
        
        self.send_header('Set-Cookie', f'session_token={session_token}; HttpOnly; Path=/; Max-Age={SESSION_TIMEOUT_HOURS*3600}')
    
    def clear_session(self):
        """Clear session cookie"""
        self.send_header('Set-Cookie', 'session_token=; HttpOnly; Path=/; Max-Age=0')
    
    def handle_logout(self):
        """Logout user"""
        self.send_response(302)
        self.clear_session()
        self.send_header('Location', '/')
        self.end_headers()
    
    def get_session_info(self):
        """API endpoint to get current session info"""
        session = self.get_session()
        if session:
            self.send_json_response({'authenticated': True, 'user': session})
        else:
            self.send_json_response({'authenticated': False})
    
    def hash_password(self, password):
        """Hash password using SHA-256 (for demo - use bcrypt in production)"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password, password_hash):
        """Verify password"""
        return self.hash_password(password) == password_hash
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def api_check_availability(self):
        """Check if username or email is available"""
        data = self.get_post_data()
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
        
        self.send_json_response({'available': available})
    
    def api_register(self):
        """Handle registration submission"""
        try:
            data = self.get_post_data()
            
            # Validate required fields
            required_fields = ['email', 'username', 'password', 'confirm_password']
            for field in required_fields:
                if field not in data:
                    self.send_json_response({'success': False, 'error': f'Missing field: {field}'}, 400)
                    return
            
            # Validate email
            if not self.validate_email(data['email']):
                self.send_json_response({'success': False, 'error': 'Invalid email format'}, 400)
                return
            
            # Check if email exists
            if self.pg_db.get_user_by_email(data['email']):
                self.send_json_response({'success': False, 'error': 'Email already registered'}, 400)
                return
            
            # Check if username exists
            if self.pg_db.get_user_by_username(data['username']):
                self.send_json_response({'success': False, 'error': 'Username already taken'}, 400)
                return
            
            # Validate password
            if len(data['password']) < 6:
                self.send_json_response({'success': False, 'error': 'Password must be at least 6 characters'}, 400)
                return
            
            if data['password'] != data['confirm_password']:
                self.send_json_response({'success': False, 'error': 'Passwords do not match'}, 400)
                return
            
            # Hash password
            password_hash = self.hash_password(data['password'])
            
            # Prepare user data for insertion
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
                self.send_json_response({'success': False, 'error': 'Failed to create user'}, 500)
                return
            
            # Save additional dynamic data to MongoDB
            dynamic_data = {k: v for k, v in data.items() if k not in required_fields and k not in user_data}
            if dynamic_data:
                self.mongo_db.save_form_submission('registration_extra', dynamic_data, user_id)
            
            # Log registration activity
            self.mongo_db.log_activity(
                user_id=user_id,
                action='register',
                ip_address=self.client_address[0],
                user_agent=self.headers.get('User-Agent'),
                details={'registration_data': {k: v for k, v in user_data.items() if k != 'password_hash'}}
            )
            
            # Create session
            self.send_response(200)
            self.set_session(user_id)
            self.send_json_response({
                'success': True,
                'message': 'Registration successful',
                'redirect': '/dashboard'
            })
            
        except Exception as e:
            self.send_json_response({'success': False, 'error': str(e)}, 500)
    
    def api_login(self):
        """Handle login"""
        data = self.get_post_data()
        username_or_email = data.get('username_or_email', '')
        password = data.get('password', '')
        
        # Try to find user by email or username
        user = self.pg_db.get_user_by_email(username_or_email)
        if not user:
            user = self.pg_db.get_user_by_username(username_or_email)
        
        if not user or not self.verify_password(password, user['password_hash']):
            self.send_json_response({'success': False, 'error': 'Invalid credentials'}, 401)
            return
        
        if not user['is_active']:
            self.send_json_response({'success': False, 'error': 'Account is deactivated'}, 403)
            return
        
        # Log login
        self.mongo_db.log_activity(
            user_id=user['id'],
            action='login',
            ip_address=self.client_address[0],
            user_agent=self.headers.get('User-Agent')
        )
        
        # Create session
        self.set_session(user['id'])
        self.send_json_response({
            'success': True,
            'message': 'Login successful',
            'redirect': '/dashboard'
        })
    
    def api_upload(self):
        """Handle file uploads"""
        try:
            content_type = self.headers.get('Content-Type', '')
            if 'multipart/form-data' not in content_type:
                self.send_json_response({'success': False, 'error': 'Expected multipart/form-data'}, 400)
                return
            
            content_length = int(self.headers.get('Content-Length', 0))
            raw_data = self.rfile.read(content_length)
            
            # Parse multipart data
            form = cgi.FieldStorage(
                fp=io.BytesIO(raw_data),
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': content_type}
            )
            
            uploaded_files = []
            for key in form.keys():
                field = form[key]
                if field.filename:
                    # Save file
                    filename = f"{secrets.token_hex(8)}_{field.filename}"
                    filepath = os.path.join(UPLOAD_DIR, filename)
                    with open(filepath, 'wb') as f:
                        f.write(field.value)
                    
                    uploaded_files.append({
                        'original_name': field.filename,
                        'saved_name': filename,
                        'size': len(field.value),
                        'path': f'/uploads/{filename}'
                    })
            
            session = self.get_session()
            if session:
                self.mongo_db.log_activity(
                    user_id=session['user_id'],
                    action='upload',
                    details={'files': uploaded_files}
                )
            
            self.send_json_response({
                'success': True,
                'files': uploaded_files
            })
            
        except Exception as e:
            self.send_json_response({'success': False, 'error': str(e)}, 500)
    
    def api_save_form_data(self):
        """Save arbitrary form data to MongoDB"""
        data = self.get_post_data()
        submission_type = data.get('submission_type', 'generic')
        form_data = data.get('data', {})
        
        session = self.get_session()
        user_id = session['user_id'] if session else None
        
        submission_id = self.mongo_db.save_form_submission(submission_type, form_data, user_id)
        
        self.send_json_response({
            'success': True,
            'submission_id': str(submission_id),
            'message': 'Form data saved successfully'
        })

def run_server():
    """Start the HTTP server"""
    with socketserver.TCPServer(("", PORT), RegistrationHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")

if __name__ == "__main__":
    run_server()
