registration_system/
├── backend/
│   ├── server.py           (main HTTP server)
│   ├── db_postgres.py      (PostgreSQL handler)
│   ├── db_mongo.py         (MongoDB handler)
│   ├── routes/
│   │   ├── register.py
│   │   ├── admin.py        (stub for later)
│   │   └── api.py
│   └── templates/          (we'll serve static HTML)
├── frontend/
│   ├── index.html
│   ├── register.html
│   ├── dashboard.html      (stub)
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── requirements.txt        (only psycopg2-binary, pymongo)
