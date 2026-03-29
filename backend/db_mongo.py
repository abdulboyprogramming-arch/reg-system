from pymongo import MongoClient
from datetime import datetime

class MongoDB:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="registration_system"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.init_collections()

    def init_collections(self):
        # Activity logs
        if "activity_logs" not in self.db.list_collection_names():
            self.db.create_collection("activity_logs", capped=False)
            self.db.activity_logs.create_index("user_id")
            self.db.activity_logs.create_index("timestamp")
        
        # Form submissions (dynamic data)
        if "form_submissions" not in self.db.list_collection_names():
            self.db.create_collection("form_submissions")
            self.db.form_submissions.create_index("submission_type")
        
        # User sessions
        if "user_sessions" not in self.db.list_collection_names():
            self.db.create_collection("user_sessions")
            self.db.user_sessions.create_index("session_token", unique=True)
            self.db.user_sessions.create_index("expires_at")

    def log_activity(self, user_id, action, ip_address=None, user_agent=None, details=None):
        self.db.activity_logs.insert_one({
            "user_id": user_id,
            "action": action,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "details": details or {},
            "timestamp": datetime.utcnow()
        })

    def save_form_submission(self, submission_type, data, user_id=None):
        result = self.db.form_submissions.insert_one({
            "submission_type": submission_type,
            "user_id": user_id,
            "data": data,
            "submitted_at": datetime.utcnow()
        })
        return result.inserted_id

    def create_session(self, user_id, session_token, expires_at):
        self.db.user_sessions.insert_one({
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": expires_at,
            "created_at": datetime.utcnow()
        })

    def get_session(self, session_token):
        return self.db.user_sessions.find_one({"session_token": session_token, "expires_at": {"$gt": datetime.utcnow()}})
