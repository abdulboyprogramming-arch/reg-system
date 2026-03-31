# 📝 Registration System

A complete, production-ready registration system built from scratch with Python, PostgreSQL, and MongoDB. No frontend frameworks, no Python web frameworks - just pure code.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791.svg)](https://www.postgresql.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-47A248.svg)](https://www.mongodb.com/)

## 🚀 Features

### Frontend
- 📝 **Complete Registration Form** with 20+ field types:
  - Text, Email, Password, Telephone
  - Date picker, Country dropdown, City input
  - Radio buttons (Gender, Contact method)
  - Checkboxes (Interests, Terms & Conditions)
  - File uploads (Profile picture, Resume, Multiple files)
  - Textarea (Bio), URL (Website), Social media handles
- ✅ **Real-time validation** and username/email availability checking
- 🔐 **User login** with secure session management
- 📊 **User dashboard** with activity feed and statistics
- 👑 **Admin panel** with complete user management
- 📱 **Fully responsive design** for all devices

### Backend
- 🚀 **Pure Python HTTP server** (no Flask/Django dependencies)
- 🔒 **Secure session-based authentication** with HTTP-only cookies
- 📁 **File upload handling** with validation and secure storage
- 🔑 **Password hashing** with SHA-256 (upgradable to bcrypt)
- 📝 **Comprehensive activity logging** for audit trails
- 🎯 **RESTful API endpoints** for all operations

### Databases
- **PostgreSQL**: Structured user data with JSONB support for flexible metadata
- **MongoDB**: Activity logs, user sessions, and dynamic form submissions

## 📋 Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Security Features](#security-features)
- [Extensibility](#extensibility)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🛠 Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Backend | Python (http.server) | 3.8+ |
| Database (Structured) | PostgreSQL | 13+ |
| Database (Unstructured) | MongoDB | 4.4+ |
| Frontend | HTML5, CSS3, Vanilla JS | - |
| Authentication | Session-based with cookies | - |
| Password Security | SHA-256 hashing | - |

## 📁 Project Structure

```plaintext
registration_system/
│
├── backend/                         # Python backend server
│   ├── server.py                   # Main HTTP server (entry point)
│   ├── db_postgres.py              # PostgreSQL database operations
│   ├── db_mongo.py                 # MongoDB database operations
│   ├── routes/                     # API route handlers
│   │   ├── __init__.py            # Makes routes a Python package
│   │   ├── register.py            # Registration & login endpoints
│   │   ├── admin.py               # Admin management endpoints
│   │   └── api.py                 # General API endpoints
│   └── templates/                  # HTML templates
│       └── base.html              # Base template for pages
│
├── frontend/                        # Static frontend files
│   ├── index.html                 # Landing page
│   ├── register.html              # Registration form (20+ fields)
│   ├── login.html                 # User login page
│   ├── dashboard.html             # User dashboard
│   ├── admin.html                 # Admin panel
│   ├── css/
│   │   └── style.css             # Responsive CSS styles
│   └── js/
│       └── app.js                # Frontend JavaScript logic
│
├── uploads/                         # Uploaded files (auto-created)
│   └── .gitkeep                   # Keep directory in version control
│
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
├── PROJECT_STRUCTURE.md            # Detailed structure documentation
└── README.md                       # This file
```

📋 Prerequisites

Before you begin, ensure you have the following installed:

· Python 3.8 or higher - Download
· PostgreSQL 13 or higher - Download
· MongoDB 4.4 or higher - Download
· Git (optional) - Download

🔧 Installation

1. Clone the Repository

```bash
git clone https://github.com/abdulboyprogramming-arch/reg-system.git
cd reg-system
```

2. Create and Activate Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

4. Setup PostgreSQL

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE reg_system;

-- Create user (optional, if you want a dedicated user)
CREATE USER reg_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE reg_system TO reg_user;

-- Exit
\q
```

5. Setup MongoDB

MongoDB typically runs on default settings:

· URI: mongodb://localhost:27017/
· Database: registration_system (auto-created)

To verify MongoDB is running:

```bash
# Check MongoDB status
mongod --version

# Connect to MongoDB
mongosh
```

⚙️ Configuration

1. Create Environment File

Copy the example environment file and update with your credentials:

```bash
cp .env.example .env
```

2. Edit .env with Your Credentials

```bash
# PostgreSQL Configuration
DB_NAME=reg_system
DB_USER=postgres
DB_PASSWORD=your_actual_password_here
DB_HOST=localhost
DB_PORT=5432

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=registration_system

# Security
SECRET_KEY=your-super-secret-key-here-change-this-in-production
SESSION_TIMEOUT_HOURS=24

# Server Configuration
PORT=8080
DEBUG=False

# File Upload Configuration
MAX_FILE_SIZE=5242880  # 5MB in bytes
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,pdf,doc,docx
```

3. Test Database Connections

```bash
# Create a test script or run Python commands
python -c "from backend.db_postgres import PostgresDB; PostgresDB()"
python -c "from backend.db_mongo import MongoDB; MongoDB()"
```

🚀 Running the Application

Start the Server

```bash
cd backend
python server.py
```

Access the Application

Open your browser and navigate to:

```
http://localhost:8080
```

## 🗺️ Default Pages

| URL | Description | Access |
|-----|-------------|--------|
| `/` | Landing page (redirects to dashboard if logged in) | Public |
| `/register` | Registration form | Public |
| `/login.html` | Login page | Public |
| `/dashboard` | User dashboard | Authenticated |
| `/admin` | Admin panel | Admin only |

---

## 📡 API Endpoints

### Public Endpoints

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| POST | `/api/register` | Register new user | `{email, username, password, confirm_password, ...}` |
| POST | `/api/login` | User login | `{username_or_email, password}` |
| POST | `/api/check-availability` | Check username/email availability | `{field, value}` |
| GET | `/api/session` | Get current session info | - |

### Authenticated Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/upload` | Upload files | Authenticated |
| POST | `/api/save-form-data` | Save custom form data | Authenticated |
| GET | `/api/user-activity` | Get user activity logs | Authenticated |
| GET | `/api/form-submissions` | Get user form submissions | Authenticated |
| GET | `/api/stats` | Get user statistics | Authenticated |

### Admin Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/users` | List all users | Admin only |
| POST | `/api/update-user` | Update user details | Admin only |
| GET | `/api/user-activity?user_id=X` | View specific user activity | Admin only |

---

## 🗄️ Database Schema

### PostgreSQL Tables

#### `users` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `email` | VARCHAR(255) | Unique email address |
| `username` | VARCHAR(100) | Unique username |
| `password_hash` | VARCHAR(255) | Hashed password |
| `full_name` | VARCHAR(255) | User's full name |
| `phone` | VARCHAR(50) | Phone number |
| `date_of_birth` | DATE | Date of birth |
| `gender` | VARCHAR(20) | Gender selection |
| `country` | VARCHAR(100) | Country of residence |
| `city` | VARCHAR(100) | City |
| `postal_code` | VARCHAR(20) | Postal/ZIP code |
| `created_at` | TIMESTAMP | Account creation time |
| `updated_at` | TIMESTAMP | Last update time |
| `is_active` | BOOLEAN | Account status |
| `is_admin` | BOOLEAN | Admin privileges |
| `email_verified` | BOOLEAN | Email verification status |

#### `user_metadata` Table

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | INTEGER | References users(id) |
| `metadata` | JSONB | Flexible user metadata |
| `preferences` | JSONB | User preferences |

#### `email_tokens` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `user_id` | INTEGER | References users(id) |
| `token` | VARCHAR(255) | Unique verification token |
| `expires_at` | TIMESTAMP | Token expiration |
| `used` | BOOLEAN | Token usage status |

## MongoDB Collections

activity_logs

```javascript
{
  _id: ObjectId,
  user_id: Number,
  action: String,
  ip_address: String,
  user_agent: String,
  details: Object,
  timestamp: ISODate
}
```

form_submissions

```javascript
{
  _id: ObjectId,
  submission_type: String,
  user_id: Number,
  data: Object,
  submitted_at: ISODate
}
```

user_sessions

```javascript
{
  _id: ObjectId,
  user_id: Number,
  session_token: String,
  expires_at: ISODate,
  created_at: ISODate
}
```

🔒 Security Features

· ✅ HTTP-only cookies for session storage
· ✅ Password hashing with SHA-256 (upgradable to bcrypt)
· ✅ Session expiration (24 hours default)
· ✅ Account deactivation capability
· ✅ Input validation and sanitization
· ✅ Activity logging for audit trails
· ✅ Admin-only endpoints protection
· ✅ File upload validation (type and size)
· ✅ Environment variables for secrets
· ✅ SQL injection prevention (parameterized queries)

🔧 Extensibility

The system is designed for easy extension:

Add New API Endpoints

1. Add method in appropriate route class (routes/register.py, routes/admin.py, or routes/api.py)
2. Add route mapping in server.py

Add New Database Tables

1. Add creation logic in db_postgres.py init_db() method
2. Add helper methods for CRUD operations

Add New Frontend Pages

1. Create HTML file in frontend/
2. Add route in server.py GET handler

Implement Email Verification

· Table email_tokens is ready
· Add email sending logic in routes/register.py

Add Password Reset

· Extend email_tokens table for reset tokens
· Add new endpoints in routes/api.py

Implement Rate Limiting

· Add rate limiter class in server.py
· Decorate API endpoints with rate limit checks

🐛 Troubleshooting

Database Connection Errors

Error: psycopg2.OperationalError: could not connect to server

Solution:

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
pg_ctl status  # Mac
# Windows: Check Services

# Verify credentials in .env file
cat .env | grep DB_
```

MongoDB Connection Errors

Error: pymongo.errors.ServerSelectionTimeoutError

Solution:

```bash
# Check if MongoDB is running
sudo systemctl status mongod  # Linux
brew services list | grep mongodb  # Mac
# Windows: Check Services

# Start MongoDB if needed
sudo systemctl start mongod  # Linux
brew services start mongodb  # Mac
```

File Upload Issues

Error: File too large or File type not allowed

Solution:

· Check MAX_FILE_SIZE in .env (default: 5MB)
· Verify ALLOWED_EXTENSIONS includes your file type
· Ensure uploads/ directory has write permissions

Session Problems

Issue: Session not persisting or immediate logout

Solution:

· Clear browser cookies
· Check MongoDB user_sessions collection for expired sessions
· Verify SESSION_TIMEOUT_HOURS in .env

Port Already in Use

Error: Address already in use

Solution:

```bash
# Change PORT in .env file
PORT=8081

# Or kill process using the port
# Linux/Mac
lsof -ti:8080 | xargs kill -9
# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add some AmazingFeature')
4. Push to the branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

Development Guidelines

· Follow PEP 8 style guide for Python code
· Use meaningful commit messages
· Update documentation for new features
· Add tests for new functionality
· Ensure all existing features work

📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments

· Built with Python's built-in http.server module
· PostgreSQL for reliable structured data storage
· MongoDB for flexible document storage
· Vanilla JavaScript for lightweight frontend

📞 Support

For issues, questions, or contributions:

· Open an issue on GitHub
· Contact the maintainer
· Check the troubleshooting section

---

⚠️ Security Notice: This code is for educational/demonstration purposes. For production use, please implement:

· HTTPS with SSL/TLS certificates
· Strong password hashing (bcrypt/argon2)
· Rate limiting on all endpoints
· CSRF protection
· Regular security updates
· Database encryption at rest

---

Made with ❤️ for the developer community
