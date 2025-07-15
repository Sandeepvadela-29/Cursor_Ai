# TrueFit Recruitment Platform - Quick Setup Guide

## Prerequisites

- Python 3.8+ installed
- PostgreSQL 12+ installed and running
- Redis 6+ installed and running
- Git installed

## Quick Start (5 minutes)

### 1. Clone and Setup Virtual Environment
```bash
git clone <repository-url>
cd truefit-recruitment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Create PostgreSQL database
createdb truefit_db

# Set environment variables (minimum required)
export SECRET_KEY="your-super-secret-key-here-change-this"
export DATABASE_URL="postgresql://username:password@localhost/truefit_db"

# Or copy and edit .env file
cp .env.example .env
# Edit .env file with your database credentials
```

### 3. Initialize Database
```bash
alembic upgrade head
```

### 4. Run the Application
```bash
uvicorn main:app --reload
```

### 5. Test the Application
Open your browser and go to:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Email Configuration (Optional)

For email functionality (verification, password reset):

1. Enable 2FA on your Gmail account
2. Generate an App Password
3. Update `.env` file:
```env
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py -v
```

## Quick API Test

### Register a Candidate
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register/candidate" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "candidate@example.com",
    "password": "TestPass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "candidate@example.com",
    "password": "TestPass123!"
  }'
```

## Docker Setup (Alternative)

```bash
# Build and run with Docker
docker build -t truefit-api .
docker run -p 8000:8000 --env-file .env truefit-api
```

## Common Issues

### Database Connection Error
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify database exists: `psql -l`
- Check connection string in `.env`

### Import Errors
- Ensure virtual environment is activated
- Check all dependencies installed: `pip install -r requirements.txt`

### Email Not Sending
- Verify SMTP settings in `.env`
- Check Gmail App Password is correct
- Ensure 2FA is enabled on Gmail account

## Next Steps

1. Explore the API documentation at `/docs`
2. Run the test suite to ensure everything works
3. Check the main README.md for detailed documentation
4. Start developing the next module (Profile Management)

## Development Workflow

1. Create a new branch for your feature
2. Make your changes
3. Write tests for new functionality
4. Run tests: `pytest`
5. Check code style: `black app/` and `flake8 app/`
6. Commit and push changes
7. Create a pull request

## Support

If you encounter issues:
1. Check the logs for error messages
2. Verify all prerequisites are installed
3. Review the detailed README.md
4. Check the GitHub issues for similar problems

---

🎉 **Congratulations!** You now have a fully functional authentication system for the TrueFit Recruitment Platform!