# AgriCapital API (Prueba técnica) 🚀

The **AgriCapital API** is a FastAPI-based backend system specifically designed for managing agricultural credit in Colombia. 🇨🇴 It handles the full lifecycle of agricultural lending applications, from submission and risk assessment to approval and rejection workflows. 🚜

---

## Project Overview

This platform streamlines agricultural credit management, providing a robust and efficient system for financial institutions to process and track loan applications tailored for the agricultural sector. 🌾💰

---

## Core Architecture

### Technology Stack 🛠️

* **Framework**: FastAPI 0.115.12 (with Starlette 0.46.2)
* **Database**: PostgreSQL (with SQLModel 0.0.24 and SQLAlchemy 2.0.41) 🐘
* **Server**: Uvicorn 0.34.2 (development), Gunicorn 23.0.0 (production)
* **Real-time Communication**: WebSockets 15.0.1 ⚡
* **Email**: FastAPI-Mail 1.5.0 (with aiosmtplib 3.0.2) 📧
* **Security**: bcrypt 4.3.0, python-jose 3.5.0, secure 1.0.1 🔒

### Application Structure 🏗️

The application boasts a modular architecture with domain-separated routers for clear organization and scalability:

* **Request Management**: Handles all credit application processing. 📝
* **Client Management**: Manages agricultural client profiles. 🧑‍🌾
* **Notification System**: Powers real-time and email notifications. 🔔
* **WebSocket Communication**: Enables live updates. 📡

---

## Key Features

### Credit Request Management ✅

The `RequestService` class is central to the business logic, orchestrating:

* **Request Creation**: Validates client profiles and prevents duplicate submissions.
* **Risk Assessment**: Automatically calculates risk using agricultural-specific factors. 📊
* **Approval/Rejection Workflows**: Manages status updates and analyst assignments.
* **Email Notifications**: Sends professional HTML emails for various request states. ✉️
* **Real-time Updates**: Delivers WebSocket notifications for instant client feedback. 🚀

### Agricultural Risk Assessment ⚖️

A sophisticated risk calculation model considers multiple factors crucial for agricultural lending:

* Credit history (25% weight)
* Payment capacity (20% weight)
* Debt burden (15% weight)
* Agricultural profile (12% weight)
* Demographics (8% weight)
* Collateral (10% weight)
* Loan characteristics (10% weight)

### Client Profile System 🧑‍💻

Manages agricultural-specific client data, including:

* Annual income and debt-to-income ratio
* Years of agricultural experience
* Farm size in hectares
* Agricultural insurance status
* Internal credit history scoring

### Communication Systems 🗣️

A dual-channel notification system ensures comprehensive communication:

* **Email Templates**: Professional HTML emails with Colombian peso formatting. 💲
* **WebSocket Notifications**: Real-time updates for credit request status changes.

---

## API Endpoints

### Credit Requests 🌐

* `POST /requests/` - Create a new credit request.
* `GET /requests/paginated-list` - Retrieve filtered and paginated credit requests.
* `GET /requests/{id}` - Get a specific credit request by ID.
* `PATCH /requests/{id}` - Update an existing credit request.
* `PATCH /requests/{id}/approve` - Approve a credit request. 👍
* `PATCH /requests/{id}/reject` - Reject a credit request. 👎

### Request Data Model 📝

A comprehensive request schema covers:

* Client and credit type references
* Financial details (amount, term, interest rate)
* Risk assessment results
* Approval/rejection tracking
* Agricultural context (collateral, purpose)

---

## Security & Configuration

### Middleware Stack 🛡️

* **CORS**: Handles environment-aware origin management.
* **Security Headers**: Provides comprehensive protection, including HSTS, XSS protection, and frame options.

### Environment Configuration ⚙️

The project uses `python-dotenv` for managing environment variables. Key variables include:

* Database connection settings
* JWT configuration
* CORS origins
* Email service configuration

---

## Development & Testing

### Dependencies 📦

* **Testing**: pytest 8.3.5 (with pytest-asyncio 1.0.0) 🧪
* **Code Quality**: pre-commit 4.2.0 ✨
* **Database Migrations**: Alembic 1.16.1 ⬆️

### Database Models 📊

SQLModel is used for type-safe database operations, with entities for:

