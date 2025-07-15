# TrueFit Recruitment Platform - Authentication Module

A comprehensive, production-ready authentication system for the TrueFit recruitment platform that focuses on perfect employer-employee matching based on values, culture, and comprehensive compatibility.

## 🚀 Features

### Authentication & Security
- **JWT-based authentication** with access and refresh tokens
- **Email verification** with secure token-based verification
- **Password reset** functionality with time-limited tokens
- **Role-based access control** (Candidates, Employers, Admins)
- **Account lockout** protection against brute force attacks
- **Rate limiting** to prevent abuse
- **Security headers** and CORS protection
- **MFA support** (ready for implementation)

### User Management
- **Multi-role user system** (Candidates and Employers)
- **Comprehensive user profiles** with extensive fields
- **Profile completeness tracking** with missing field indicators
- **Account status management** (Active, Pending, Suspended, Deactivated)
- **Privacy controls** for candidate profiles

### Candidate Features
- **Professional profile** with headline, summary, and experience
- **Skills and certifications** tracking
- **Education history** management
- **Career preferences** (salary, job type, work arrangement)
- **Personality and values assessment** for better matching
- **Document management** (resume, cover letter, portfolio)
- **Profile visibility controls** (public, private, employers only)

### Employer Features
- **Company profiles** with detailed information
- **Company culture and values** description
- **Benefits and perks** management
- **Diversity and inclusion** initiatives
- **Hiring process** documentation
- **Company verification** system
- **Subscription management** (Free, Basic, Premium, Enterprise)

### Technical Features
- **RESTful API** with comprehensive documentation
- **Database migrations** with Alembic
- **Background task processing** with Celery (ready)
- **Redis caching** for sessions and rate limiting
- **Email service** with HTML templates
- **Prometheus metrics** for monitoring
- **Comprehensive test suite** with pytest
- **Production-ready** with Docker support

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Cache**: Redis
- **Email**: SMTP (configurable)
- **Authentication**: JWT with bcrypt
- **Testing**: pytest with fixtures
- **Documentation**: Automatic OpenAPI/Swagger
- **Monitoring**: Prometheus metrics
- **Deployment**: Docker-ready

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis
- SMTP server (for email)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd truefit-platform
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

5. **Initialize database**
   ```bash
   alembic upgrade head
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## 📖 API Documentation

Once the application is running, you can access:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 🔐 Authentication Flow

### User Registration
1. POST `/api/v1/auth/register` - Register new user
2. Email verification sent automatically
3. GET `/api/v1/auth/verify-email` - Verify email with token
4. Account activated and ready to use

### User Login
1. POST `/api/v1/auth/login` - Login with email/password
2. Receive access token (30 min) and refresh token (7 days)
3. Use access token in Authorization header: `Bearer <token>`

### Token Refresh
1. POST `/api/v1/auth/refresh` - Refresh access token
2. Receive new access token

### Password Reset
1. POST `/api/v1/auth/password-reset` - Request reset
2. Email sent with reset link
3. POST `/api/v1/auth/password-reset/confirm` - Set new password

## 📋 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/logout` - Logout user
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/verify-email` - Verify email
- `POST /api/v1/auth/resend-verification` - Resend verification email
- `POST /api/v1/auth/password-reset` - Request password reset
- `POST /api/v1/auth/password-reset/confirm` - Confirm password reset
- `GET /api/v1/auth/me` - Get current user info

### User Management
- `GET /api/v1/users/profile` - Get user profile
- `PUT /api/v1/users/profile` - Update user profile
- `POST /api/v1/users/change-password` - Change password
- `POST /api/v1/users/deactivate` - Deactivate account
- `GET /api/v1/users/account-status` - Get account status

### Candidate Profiles
- `GET /api/v1/candidates/profile` - Get candidate profile
- `POST /api/v1/candidates/profile` - Create candidate profile
- `PUT /api/v1/candidates/profile` - Update candidate profile
- `GET /api/v1/candidates/profile/visibility` - Get visibility settings
- `PUT /api/v1/candidates/profile/visibility` - Update visibility settings
- `GET /api/v1/candidates/profile/completeness` - Get profile completeness

### Employer Profiles
- `GET /api/v1/employers/profile` - Get employer profile
- `POST /api/v1/employers/profile` - Create employer profile
- `PUT /api/v1/employers/profile` - Update employer profile
- `GET /api/v1/employers/profile/verification` - Get verification status
- `POST /api/v1/employers/profile/verification/request` - Request verification
- `GET /api/v1/employers/profile/completeness` - Get profile completeness
- `GET /api/v1/employers/subscription` - Get subscription info

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::TestUserRegistration::test_register_candidate_success
```

### Test Categories
- **Authentication tests**: Registration, login, token management
- **User management tests**: Profile updates, password changes
- **Candidate profile tests**: Profile creation, visibility settings
- **Employer profile tests**: Company profiles, verification
- **Security tests**: Rate limiting, permissions

## 🔧 Configuration

### Environment Variables

Required environment variables (see `.env.example`):

```env
# Security
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379/0

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
```

### Database Migration

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 📊 Monitoring

The application includes Prometheus metrics:

- **HTTP requests**: Total requests, duration, status codes
- **Active connections**: Current active connections
- **Authentication metrics**: Login attempts, failures
- **Custom metrics**: User registrations, profile completeness

Access metrics at: `http://localhost:8000/metrics`

## 🔒 Security Features

### Password Security
- **bcrypt hashing** with salt
- **Password strength validation**
- **Password history** (extensible)

### Account Security
- **Account lockout** after failed attempts
- **Email verification** required
- **Session management** with Redis
- **Token expiration** and refresh

### API Security
- **Rate limiting** by IP and user
- **CORS protection**
- **Security headers**
- **Request validation**

## 📝 Development

### Code Quality
- **Black** code formatting
- **Flake8** linting
- **Pre-commit hooks** (configurable)
- **Type hints** throughout codebase

### Architecture
- **Clean architecture** with separation of concerns
- **Dependency injection** with FastAPI
- **Service layer** for business logic
- **Repository pattern** ready for implementation

### Adding New Features
1. Create models in `app/models/`
2. Add schemas in `app/schemas/`
3. Implement services in `app/services/`
4. Create endpoints in `app/api/v1/endpoints/`
5. Add tests in `tests/`

## 🐳 Docker Deployment

```bash
# Build image
docker build -t truefit-platform .

# Run with docker-compose
docker-compose up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Next Steps

This authentication module is the foundation for the complete TrueFit platform. Next modules to implement:

1. **Job Management System** - Job posting, search, and applications
2. **Matching Algorithm** - AI-powered compatibility matching
3. **Messaging System** - Real-time communication
4. **Interview Scheduling** - Calendar integration
5. **Analytics Dashboard** - User behavior and metrics
6. **Payment System** - Subscription and billing
7. **File Management** - Resume parsing and storage
8. **Notification System** - Email and push notifications

## 🔍 Troubleshooting

### Common Issues

**Database connection errors**:
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Ensure database exists

**Email not sending**:
- Check SMTP configuration
- Verify email credentials
- Check firewall/network settings

**Redis connection errors**:
- Ensure Redis is running
- Check REDIS_URL configuration
- Verify Redis is accessible

**Test failures**:
- Check test database configuration
- Ensure test dependencies are installed
- Run tests with `-v` for verbose output

For more help, check the logs or create an issue in the repository.

---

**Built with ❤️ for better recruitment experiences**