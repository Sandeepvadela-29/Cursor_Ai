# TrueFit Recruitment Platform

A comprehensive recruitment platform that finds the **perfect match between employers and employees** based on comprehensive compatibility, not just skills and pay, but also attitudes, worldviews, character, and cultural alignment.

## 🌟 Vision

Build a recruitment platform that helps companies and job seekers connect meaningfully by including **values, integrity, personality compatibility**, and **cultural alignment** in the matching process — not just resumes.

## 🚀 Features

### ✅ Completed (Authentication Module)
- **User Registration & Authentication**
  - Separate candidate and employer registration
  - JWT-based authentication with refresh tokens
  - Email verification with HTML templates
  - Password reset functionality
  - Strong password validation
  - Account lockout after failed attempts
  - Role-based access control (RBAC)

### 🔄 In Development
- **Job Posting and Search Engine**
- **Persona Assessment Engine**
- **Intelligent Matching Algorithm**
- **Profile Management**
- **Application Tracking System**
- **Messaging & Interview System**
- **Company Reviews & Insights**
- **Salary Tools & Research**
- **Admin Dashboard**
- **Analytics Module**

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis
- **Authentication**: JWT with OAuth2
- **Email**: FastMail with HTML templates
- **Migration**: Alembic
- **Testing**: Pytest
- **Documentation**: Automatic OpenAPI/Swagger

### Frontend (Planned)
- **Framework**: React.js with TypeScript
- **State Management**: Redux Toolkit
- **UI Library**: Tailwind CSS
- **PWA**: Progressive Web App support

### DevOps
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: Structured logging with Loguru

## 📋 Requirements

- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Email server (SMTP)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/truefit-recruitment.git
cd truefit-recruitment
```

### 2. Set Up Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

### 3. Configure Environment Variables
Edit `.env` file with your settings:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost/truefit_db

# JWT Secret (generate a secure key)
SECRET_KEY=your-super-secret-key-here

# Email Configuration
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
```

### 4. Set Up Database
```bash
# Create database
createdb truefit_db

# Run migrations
alembic upgrade head
```

### 5. Run the Application
```bash
# Development server
uvicorn main:app --reload

# Production server
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 6. Access the Application
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run Tests with Coverage
```bash
pytest --cov=app tests/
```

### Run Specific Test Module
```bash
pytest tests/test_auth.py -v
```

## 📖 API Documentation

### Authentication Endpoints

#### Register Candidate
```http
POST /api/v1/auth/register/candidate
Content-Type: application/json

{
  "email": "candidate@example.com",
  "password": "StrongPass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

#### Register Employer
```http
POST /api/v1/auth/register/employer
Content-Type: application/json

{
  "email": "employer@company.com",
  "password": "StrongPass123!",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "+1987654321",
  "company_name": "Tech Corp Inc."
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "StrongPass123!"
}
```

#### Verify Email
```http
POST /api/v1/auth/verify-email
Content-Type: application/json

{
  "token": "verification-token-here"
}
```

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

### Error Responses
All endpoints return consistent error responses:
```json
{
  "error": true,
  "message": "Error description",
  "status_code": 400
}
```

## 🔒 Security Features

### Password Security
- Minimum 8 characters
- Must contain uppercase, lowercase, digit, and special character
- Bcrypt hashing with salt
- Password history (planned)

### Account Security
- Account lockout after 5 failed attempts
- 30-minute lockout duration
- Login attempt tracking
- IP-based monitoring

### Token Security
- JWT with RS256 algorithm
- 30-minute access token expiry
- 7-day refresh token expiry
- Token blacklisting (planned)

### API Security
- CORS configuration
- Rate limiting (planned)
- Request validation
- SQL injection prevention
- XSS protection

## 🗃️ Database Schema

### Users Table
- Basic user information
- Authentication credentials
- Security tracking
- Verification status

### Candidate Profiles
- Professional information
- Skills and qualifications
- Preferences and availability
- Personality assessments

### Employer Profiles
- Company information
- Culture and values
- Benefits and perks
- Verification status

## 📁 Project Structure

```
truefit-recruitment/
├── app/
│   ├── api/
│   │   ├── dependencies.py      # FastAPI dependencies
│   │   └── v1/
│   │       ├── auth.py          # Authentication endpoints
│   │       └── router.py        # API router
│   ├── core/
│   │   ├── config.py           # Configuration settings
│   │   ├── database.py         # Database connection
│   │   └── security.py         # Security utilities
│   ├── models/
│   │   └── user.py             # User models
│   ├── schemas/
│   │   ├── auth.py             # Authentication schemas
│   │   └── user.py             # User schemas
│   ├── services/
│   │   ├── auth_service.py     # Authentication service
│   │   └── email_service.py    # Email service
│   └── utils/
├── tests/
│   └── test_auth.py            # Authentication tests
├── alembic/                    # Database migrations
├── main.py                     # FastAPI application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── alembic.ini                # Alembic configuration
└── README.md                  # This file
```

## 🚢 Deployment

### Docker Deployment
```bash
# Build image
docker build -t truefit-api .

# Run container
docker run -p 8000:8000 --env-file .env truefit-api
```

### Kubernetes Deployment
```bash
# Apply manifests
kubectl apply -f k8s/
```

### Database Migration
```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Write comprehensive tests
- Document new features
- Update API documentation

## 📊 Monitoring

### Health Checks
- Application health: `/health`
- Database health: `/api/v1/health`
- Detailed metrics: `/metrics` (planned)

### Logging
- Structured JSON logging
- Request/response logging
- Error tracking
- Performance monitoring

## 🔄 Roadmap

### Phase 1: Core Authentication ✅
- [x] User registration and login
- [x] Email verification
- [x] Password reset
- [x] JWT authentication
- [x] Role-based access control

### Phase 2: Profile Management (In Progress)
- [ ] Candidate profile creation
- [ ] Employer profile creation
- [ ] File upload (resume, documents)
- [ ] Profile validation

### Phase 3: Assessment Engine
- [ ] Personality assessment
- [ ] Values assessment
- [ ] Communication style assessment
- [ ] Leadership style assessment

### Phase 4: Job Management
- [ ] Job posting
- [ ] Job search and filtering
- [ ] Application management
- [ ] Interview scheduling

### Phase 5: Matching Algorithm
- [ ] Skill-based matching
- [ ] Culture-based matching
- [ ] Values-based matching
- [ ] Weighted scoring system

### Phase 6: Communication
- [ ] Real-time messaging
- [ ] Video interview integration
- [ ] Email notifications
- [ ] Calendar integration

### Phase 7: Analytics & Insights
- [ ] Matching effectiveness
- [ ] User behavior analytics
- [ ] Performance metrics
- [ ] Reporting dashboard

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Lead Developer**: [Your Name]
- **Backend Developer**: [Team Member]
- **Frontend Developer**: [Team Member]
- **DevOps Engineer**: [Team Member]

## 📞 Support

For support, email support@truefit.com or join our Slack channel.

## 🙏 Acknowledgments

- FastAPI team for the amazing framework
- SQLAlchemy for the robust ORM
- All contributors and testers

---

**TrueFit Recruitment Platform** - Finding the perfect match between employers and employees! 🎯