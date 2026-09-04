# CRM & Customer Support Management System

A FastAPI-based backend for managing customers, support tickets, ticket assignments, comments, attachments, notifications, ticket history, SLA operations, dashboards, reports, and audit logs.

## Project Overview

The CRM & Customer Support Management System provides a centralized backend for customer support operations.

Customers can raise and track support tickets. Support Agents can manage, assign, update, resolve, and close tickets. Administrators can manage users, customers, categories, support operations, reports, SLA-related operations, notifications, and audit information.

## Key Features

- JWT-based authentication
- Role-based access control
- Admin, Support Agent, and Customer roles
- Customer management
- User management
- Ticket management
- Ticket assignment and reassignment
- Ticket status workflow
- Ticket priority management
- Ticket categories
- Ticket comments
- Ticket attachments
- Ticket history tracking
- In-app notifications
- Audit logging
- SLA-related operations
- Dashboard APIs
- Reporting APIs
- PostgreSQL database
- SQLAlchemy ORM
- Alembic migrations
- Swagger / OpenAPI documentation
- Postman API testing

## User Roles

### Admin

- Manage users
- Manage customers
- Manage categories
- Manage and monitor tickets
- Assign and reassign tickets
- Access dashboards and reports
- Manage support operations

### Support Agent

- View tickets
- Manage assigned tickets
- Update ticket status and priority
- Add comments
- Resolve and close tickets
- Work with customer support requests

### Customer

- Create support tickets
- View own tickets
- Track ticket status
- Add comments where permitted
- Upload ticket attachments where permitted
- Receive notifications

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | REST API framework |
| PostgreSQL | Relational database |
| SQLAlchemy | ORM |
| Pydantic | Request and response validation |
| JWT | Authentication |
| Alembic | Database migrations |
| Uvicorn | ASGI application server |
| Swagger UI / OpenAPI | API documentation and testing |
| Postman | API testing |

# Project Structure

```text
CRM & Customer Support Management System/
│
├── .venv/                              # Python virtual environment
│   └── ...
│
├── alembic/                            # Database migration package
│   ├── versions/                       # Migration revision files
│   │   └── ...
│   ├── env.py                          # Alembic environment configuration
│   └── script.py.mako                  # Migration file template
│
├── app/                                # Main application package
│   │
│   ├── __init__.py                     # App package initializer
│   │
│   ├── auth.py                          # Authentication dependencies / JWT helpers
│   ├── database.py                      # Database engine, session and configuration
│   ├── main.py                          # FastAPI application entry point
│   ├── models.py                        # SQLAlchemy database models
│   └── schemas.py                       # Pydantic request/response schemas
│   │
│   ├── repositories/                    # Database access layer
│   │   ├── __init__.py
│   │   ├── attachment_repository.py     # Attachment database operations
│   │   ├── audit_repository.py          # Audit log database operations
│   │   ├── category_repository.py      # Category database operations
│   │   ├── comment_repository.py       # Comment database operations
│   │   ├── customer_repository.py      # Customer database operations
│   │   ├── notification_repository.py  # Notification database operations
│   │   ├── ticket_history_repository.py# Ticket history database operations
│   │   ├── ticket_repository.py        # Ticket database operations
│   │   └── user_repository.py           # User database operations
│   │
│   ├── routers/                         # API route layer
│   │   ├── __init__.py
│   │   ├── attachments.py               # Ticket attachment endpoints
│   │   ├── audit_logs.py                # Audit log endpoints
│   │   ├── auth.py                      # Signup / login endpoints
│   │   ├── categories.py                # Category endpoints
│   │   ├── comments.py                  # Ticket comment endpoints
│   │   ├── customers.py                 # Customer endpoints
│   │   ├── dashboard.py                 # Dashboard endpoints
│   │   ├── notifications.py             # Notification endpoints
│   │   ├── reports.py                   # Reporting endpoints
│   │   ├── sla.py                       # SLA endpoints
│   │   ├── ticket_history.py            # Ticket history endpoints
│   │   ├── tickets.py                   # Ticket endpoints
│   │   └── users.py                     # User management endpoints
│   │
│   └── services/                        # Business logic layer
│       ├── __init__.py
│       ├── attachment_service.py        # Attachment business logic
│       ├── audit_service.py             # Audit logging logic
│       ├── auth_service.py              # Authentication and JWT logic
│       ├── category_service.py          # Category business logic
│       ├── comment_service.py           # Comment business logic
│       ├── dashboard_service.py         # Dashboard aggregation logic
│       ├── notification_service.py      # Notification business logic
│       ├── sla_service.py               # SLA business logic
│       ├── ticket_history_service.py    # Ticket history logic
│       └── ticket_service.py            # Ticket workflow and business logic
│
├── uploads/                             # Stored ticket attachment files
│   └── ...
│
├── .env                                 # Environment variables / secrets
├── .gitignore                           # Git ignore rules
├── alembic.ini                          # Alembic configuration
├── requirements.txt                     # Python dependencies
├── Architecture Diagram.png             # System architecture diagram
└── Database Schema Diagram.png          # Database schema diagram
```

> **Note:** `.venv/`, `__pycache__/`, and generated migration files under `alembic/versions/` are shown for clarity but should normally not be committed to Git. Uploaded attachment files under `uploads/` should also be handled according to the project's storage policy.

## Architecture

The application follows a layered architecture:

```text
Client
  |
  | HTTP / JSON
  v
FastAPI Routers
  |
  v
Authentication / Authorization
  |
  v
Service Layer
  |
  v
Repository Layer
  |
  v
SQLAlchemy ORM
  |
  v
PostgreSQL
```

