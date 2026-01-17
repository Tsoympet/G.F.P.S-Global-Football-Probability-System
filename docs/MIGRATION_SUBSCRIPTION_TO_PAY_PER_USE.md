# Migration Guide: Subscription Model to Pay-Per-Use

## Overview

GFPS has transitioned from a role-based subscription model to a **pay-per-use model**. Users are now charged only for the external data API providers they consume, with no subscription tiers or role-based access restrictions.

## What Changed

### Removed
- **User roles**: The `role` field (previously defaulting to "free") has been removed from the User model
- **Role-based access control**: No endpoints check user roles for authorization
- **Subscription tiers**: No concept of free vs. premium user tiers

### Added
- **API usage tracking**: New fields `api_calls_count` and `api_calls_last_reset` on the User model to track API consumption
- **Pay-per-use billing**: Users are billed based on actual API data provider usage

### Unchanged
- **Authentication**: JWT-based authentication remains the same
- **OAuth providers**: Google OAuth is fully supported and additional providers can be easily added
- **2FA support**: TOTP-based two-factor authentication remains available
- **All API endpoints**: No changes to endpoint URLs or request/response formats

## Database Migration

If you have an existing database, the `role` column will be automatically dropped when the new code runs. The migration is handled by SQLAlchemy's schema management.

**Migration steps:**
1. Backup your database before upgrading
2. Deploy the new code
3. The database schema will be automatically updated on startup
4. Existing user accounts will continue to work without any action required

## For Developers

### Token Changes
JWT tokens no longer include a `role` field. If your client code was checking the role field, remove those checks:

**Before:**
```typescript
interface Profile {
  email: string;
  role?: string;  // ❌ No longer present
}
```

**After:**
```typescript
interface Profile {
  email: string;
  // role field removed
}
```

### API Response Changes
Authentication endpoints (`/auth/signup`, `/auth/login`, `/auth/google`) no longer return a `role` field in the profile object:

**Before:**
```json
{
  "ok": true,
  "token": "...",
  "profile": {
    "email": "user@example.com",
    "display_name": "User Name",
    "role": "free"  // ❌ No longer returned
  }
}
```

**After:**
```json
{
  "ok": true,
  "token": "...",
  "profile": {
    "email": "user@example.com",
    "display_name": "User Name"
  }
}
```

## Adding More OAuth Providers

Google OAuth is currently supported. To add additional social login providers (Facebook, Twitter, GitHub, etc.):

1. Add the provider's CLIENT_ID and CLIENT_SECRET to your `.env` file
2. Install the appropriate OAuth library (e.g., `authlib` for general OAuth support)
3. Create a new endpoint in the auth router following the Google OAuth pattern
4. Update the frontend to add a login button for the new provider

**Recommended approach for better maintainability:**

For a single additional provider, you can add it to `backend/google_auth.py`. For multiple providers, consider organizing them in a dedicated module:

```
backend/
  auth/
    __init__.py
    google.py      # Google OAuth
    github.py      # GitHub OAuth
    facebook.py    # Facebook OAuth
    router.py      # Main auth router
```

Example for adding GitHub OAuth in `backend/google_auth.py` or a dedicated `backend/auth/github.py`:

```python
# In .env
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

# In backend/google_auth.py (or backend/auth/github.py)
class GitHubLogin(BaseModel):
    access_token: str

@router.post("/github")
def github_login(p: GitHubLogin, db: Session = Depends(get_db)):
    # Verify GitHub token
    # Extract email, name, avatar from GitHub API
    # Create or login user (similar to google_login)
    # Return JWT token
    pass
```

## Questions?

If you have questions about this migration, please open an issue on the GitHub repository.
