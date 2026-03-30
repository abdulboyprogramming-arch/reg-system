"""General API route handlers"""
import json
import os
import secrets
import sys
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

class APIRoutes:
    def __init__(self, pg_db, mongo_db):
        self.pg_db = pg_db
        self.mongo_db = mongo_db
    
    def handle_get_session(self, handler, session):
        """Get current session info"""
        if session:
            handler.send_json_response({'authenticated': True, 'user': session})
        else:
            handler.send_json_response({'authenticated': False})
    
    def handle_upload(self, handler, session, form_data, files):
        """Handle file uploads"""
        uploaded_files = []
        
        for field_name, file_data in files.items():
            if file_data and file_data.get('filename'):
                filename = f"{secrets.token_hex(8)}_{file_data['filename']}"
                filepath = os.path.join(UPLOAD_DIR, filename)
                with open(filepath, 'wb') as f:
                    f.write(file_data['content'])
                
                uploaded_files.append({
                    'original_name': file_data['filename'],
                    'saved_name': filename,
                    'size': len(file_data['content']),
                    'path': f'/uploads/{filename}'
                })
        
        if session:
            self.mongo_db.log_activity(
                user_id=session['user_id'],
                action='upload',
                details={'files': uploaded_files}
            )
        
        handler.send_json_response({
            'success': True,
            'files': uploaded_files
        })
    
    def handle_save_form_data(self, handler, session, data):
        """Save arbitrary form data to MongoDB"""
        submission_type = data.get('submission_type', 'generic')
        form_data = data.get('data', {})
        
        user_id = session['user_id'] if session else None
        submission_id = self.mongo_db.save_form_submission(submission_type, form_data, user_id)
        
        handler.send_json_response({
            'success': True,
            'submission_id': str(submission_id),
            'message': 'Form data saved successfully'
        })
    
    def handle_get_user_activity(self, handler, session, query_params):
        """Get user activity logs"""
        if not session:
            handler.send_json_response({'error': 'Unauthorized'}, 403)
            return
        
        user_id = session['user_id']
        # Admin can view other users
        if session.get('is_admin', False) and 'user_id' in query_params:
            user_id = int(query_params['user_id'][0])
        
        logs = list(self.mongo_db.db.activity_logs.find({'user_id': user_id}).sort('timestamp', -1).limit(50))
        for log in logs:
            log['_id'] = str(log['_id'])
            log['timestamp'] = str(log['timestamp'])
        
        handler.send_json_response({'activity_logs': logs})
    
    def handle_get_form_submissions(self, handler, session, query_params):
        """Get form submissions"""
        if not session:
            handler.send_json_response({'error': 'Unauthorized'}, 403)
            return
        
        submission_type = query_params.get('type', [None])[0]
        query = {}
        if submission_type:
            query['submission_type'] = submission_type
        if not session.get('is_admin', False):
            query['user_id'] = session['user_id']
        
        submissions = list(self.mongo_db.db.form_submissions.find(query).sort('submitted_at', -1).limit(100))
        for sub in submissions:
            sub['_id'] = str(sub['_id'])
            sub['submitted_at'] = str(sub['submitted_at'])
        
        handler.send_json_response({'submissions': submissions})
