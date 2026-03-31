from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class MongoDB:
    def __init__(self):
        # Read MongoDB configuration from environment variables
        uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        db_name = os.getenv('MONGODB_DB_NAME', 'registration_system')
        
        try:
            self.client = MongoClient(uri)
            # Test the connection
            self.client.admin.command('ping')
            self.db = self.client[db_name]
            self.init_collections()
            print(f"✅ MongoDB connected successfully to database: {db_name}")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            print("Please check your MongoDB connection in .env file")
            raise

    def init_collections(self):
        """Initialize collections and indexes"""
        try:
            # Activity logs
            if "activity_logs" not in self.db.list_collection_names():
                self.db.create_collection("activity_logs", capped=False)
                self.db.activity_logs.create_index("user_id")
                self.db.activity_logs.create_index("timestamp")
            
            # Form submissions (dynamic data)
            if "form_submissions" not in self.db.list_collection_names():
                self.db.create_collection("form_submissions")
                self.db.form_submissions.create_index("submission_type")
                self.db.form_submissions.create_index("user_id")
            
            # User sessions
            if "user_sessions" not in self.db.list_collection_names():
                self.db.create_collection("user_sessions")
                self.db.user_sessions.create_index("session_token", unique=True)
                self.db.user_sessions.create_index("expires_at")
            
            # Create TTL index to auto-expire old sessions
            self.db.user_sessions.create_index("expires_at", expireAfterSeconds=0)
            
            print("✅ MongoDB collections initialized")
        except Exception as e:
            print(f"⚠️ Failed to initialize collections: {e}")

    def log_activity(self, user_id, action, ip_address=None, user_agent=None, details=None):
        """Log user activity with error handling"""
        try:
            self.db.activity_logs.insert_one({
                "user_id": user_id,
                "action": action,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "details": details or {},
                "timestamp": datetime.utcnow()
            })
        except Exception as e:
            # Log to console but don't crash the application
            print(f"⚠️ Failed to log activity: {e}")

    def save_form_submission(self, submission_type, data, user_id=None):
        """Save form submission data with error handling"""
        try:
            result = self.db.form_submissions.insert_one({
                "submission_type": submission_type,
                "user_id": user_id,
                "data": data,
                "submitted_at": datetime.utcnow()
            })
            return result.inserted_id
        except Exception as e:
            print(f"⚠️ Failed to save form submission: {e}")
            return None

    def create_session(self, user_id, session_token, expires_at):
        """Create a new user session"""
        try:
            self.db.user_sessions.insert_one({
                "user_id": user_id,
                "session_token": session_token,
                "expires_at": expires_at,
                "created_at": datetime.utcnow()
            })
        except Exception as e:
            print(f"⚠️ Failed to create session: {e}")

    def get_session(self, session_token):
        """Get a valid session (not expired)"""
        try:
            return self.db.user_sessions.find_one({
                "session_token": session_token, 
                "expires_at": {"$gt": datetime.utcnow()}
            })
        except Exception as e:
            print(f"⚠️ Failed to get session: {e}")
            return None

    def delete_session(self, session_token):
        """Delete a session (logout)"""
        try:
            self.db.user_sessions.delete_one({"session_token": session_token})
        except Exception as e:
            print(f"⚠️ Failed to delete session: {e}")

    def get_user_activity(self, user_id, limit=50):
        """Get recent user activity logs"""
        try:
            return list(self.db.activity_logs.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit))
        except Exception as e:
            print(f"⚠️ Failed to get user activity: {e}")
            return []

    def get_all_activity(self, limit=100, skip=0):
        """Get all activity logs (admin only)"""
        try:
            return list(self.db.activity_logs.find()
                       .sort("timestamp", -1)
                       .skip(skip)
                       .limit(limit))
        except Exception as e:
            print(f"⚠️ Failed to get all activity: {e}")
            return []

    def cleanup_expired_sessions(self):
        """Manually cleanup expired sessions (TTL index handles this automatically)"""
        try:
            result = self.db.user_sessions.delete_many({
                "expires_at": {"$lt": datetime.utcnow()}
            })
            return result.deleted_count
        except Exception as e:
            print(f"⚠️ Failed to cleanup sessions: {e}")
            return 0