# Admin User Management Guide

## Overview

The KIKI Agent™ platform includes a comprehensive admin user management system that allows administrators to:

- Create new users with specific roles (user or admin)
- Promote users to admin role
- Demote admins to user role  
- Activate/deactivate user accounts
- View and manage all users in the system

## Bootstrap Problem Solution

The platform solves the "chicken-and-egg" problem of creating the first admin user through **two complementary approaches**:

### Option 1: Migration-Based Admin Creation (Recommended for Production)

The platform automatically creates a default admin user on first deployment using environment variables.

**Setup:**

1. **Set environment variables** before running migrations:
   ```bash
   export KIKI_ADMIN_EMAIL=admin@yourcompany.com
   export KIKI_ADMIN_PASSWORD=YourSecurePassword123
   export KIKI_ADMIN_USERNAME=admin
   ```

2. **Run database migrations:**
   ```bash
   ./db_migrate.sh upgrade
   ```

3. **Admin user is created automatically** with role="admin"

4. **Login** at `http://localhost:8021/login` with your admin credentials

5. **Delete environment variables** after first login for security:
   ```bash
   unset KIKI_ADMIN_EMAIL
   unset KIKI_ADMIN_PASSWORD
   unset KIKI_ADMIN_USERNAME
   ```

**Migration Details:**
- Migration file: `/alembic/versions/20260206_1815_add_default_admin.py`
- Checks if admin already exists (idempotent)
- Only runs if environment variables are set
- Logs success/failure to console

### Option 2: Manual Admin Creation/Promotion

Use the dedicated script to create admin users or promote existing users.

**Create new admin user:**
```bash
# Using the wrapper script
./scripts/create_admin.sh --email admin@example.com --password SecurePass123

# Or directly
python scripts/create_admin.py --email admin@example.com --password SecurePass123 --username admin
```

**Promote existing user to admin:**
```bash
# User registered normally, now needs admin access
./scripts/create_admin.sh --promote user@example.com

# Or directly
python scripts/create_admin.py --promote user@example.com
```

**Script Features:**
- Validates email uniqueness
- Enforces minimum password length (8 characters)
- Auto-generates username from email if not provided
- Handles username conflicts with random suffix
- Provides detailed success/error messages
- Full audit trail in console output

## Admin Features

### Accessing Admin Panel

1. **Login** as an admin user at `http://localhost:8021/login`

2. **Navigate** to Admin Panel:
   - Dashboard → Click "Users" in navigation menu
   - Or directly: `http://localhost:8021/admin/users`

3. **Admin users only** - Regular users will see 403 Forbidden error

### User Management Interface

The admin panel provides:

**User List View:**
- Username, email, full name
- Role badge (User/Admin)
- Status badge (Active/Inactive)
- Creation date
- Action buttons for each user

**Available Actions:**

#### 1. Create New User
- Click "Create User" button
- Fill in user details:
  - Username (required)
  - Email (required)
  - Full Name (optional)
  - Password (required, min 8 chars)
  - Role (user or admin)
- User is created immediately and can login

#### 2. Promote/Demote Users
- **Promote to Admin:** Grants admin role to regular user
- **Demote to User:** Removes admin privileges

#### 3. Activate/Deactivate Accounts
- **Deactivate:** User cannot login (soft delete)
- **Activate:** Re-enable deactivated user

#### 4. View User Details
- Real-time user list with filters
- Sort by creation date (newest first)

## API Endpoints

All admin endpoints require authentication with `role="admin"`.

### List Users
```http
GET /api/auth/users?skip=0&limit=100&role=admin&is_active=true
Authorization: Bearer <admin-token>
```

**Filters:**
- `skip`: Pagination offset (default: 0)
- `limit`: Max results (default: 100)
- `role`: Filter by role ("user" or "admin")
- `is_active`: Filter by status (true/false)

**Response:**
```json
[
  {
    "user_id": "usr_abc123",
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "role": "user",
    "is_active": true,
    "created_at": "2026-02-06T12:00:00Z"
  }
]
```

### Create User (Admin)
```http
POST /api/auth/users/create?role=admin
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "SecurePass123",
  "full_name": "New User"
}
```

**Response:** Created user object

### Update User Role
```http
PATCH /api/auth/users/{user_id}/role?new_role=admin
Authorization: Bearer <admin-token>
```

**Response:**
```json
{
  "message": "User role updated to admin",
  "user_id": "usr_abc123",
  "new_role": "admin"
}
```

### Activate/Deactivate User
```http
PATCH /api/auth/users/{user_id}/activate?active=false
Authorization: Bearer <admin-token>
```

**Response:**
```json
{
  "message": "User deactivated successfully",
  "user_id": "usr_abc123",
  "is_active": false
}
```

### Delete User (Soft Delete)
```http
DELETE /api/auth/users/{user_id}
Authorization: Bearer <admin-token>
```

**Note:** Prevents self-deletion and performs soft delete (deactivation).

## Security Features

### Audit Logging
All admin actions are logged to the `audit_logs` table:

- `user.created_by_admin` - Admin created new user
- `user.role_updated` - Role changed (user ↔ admin)
- `user.activated` / `user.deactivated` - Status changed
- `user.deleted` - User soft-deleted

