# KIKI Authentication Service

OAuth2/JWT authentication service for KIKI Agent™ platform.

## Features

- ✅ User registration with validation
- ✅ OAuth2 password flow login
- ✅ JWT access tokens (30 min expiry)
- ✅ JWT refresh tokens (7 day expiry)
- ✅ Token refresh endpoint
- ✅ Password change
- ✅ User management (admin only)
- ✅ Audit logging
- ✅ Password strength requirements
- ✅ BCrypt password hashing

## API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login (returns tokens) |
| POST | `/api/auth/refresh` | Refresh access token |
| GET | `/healthz` | Health check |

### Protected Endpoints (Requires Auth)

| Method | Endpoint | Description | Auth Level |
|--------|----------|-------------|------------|
| GET | `/api/auth/me` | Get current user | User |
| POST | `/api/auth/change-password` | Change password | User |
| GET | `/api/auth/users` | List all users | Admin |
| DELETE | `/api/auth/users/{user_id}` | Delete user | Admin |

## Quick Start

### 1. Local Development

```bash
# Install dependencies
cd services/auth
pip install -r requirements.txt

# Set environment variables
export KIKI_JWT_SECRET="your-secret-key-min-32-chars"
export KIKI_DATABASE_URL="sqlite:///./kiki_campaigns.db"

# Run server
python app/main.py
```

Server runs on http://localhost:8030

### 2. Docker

```bash
docker-compose up auth
```

### 3. Test Authentication

```bash
# Register user
curl -X POST http://localhost:8030/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "full_name": "John Doe"
  }'

# Login
curl -X POST http://localhost:8030/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=johndoe&password=SecurePass123"

# Get current user (use access_token from login)
curl -X GET http://localhost:8030/api/auth/me \
  -H "Authorization: Bearer <access_token>"
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `KIKI_JWT_SECRET` | **REQUIRED** JWT signing secret (32+ chars) | (none) |
| `KIKI_DATABASE_URL` | Database connection string | `sqlite:///./kiki_campaigns.db` |
| `KIKI_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `30` |
| `KIKI_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | `7` |
| `KIKI_ENV` | Environment (development/production) | `development` |

## Password Requirements

- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit
- No maximum length

## Security Features

### Password Hashing
- BCrypt with automatic salt generation
- Cost factor: 12 (configurable via passlib)

### Token Security
- JWT with HS256 algorithm
- Access tokens: 30 minutes (short-lived)
- Refresh tokens: 7 days (can be revoked)
- Token type validation (access vs refresh)

### Audit Logging
All authentication events logged:
- User registration
- Login attempts
- Password changes
- User deletions (soft delete)

## Integration with Other Services

### Protecting API Endpoints

```python
from fastapi import Depends
from shared.auth_middleware import get_current_user, get_current_admin_user
from shared.models import UserModel

@app.get("/api/campaigns")
def list_campaigns(user: UserModel = Depends(get_current_user)):
    """Protected endpoint - requires authentication"""
    return get_user_campaigns(user.user_id)

@app.delete("/api/campaigns/{id}")
def delete_campaign(id: str, admin: UserModel = Depends(get_current_admin_user)):
    """Admin-only endpoint"""
    return delete_campaign_by_id(id)
```

### Optional Authentication

```python
from shared.auth_middleware import get_optional_user
from typing import Optional

@app.get("/api/public-campaigns")
def list_campaigns(user: Optional[UserModel] = Depends(get_optional_user)):
    """Works with or without authentication"""
    if user:
        return get_user_campaigns(user.user_id)
    else:
        return get_public_campaigns()
```

## Production Deployment

### ⚠️ Critical Security Checklist

- [ ] Set `KIKI_JWT_SECRET` to random 32+ character string
- [ ] Use PostgreSQL (not SQLite) in production
- [ ] Enable HTTPS/TLS for all endpoints
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable audit log monitoring
- [ ] Implement token revocation (Redis)
- [ ] Add MFA/2FA (future enhancement)

### Generate Secure JWT Secret

```bash
# Generate 64-character random secret
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Set as environment variable
export KIKI_JWT_SECRET="<generated-secret>"
```

## Architecture

```
┌─────────────────┐
│   Client App    │
│  (Dashboard)    │
└────────┬────────┘
         │
         │ POST /api/auth/login
         │ { username, password }
         ▼
┌─────────────────┐
│  Auth Service   │
│   (Port 8030)   │
├─────────────────┤
│ • Verify creds  │
│ • Generate JWT  │
│ • Audit log     │
└────────┬────────┘
         │
         │ Returns tokens
         │ { access_token, refresh_token }
         ▼
┌─────────────────┐
│   Client App    │
│  Stores tokens  │
└────────┬────────┘
         │
         │ GET /api/campaigns
         │ Authorization: Bearer <token>
         ▼
┌─────────────────┐
│ SyncValue API   │
│   (Port 8020)   │
├─────────────────┤
│ • Verify JWT    │
│ • Get user_id   │
│ • Return data   │
└─────────────────┘
```

## Troubleshooting

### "Invalid token" error
- Check token hasn't expired
- Verify JWT secret matches across services
- Ensure token type is correct (access vs refresh)

### "Username already registered"
- Username must be unique
- Try different username

### "Incorrect username or password"
- Check username/email spelling
- Verify password is correct
- Account may be deactivated (check with admin)

### Production: "Using default JWT secret"
- Set `KIKI_JWT_SECRET` environment variable
- Secret must be 32+ characters
- Never commit secrets to git

## Testing

```bash
# Run tests
pytest services/auth/tests/

# Test coverage
pytest --cov=services/auth/app services/auth/tests/
```

## Support

For issues or questions:
- See `/docs/API_REFERENCE.md` for full API documentation
- Check `/docs/ARCHITECTURE.md` for system architecture
- Review audit logs in database: `SELECT * FROM audit_logs WHERE event_type LIKE 'user.%';`
