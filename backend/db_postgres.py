import psycopg2
from psycopg2 import sql, extras
import json

class PostgresDB:
    def __init__(self, dbname="reg_system", user="postgres", password="postgres", host="localhost", port=5432):
        self.conn_params = {
            "dbname": dbname,
            "user": user,
            "password": password,
            "host": host,
            "port": port
        }
        self.conn = None
        self.init_db()

    def connect(self):
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(**self.conn_params)
        return self.conn

    def init_db(self):
        conn = self.connect()
        cur = conn.cursor()
        # Users table - core registration data
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                phone VARCHAR(50),
                date_of_birth DATE,
                gender VARCHAR(20),
                country VARCHAR(100),
                city VARCHAR(100),
                postal_code VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                is_admin BOOLEAN DEFAULT FALSE,
                email_verified BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Additional profile fields (flexible JSONB)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_metadata (
                user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                metadata JSONB DEFAULT '{}'::jsonb,
                preferences JSONB DEFAULT '{}'::jsonb
            )
        """)
        
        # Email verification tokens
        cur.execute("""
            CREATE TABLE IF NOT EXISTS email_tokens (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                token VARCHAR(255) UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT FALSE
            )
        """)
        
        conn.commit()
        cur.close()

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        conn = self.connect()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query, params or ())
        result = None
        if fetch_one:
            result = cur.fetchone()
        elif fetch_all:
            result = cur.fetchall()
        conn.commit()
        cur.close()
        return result

    def insert_user(self, user_data):
        query = """
            INSERT INTO users (email, username, password_hash, full_name, phone, date_of_birth, gender, country, city, postal_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        params = (
            user_data['email'],
            user_data['username'],
            user_data['password_hash'],
            user_data.get('full_name'),
            user_data.get('phone'),
            user_data.get('date_of_birth'),
            user_data.get('gender'),
            user_data.get('country'),
            user_data.get('city'),
            user_data.get('postal_code')
        )
        result = self.execute_query(query, params, fetch_one=True)
        user_id = result[0] if result else None
        if user_id:
            # Insert empty metadata
            self.execute_query(
                "INSERT INTO user_metadata (user_id, metadata, preferences) VALUES (%s, %s, %s)",
                (user_id, '{}', '{}')
            )
        return user_id

    def get_user_by_email(self, email):
        return self.execute_query("SELECT * FROM users WHERE email = %s", (email,), fetch_one=True)

    def get_user_by_username(self, username):
        return self.execute_query("SELECT * FROM users WHERE username = %s", (username,), fetch_one=True)