Supporting components:

```text
                    +----------------------+
                    |       Clients        |
                    | Customer / Agent /   |
                    | Admin                |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |     FastAPI API      |
                    |       Routers        |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |   Service Layer      |
                    | Business Logic       |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Repository Layer     |
                    | Database Operations  |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |    PostgreSQL        |
                    +----------------------+

       +----------------+    +----------------------+
       | File Storage   |    | Notification Service |
       | Ticket uploads |    | In-app notifications |
       +----------------+    +----------------------+
```

## Database Schema

Main entities:

- `users`
- `customers`
- `categories`
- `tickets`
- `ticket_comments`
- `ticket_attachments`
- `notifications`
- Ticket history / audit information

Main relationships:

```text
User       1 ───────── N Tickets
Customer   1 ───────── N Tickets
Category   1 ───────── N Tickets
Ticket     1 ───────── N Ticket Comments
Ticket     1 ───────── N Ticket Attachments
User       1 ───────── N Notifications
```

## Ticket Workflow

The ticket workflow is controlled by application business rules:

```text
OPEN
  |
  v
IN_PROGRESS
  |
  v
RESOLVED
  |
  v
CLOSED
```

Cancellation is also supported where allowed by the application's transition rules.

### Priority Levels

- Low
- Medium
- High
- Critical

Critical tickets can generate notifications for the relevant users.

## Authentication

JWT tokens are used to protect secured endpoints.

```text
Login
  |
  v
POST /auth/login
  |
  v
Validate credentials
  |
  v
Generate JWT
  |
  v
Authorization: Bearer <token>
```

Passwords are stored as hashes rather than plain text.

## API Modules

The API is organized by router modules:

| Router | Responsibility |
|---|---|
| `auth.py` | Signup and login |
| `users.py` | User management |
| `customers.py` | Customer management |
| `categories.py` | Ticket categories |
| `tickets.py` | Ticket creation and workflow |
| `comments.py` | Ticket comments |
| `attachments.py` | Ticket file uploads |
| `notifications.py` | User notifications |
| `ticket_history.py` | Ticket history |
| `audit_logs.py` | Audit information |
| `dashboard.py` | Dashboard data |
| `reports.py` | Reports and analytics |
| `sla.py` | SLA-related operations |

## Ticket Endpoints

Core ticket operations include:

| Method | Endpoint | Description |
|---|---|---|
| POST | `/tickets/` | Create ticket |
| GET | `/tickets/` | Get tickets |
| GET | `/tickets/{id}` | Get ticket by ID |
| PUT | `/tickets/{id}` | Update ticket |
| PUT | `/tickets/{id}/assign` | Assign ticket |
| PUT | `/tickets/{id}/reassign` | Reassign ticket |
| PUT | `/tickets/{id}/resolve` | Resolve ticket |
| PUT | `/tickets/{id}/close` | Close ticket |
| PUT | `/tickets/{id}/cancel` | Cancel ticket |

Other resources are exposed through their corresponding router modules.

## Project Setup

### 1. Open the project

```powershell
cd "CRM & Customer Support Management System"
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the virtual environment

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

## Environment Configuration

Create or update `.env` with the required configuration.

Example:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5433/crm_support_db
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Do not commit real passwords, secret keys, or other credentials.

## Database Migration

Run the existing migrations:

```powershell
python -m alembic upgrade head
```

Create a new migration after changing SQLAlchemy models:

```powershell
python -m alembic revision --autogenerate -m "describe change"
```

Apply the migration:

```powershell
python -m alembic upgrade head
```

## Run the Application

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## API Documentation

Swagger / OpenAPI documentation is available from the application.

Open:

```text
http://127.0.0.1:8000/
```

Swagger can be used to:

- View available endpoints
- Inspect schemas
- Authorize with a JWT token
- Send requests
- Verify API responses

## Postman Testing

Recommended flow:

```text
Signup
   ↓
Login
   ↓
Copy JWT token
   ↓
Authorize protected requests
   ↓
Create customer
   ↓
Create category
   ↓
Create ticket
   ↓
Assign / Reassign ticket
   ↓
Update ticket
   ↓
Resolve / Close ticket
   ↓
Verify comments / attachments / notifications / history
```

## Error Handling

The API uses FastAPI HTTP exceptions and standard HTTP status codes.

Common responses include:

```text
200 OK
201 Created
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
422 Unprocessable Entity
500 Internal Server Error
```

## Security

- JWT authentication protects secured API operations.
- Role-based authorization controls access to resources.
- Passwords are hashed before storage.
- Secrets are loaded from environment configuration.
- File uploads are handled through the attachment module.
- Audit logging can capture important system activities.

## Development Notes

The codebase is separated into:

```text
Routers      → API endpoints
Services     → Business rules
Repositories → Database access
Models       → SQLAlchemy entities
Schemas      → Pydantic validation
```

This separation makes the application easier to maintain, test, and extend.

## Future Enhancements

Potential improvements include:

- Email notifications
- Background task processing with a queue
- Redis caching
- Advanced search and filtering
- SLA escalation automation
- Rich reporting and analytics
- Cloud object storage for attachments
- Automated test suite
- Docker support
- CI/CD integration

## Conclusion

The CRM & Customer Support Management System is a modular FastAPI backend designed for customer support operations. It combines JWT authentication, role-based authorization, PostgreSQL persistence, ticket workflows, comments, attachments, notifications, ticket history, SLA operations, dashboards, reports, and audit logging in a maintainable layered architecture.