* Request management with full lifecycle tracking.
* Client profiles with agricultural-specific fields.
* Notification system for user communications.

---

## Notes 📝

This platform is specifically tailored for the **Colombian agricultural lending market**. It features peso currency formatting, Spanish language support, and agricultural industry-specific risk factors. The system prioritizes real-time communication and comprehensive email notifications to keep all stakeholders informed throughout the credit application process. 🤝

---

<details>
<summary>Environments 🔒</summary>
  
```bash
# JWT
# JWT_SECRET_KEY: A highly secure, randomly generated secret key used for signing and verifying JWTs. Keep this absolutely confidential.
JWT_SECRET_KEY="your_jwt_secret_key_here_please_generate_a_strong_one_for_production_like_this_long_string_of_random_characters"
# JWT_ALGORITHM: The cryptographic algorithm used for signing the JWT. HS256 (HMAC SHA-256) is a common and secure choice.
JWT_ALGORITHM="HS256"
# JWT_AUDIENCE: Defines the intended recipient of the JWT. This helps prevent the token from being used by unintended parties.
JWT_AUDIENCE="authenticated"

# DB
# DATABASE_URL: The complete connection string for your PostgreSQL database. This often includes all necessary details like user, password, host, port, and database name.
DATABASE_URL="postgresql://user:password@host:port/database"
# DATABASE_HOST: The hostname or IP address of your database server.
DATABASE_HOST="your_database_host.example.com"
# DATABASE_PORT: The port number on which the database server is listening.
DATABASE_PORT="5432"
# DATABASE_NAME: The name of the database to connect to.
DATABASE_NAME="your_database_name"
# DATABASE_USER: The username for accessing the database.
DATABASE_USER="your_database_user"
# DATABASE_PASSWORD: The password for the database user.
DATABASE_PASSWORD="your_database_password"

# MAIL
# MAIL_HOST: The hostname of the SMTP (Simple Mail Transfer Protocol) server.
MAIL_HOST="smtp.yourmailprovider.com"
# MAIL_PORT: The port number for connecting to the SMTP server. 587 is commonly used for TLS/STARTTLS.
MAIL_PORT="587"
# MAIL_SECURE: A boolean indicating whether to use a secure connection (TLS/SSL). Set to true for secure connections.
MAIL_SECURE="true"
# MAIL_USER: The email address used to authenticate with the SMTP server.
MAIL_USER="your_email@example.com"
# MAIL_PASSWORD: The password or app-specific password for the email account used for sending. Be extremely cautious with this value.
MAIL_PASSWORD="your_email_app_password"
# MAIL_SENDER: The display name and email address that will appear as the sender of the emails.
MAIL_SENDER="YourAppName<noreply@yourdomain.com>"

# APP
# ENVIRONMENT: Specifies the current operating environment of the application (e.g., development, production, testing). This can influence logging, error handling, and other behaviors.
ENVIRONMENT="development"
# FRONTEND_URL: The URL of the frontend application. Used for CORS settings or generating links back to the frontend.
FRONTEND_URL="https://your-frontend-app.vercel.app"
# BACKEND_URL: The base URL of the backend API. Useful for internal redirects or client-side configuration.
BACKEND_URL="http://localhost:8000"
# ALLOWED_METHODS: A comma-separated list of HTTP methods allowed for CORS (Cross-Origin Resource Sharing).
ALLOWED_METHODS="GET,POST,PATCH,DELETE,OPTIONS,HEAD"
# ALLOWED_HEADERS: A comma-separated list of HTTP headers allowed for CORS requests.
ALLOWED_HEADERS="Content-Type,Authorization"
```
</details>

---

## Useful Wiki Pages 📖

---

* [DOCUMENTATION](https://deepwiki.com/JhefersonCh/agricapital-pt-back)

<details>
<summary>Project Commands 💻</summary>

```bash
# Instalación de dependencias
pip install -r requirements.txt

# Ejecutar la aplicación en desarrollo
uvicorn main:app --reload

# Ejecutar la aplicación en producción (usando Gunicorn)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Ejecutar tests
pytest

# Generar una nueva migración de base de datos (después de cambios en modelos)
alembic revision --autogenerate -m "Descripción de la migración"

# Aplicar migraciones a la base de datos
alembic upgrade head

# Configurar pre-commit hooks
pre-commit install