Each audit log includes:
- Event type
- Timestamp
- Admin user ID (who performed action)
- Target user details
- Old/new values (for updates)

### Role-Based Access Control

**Admin Role Permissions:**
- View all users
- Create users with any role
- Promote/demote users
- Activate/deactivate users
- Access admin dashboard
- View audit logs (coming soon)

**User Role Permissions:**
- View own profile
- Change own password
- Access user dashboard
- Manage own campaigns

### Authentication Requirements

All admin endpoints use `get_current_admin_user()` dependency:

```python
@app.get("/api/auth/users")
def list_users(
    admin: UserModel = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    # Only admins can access this endpoint
    ...
```

Returns 403 Forbidden if:
- User is not authenticated
- User role is not "admin"
- Token is expired/invalid

## Best Practices

### Production Deployment

1. **Create admin via migration** on first deployment
2. **Login immediately** and verify admin access
3. **Delete environment variables** from server
4. **Create additional admins** through UI as needed
5. **Use strong passwords** (12+ characters, mixed case, numbers, symbols)
6. **Rotate admin passwords** every 90 days
7. **Deactivate unused accounts** instead of deleting

### Development Workflow

1. **Use migration** for consistent dev environment setup
2. **Commit .env.example** with placeholder values
3. **Never commit .env** with real credentials
4. **Each developer** sets own admin credentials locally
5. **Test admin features** after any authentication changes

### Security Checklist

- [ ] Admin password is strong (12+ characters)
- [ ] Environment variables deleted after admin creation
- [ ] Only trusted users have admin role
- [ ] Deactivated users cannot access system
- [ ] Audit logs reviewed regularly
- [ ] Admin accounts use unique emails
- [ ] No hardcoded admin credentials in code

## Troubleshooting

### "Admin user already exists" during migration
**Cause:** Migration already ran or email exists in database  
**Solution:** Migration is idempotent, safe to ignore. Use manual script to promote existing user.

### "Access denied. Admin role required."
**Cause:** User doesn't have admin role  
**Solution:** Use `create_admin.py --promote <email>` to grant admin role

### Cannot create first admin user
**Cause:** Environment variables not set  
**Solution:** Set `KIKI_ADMIN_EMAIL` and `KIKI_ADMIN_PASSWORD` before running migrations

### Admin panel shows 403 Forbidden
**Cause:** Not logged in as admin user  
**Solution:** Login with admin credentials at `/login`, verify role in token

### Script error "User with email X already exists"
**Cause:** Email already registered  
**Solution:** Use `--promote` flag instead of creating new user

## Examples

### Scenario 1: Production First Deployment

```bash
# 1. Set admin credentials
export KIKI_ADMIN_EMAIL=admin@production.com
export KIKI_ADMIN_PASSWORD=$(openssl rand -base64 32)
echo "Admin password: $KIKI_ADMIN_PASSWORD" >> admin_creds.txt

# 2. Run migrations (creates admin)
./db_migrate.sh upgrade

# 3. Start services
docker-compose up -d

# 4. Login and verify
curl -X POST http://localhost:8030/api/auth/login \
  -d "username=admin@production.com&password=$KIKI_ADMIN_PASSWORD"

# 5. Delete env vars
unset KIKI_ADMIN_EMAIL
unset KIKI_ADMIN_PASSWORD

# 6. Store admin_creds.txt securely (password manager)
```

### Scenario 2: Promote Team Member to Admin

```bash
# Team member registered normally
# Now needs admin access for user management

./scripts/create_admin.sh --promote alice@company.com

# Alice can now access /admin/users
```

### Scenario 3: Create Additional Admins via UI

1. Login as existing admin
2. Navigate to `/admin/users`
3. Click "Create User"
4. Fill in details:
   - Username: `bob_admin`
   - Email: `bob@company.com`
   - Password: `SecurePass456`
   - Role: **Admin** (select from dropdown)
5. Click "Create User"
6. Bob can now login and access admin features

### Scenario 4: Development Setup

```bash
# Copy example env
cp .env.example .env

# Edit .env, set admin credentials
vim .env  # Set KIKI_ADMIN_EMAIL and KIKI_ADMIN_PASSWORD

# Run migrations
./db_migrate.sh upgrade

# Start dev environment
docker-compose up

# Admin user created automatically
# Login at http://localhost:8021/login
```

## Files Reference

- **Admin UI:** `/services/dashboard/app/templates/admin_users.html`
- **Dashboard Route:** `/services/dashboard/app/main.py` → `/admin/users`
- **Auth Endpoints:** `/services/auth/app/main.py` → Admin endpoints
- **Migration:** `/alembic/versions/20260206_1815_add_default_admin.py`
- **Creation Script:** `/scripts/create_admin.py`
- **Env Template:** `/.env.example` → Admin credential vars

## Next Steps

After setting up admin users:

1. **Disable public registration** (implement invite-only system)
2. **Enable email verification** for new users
3. **Add audit log viewer** to admin panel
4. **Implement role permissions** beyond user/admin (e.g., moderator, analyst)
5. **Add user activity tracking** (last login, action history)
6. **Create admin notification system** for security events

---

**Admin User Management - Live!** 🚀  
Create admins → Manage users → Scale your KIKI platform
