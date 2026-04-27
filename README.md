# Popna Backend — Django REST Framework

Production-ready DRF backend for the Popna multi-industry business management platform.

## Tech Stack

- **Python** 3.11+
- **Django** 4.2
- **Django REST Framework** 3.15
- **SimpleJWT** 5.3 (JWT auth)
- **MySQL** 5.7.8+ / 8.0
- **django-cors-headers** (CORS for React frontend)
- **django-filter** (filtering support)

---

## Project Structure

```
backend/
├── config/                  # Settings, URLs, WSGI/ASGI
│   └── settings/
│       ├── base.py
│       ├── development.py
│       └── production.py
├── apps/
│   ├── core/                # Base models, management commands
│   ├── users/               # Auth, Users, Organizations, Signup Requests
│   ├── contacts/            # Customers, Suppliers, Vendors
│   ├── inventory/           # Unified catalog (Products, ISP Categories, ISP Plans)
│   ├── activities/          # Complaints, Connection Requests, Appointments, Leads
│   ├── invoices/            # Sales, Purchase, POS invoices
│   ├── documents/           # Quotations, Purchase Orders, Expenses
│   ├── subscriptions/       # Recurring subscriptions
│   ├── org_settings/        # Company profile, branches, SMS, UPI, website
│   ├── audit/               # Audit log + SMS logs
│   └── dashboard/           # KPI stats and reports
├── common/
│   ├── exceptions/          # Custom exception handler
│   ├── permissions/         # Role-based permissions
│   ├── utils/               # Response helpers, pagination
│   └── validators/
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── manage.py
├── .env
└── .env.example
```

---

## Setup

### 1. Clone and create virtual environment

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements/development.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your DB credentials and secret key
```

### 4. Configure JWT authentication backend

Add to `config/settings/base.py` → `REST_FRAMEWORK`:

```python
'DEFAULT_AUTHENTICATION_CLASSES': (
    'apps.users.tokens.PopnaJWTAuthentication',
),
```

### 5. Create the MySQL database

```sql
CREATE DATABASE popna_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Run migrations

```bash
python manage.py migrate
```

### 7. Create log directory

```bash
mkdir logs
```

### 8. Seed initial data

```bash
python manage.py seed_data
```

To reset and re-seed:

```bash
python manage.py seed_data --flush
```

### 9. Run the development server

```bash
python manage.py runserver 0.0.0.0:8000
```

---

## Default Credentials (after seeding)

| Role        | Username         | Password         |
|-------------|-----------------|------------------|
| Super Admin | `superadmin`    | `superadmin123`  |
| Admin       | `bankaitech`    | `test123`        |
| Employee    | `bankaitech-emp`| `test123`        |

---

## Authentication

All API calls (except public endpoints) require:

```
Authorization: Bearer <access_token>
```

### Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "bankaitech",
  "password": "test123",
  "organization_id": "org_001"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "access": "<jwt_access_token>",
    "refresh": "<jwt_refresh_token>",
    "user": { "id": 1, "name": "Admin User", "role": "admin", ... }
  }
}
```

### Token Refresh

```http
POST /api/auth/refresh
{ "refresh": "<refresh_token>" }
```

---

## API Overview

| Domain          | Base Path          | Auth Scope      |
|-----------------|-------------------|-----------------|
| Auth            | `/api/auth/`      | Public / Auth   |
| Users           | `/api/users/`     | Admin (org)     |
| Organizations   | `/api/organizations/` | Super Admin |
| Contacts        | `/api/contacts/`  | Org Member      |
| Inventory       | `/api/inventory/` | Org Member      |
| Activities      | `/api/activities/`| Org Member      |
| Invoices        | `/api/invoices/`  | Org Member      |
| Documents       | `/api/documents/` | Org Member      |
| Subscriptions   | `/api/subscriptions/` | Org Member  |
| Settings        | `/api/settings/`  | Org Member/Admin|
| Audit Log       | `/api/audit-log/` | Org Member      |
| Dashboard       | `/api/dashboard/` | Org Member      |

Full API list: see `popna_API_LIST.md`

---

## Standard Response Format

**Success:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message"
}
```

**Paginated:**
```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "count": 100,
    "next": "http://...",
    "previous": null,
    "page": 1,
    "total_pages": 5
  }
}
```

**Error:**
```json
{
  "success": false,
  "message": "Error description",
  "errors": { "field": ["message"] }
}
```

---

## Production Deployment

```bash
# Set environment
export DJANGO_SETTINGS_MODULE=config.settings.production

# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn
gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 120
```

---

## Key Design Decisions

1. **Unified tables** — `inventory`, `activities`, `invoices`, `documents` use discriminator columns (`catalog_type`, `kind`) and JSONB `payload`/`meta` for kind-specific data.
2. **Custom JWT auth** — `PopnaJWTAuthentication` handles both staff users and customer portal logins from a single token endpoint.
3. **Thin views** — all business logic lives in `services.py` files; views only handle HTTP concerns.
4. **Org scoping** — every org-scoped query filters by `request.user.organization` to prevent data leakage.
5. **MySQL JSONField** — requires MySQL 5.7.8+ or MariaDB 10.2.7+.
