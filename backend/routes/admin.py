"""Admin route handlers"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

class AdminRoutes:
    def __init__(self, pg_db, mongo_db):
        self.pg_db = pg_db
        self.mongo_db = mongo_db
    
    def check_admin(self, session):
        """Verify user is admin"""
        return session and session.get('is_admin', False)
    
    def handle_get_users(self, handler, session, query_params):
        """Get all users (admin only)"""
        if not self.check_admin(session):
            handler.send_json_response({'error': 'Unauthorized'}, 403)
            return
        
        limit = int(query_params.get('limit', [100])[0])
        offset = int(query_params.get('offset', [0])[0])
        
        users = self.pg_db.get_all_users(limit, offset)
        user_list = []
        for user in users:
            user_list.append({
                'id': user['id'],
                'email': user['email'],
                'username': user['username'],
                'full_name': user['full_name'],
                'phone': user['phone'],
                'created_at': str(user['created_at']),
                'is_active': user['is_active'],
                'is_admin': user['is_admin'],
                'email_verified': user['email_verified']
            })
        
        handler.send_json_response({'users': user_list, 'count': len(user_list)})
    
    def handle_update_user(self, handler, session, data):
        """Update user (admin only)"""
        if not self.check_admin(session):
            handler.send_json_response({'error': 'Unauthorized'}, 403)
            return
        
        user_id = data.get('user_id')
        updates = data.get('updates', {})
        
        # Remove sensitive fields
        forbidden = ['id', 'password_hash', 'created_at', 'email', 'username']
        for field in forbidden:
            updates.pop(field, None)
        
        if self.pg_db.update_user(user_id, updates):
            self.mongo_db.log_activity(
                user_id=session['user_id'],
                action='admin_update_user',
                details={'target_user': user_id, 'updates': updates}
            )
            handler.send_json_response({'success': True, 'message': 'User updated'})
        else:
            handler.send_json_response({'success': False, 'error': 'Update failed'}, 500)
    
    def handle_delete_user(self, handler, session, user_id):
        """Soft delete user (admin only)"""
        if not self.check_admin(session):
            handler.send_json_response({'error': 'Unauthorized'}, 403)
            return
        
        if self.pg_db.delete_user(user_id):
            self.mongo_db.log_activity(
                user_id=session['user_id'],
                action='admin_delete_user',
                details={'target_user': user_id}
            )
            handler.send_json_response({'success': True, 'message': 'User deactivated'})
        else:
            handler.send_json_response({'success': False, 'error': 'Delete failed'}, 500)
    
    def handle_get_stats(self, handler, session):
        """Get system statistics (admin only)"""
        if not self.check_admin(session):
            handler.send_json_response({'error': 'Unauthorized'}, 403)
            return
        
        import datetime
        users = self.pg_db.get_all_users(limit=10000)
        total_users = len(users)
        active_users = sum(1 for u in users if u['is_active'])
        admin_users = sum(1 for u in users if u['is_admin'])
        
        recent_activities = list(self.mongo_db.db.activity_logs.find({
            'timestamp': {'$gte': datetime.datetime.utcnow() - datetime.timedelta(days=7)}
        }))
        
        stats = {
            'total_users': total_users,
            'active_users': active_users,
            'admin_users': admin_users,
            'activities_last_7_days': len(recent_activities),
            'registration_rate': f"{(active_users/total_users*100):.1f}%" if total_users > 0 else "0%"
        }
        
        handler.send_json_response({'stats': stats})
