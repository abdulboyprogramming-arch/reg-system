# 📁 Project Structure

## Complete File Tree

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
├── PROJECT_STRUCTURE.md            # This file
└── README.md                       # Project documentation
```

## 📁 Project Structure

```mermaid
graph TD
    A[registration_system/] --> B[backend/]
    A --> C[frontend/]
    A --> D[uploads/]
    A --> E[.env.example]
    A --> F[.gitignore]
    A --> G[requirements.txt]
    
    B --> B1[server.py]
    B --> B2[db_postgres.py]
    B --> B3[db_mongo.py]
    B --> B4[routes/]
    B --> B5[templates/]
    
    B4 --> B4a[register.py]
    B4 --> B4b[admin.py]
    B4 --> B4c[api.py]
    
    B5 --> B5a[base.html]
    
    C --> C1[index.html]
    C --> C2[register.html]
    C --> C3[login.html]
    C --> C4[dashboard.html]
    C --> C5[admin.html]
    C --> C6[css/]
    C --> C7[js/]
    
    C6 --> C6a[style.css]
    C7 --> C7a[app.js]## 📁 Project Structure

```mermaid
graph TD
    A[registration_system/] --> B[backend/]
    A --> C[frontend/]
    A --> D[uploads/]
    A --> E[.env.example]
    A --> F[.gitignore]
    A --> G[requirements.txt]
    
    B --> B1[server.py]
    B --> B2[db_postgres.py]
    B --> B3[db_mongo.py]
    B --> B4[routes/]
    B --> B5[templates/]
    
    B4 --> B4a[register.py]
    B4 --> B4b[admin.py]
    B4 --> B4c[api.py]
    
    B5 --> B5a[base.html]
    
    C --> C1[index.html]
    C --> C2[register.html]
    C --> C3[login.html]
    C --> C4[dashboard.html]
    C --> C5[admin.html]
    C --> C6[css/]
    C --> C7[js/]
    
    C6 --> C6a[style.css]
    C7 --> C7a[app.js]## 📁 Project Structure

```mermaid
graph TD
    A[registration_system/] --> B[backend/]
    A --> C[frontend/]
    A --> D[uploads/]
    A --> E[.env.example]
    A --> F[.gitignore]
    A --> G[requirements.txt]
    
    B --> B1[server.py]
    B --> B2[db_postgres.py]
    B --> B3[db_mongo.py]
    B --> B4[routes/]
    B --> B5[templates/]
    
    B4 --> B4a[register.py]
    B4 --> B4b[admin.py]
    B4 --> B4c[api.py]
    
    B5 --> B5a[base.html]
    
    C --> C1[index.html]
    C --> C2[register.html]
    C --> C3[login.html]
    C --> C4[dashboard.html]
    C --> C5[admin.html]
    C --> C6[css/]
    C --> C7[js/]
    
    C6 --> C6a[style.css]
    C7 --> C7a[app.js]
```
