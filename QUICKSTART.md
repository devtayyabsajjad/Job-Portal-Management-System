# Quick Start Guide - Job Portal

## Setup in 6 Steps

### 1. Navigate to Project Directory
```bash
cd "c:\Users\TAYYAB SAJJAD\Desktop\job portal\job_portal_project"
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Run Database Migrations (Supabase)
```bash
python manage.py migrate
```

**Note:** Ensure you have internet connection for Supabase!

### 4. Create Admin User
```bash
python manage.py create_admin
```

### 5. Run the Server
```bash
python manage.py runserver
```

### 6. Open Browser
Visit: **http://127.0.0.1:8000/**

---

## Default Login Credentials

### Admin Account (After running create_admin)
- **URL:** http://127.0.0.1:8000/login/
- **Username:** `admin`
- **Password:** `admin123`
- **⚠️ CHANGE PASSWORD IMMEDIATELY!**

## Quick Commands

| Command | Description |
|---------|-------------|
| `python manage.py runserver` | Start development server |
| `python manage.py migrate` | Run database migrations |
| `python manage.py create_admin` | Create admin user |
| `python manage.py createsuperuser` | Create custom superuser |
| `python manage.py makemigrations` | Create new migrations |
| `python manage.py shell` | Open Django shell |

## User Registration

### Job Seeker
- Go to: http://127.0.0.1:8000/register/
- Register and complete profile
- Start applying for jobs

### Company
- Go to: http://127.0.0.1:8000/company/register/
- Register company
- Wait for admin approval
- Post jobs once approved

## Project Status

✅ Database: SQLite (Local Development)
✅ Admin User: Created
✅ Migrations: Applied
✅ Static Files: Configured
✅ Virtual Environment: Created

## Need Help?

Read the full [README.md](README.md) for detailed documentation.

## Quick Troubleshooting

**Server not starting?**
```bash
venv\Scripts\activate
python manage.py runserver
```

**Port already in use?**
```bash
python manage.py runserver 8001
```

**Database error?**
```bash
python manage.py migrate
```

---

**That's it! You're ready to go!** 🎉
