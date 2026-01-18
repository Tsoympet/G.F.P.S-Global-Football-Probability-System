# Security Best Practices for G.F.P.S

This document outlines critical security configurations and best practices for deploying and maintaining the Global Football Probability System.

## 🔐 Core Security Requirements

### 1. Secret Key Management

**CRITICAL:** The `SECRET_KEY` environment variable is required for JWT token signing and must be set before running the application.

```bash
# Generate a secure random key
openssl rand -hex 32

# Set in .env file
SECRET_KEY=your-generated-key-here
```

**Never:**
- Use default or example keys in production
- Commit secret keys to version control
- Share keys across environments (dev/staging/prod)

### 2. Database Security

**For Production:**
- Use PostgreSQL instead of SQLite
- Enable SSL/TLS connections
- Use connection pooling with proper limits
- Rotate database credentials regularly

```bash
# Example secure connection string
DATABASE_URL=postgresql://user:password@host:5432/dbname?sslmode=require
```

### 3. CORS Configuration

Restrict allowed origins to your actual frontend domains:

```bash
# In .env
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

**Do not** use wildcards (`*`) in production.

### 4. Rate Limiting

The application includes basic rate limiting, but for production:

- Configure appropriate limits based on your use case
- Consider Redis-backed rate limiting for distributed deployments
- Monitor rate limit violations

```bash
RATE_LIMIT_PER_MINUTE=120
RATE_LIMIT_WINDOW_SEC=60
```

### 5. Content Security Policy (CSP)

The Tauri desktop app now includes CSP headers. Review and adjust based on your needs:

```json
"csp": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' http://localhost:8000 ws://localhost:8000"
```

**For production builds:**
- Remove `localhost` references
- Use your actual API domain
- Minimize use of `'unsafe-inline'` where possible

### 6. HTTPS/TLS

**Always** use HTTPS in production:

- Configure nginx with valid SSL certificates
- Use Let's Encrypt for free certificates
- Enable HSTS headers
- Redirect HTTP to HTTPS

### 7. Authentication & Authorization

**Token Security:**
- Tokens expire after 7 days (configurable via `ACCESS_TOKEN_EXPIRE_DAYS`)
- Consider shorter expiry times with refresh token pattern
- Store tokens securely (desktop app uses encrypted storage)

**Password Requirements:**
- Minimum 8 characters
- Hashed with bcrypt
- Never log or expose passwords

### 8. Desktop App Encryption

**Local Storage Security:**

The desktop application encrypts sensitive data (auth tokens, API keys) before storing in localStorage. To maximize security:

```bash
# In GFPS/desktop/.env
# Generate a unique value for each deployment
VITE_SECRET_SALT=$(openssl rand -hex 32)
```

**Best practices:**
- Set `VITE_SECRET_SALT` at build time for production deployments
- Use different salts for dev/staging/prod builds
- Never commit the `.env` file to version control
- If not set, the app will use a device-specific fallback (less secure)

**Note:** Changing the salt will invalidate existing encrypted localStorage data. Users will need to re-authenticate and reconfigure settings.

### 9. API Key Management

For data provider integrations:

```bash
APIFOOTBALL_KEY=your-api-key
GOOGLE_CLIENT_ID=your-google-client-id
```

**Best practices:**
- Use separate keys for dev/staging/prod
- Rotate keys periodically
- Monitor API usage and quotas
- Store in environment variables, not code

### 10. Input Validation

The backend includes Pydantic validation. Ensure:

- All API inputs are validated
- SQL injection protection via SQLAlchemy ORM
- XSS protection in frontend (React escaping by default)
- File upload validation (if applicable)

### 11. Monitoring & Logging

**Security monitoring:**
- Log authentication failures
- Monitor rate limit violations
- Track unusual API usage patterns
- Set up alerts for security events

**Do not log:**
- Passwords (plaintext or hashed)
- API keys
- User tokens
- Sensitive personal data

## 🚀 Production Deployment Checklist

Before deploying to production:

- [ ] Generate and set unique `SECRET_KEY`
- [ ] Generate and set unique `VITE_SECRET_SALT` for desktop builds
- [ ] Configure PostgreSQL with SSL
- [ ] Set restrictive `ALLOWED_ORIGINS`
- [ ] Enable HTTPS with valid certificates
- [ ] Review and adjust rate limits
- [ ] Set up monitoring and alerting
- [ ] Enable database backups
- [ ] Review and test CSP headers
- [ ] Audit all environment variables
- [ ] Test authentication flows
- [ ] Review error messages (no sensitive data leakage)
- [ ] Set up log aggregation
- [ ] Document incident response procedures

## 🔍 Security Audit Schedule

**Regular reviews:**
- Weekly: Check logs for anomalies
- Monthly: Review access patterns and rate limits
- Quarterly: Full security audit
- Annually: Penetration testing

## 📞 Incident Response

If a security incident is detected:

1. **Immediate Actions:**
   - Rotate compromised credentials
   - Review access logs
   - Block suspicious IP addresses
   - Notify affected users

2. **Investigation:**
   - Document the incident
   - Identify the root cause
   - Assess impact

3. **Remediation:**
   - Apply security patches
   - Update configurations
   - Improve monitoring

4. **Post-Incident:**
   - Update documentation
   - Review and improve procedures
   - Conduct team training

## 🔗 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Tauri Security](https://tauri.app/v1/guides/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/14/faq/security.html)

## ⚠️ Known Dependency Issues

### Desktop App (Tauri/Rust)

**glib Vulnerability (CVE in versions 0.15.0-0.19.x)**

**Issue:** The `glib` crate versions 0.15.0 through 0.19.x contain a vulnerability in `VariantStrIter::impl_get` function that can cause undefined behavior and NULL pointer dereferences.

**Status:** Partially mitigated
- ✅ Added direct dependency on `glib >= 0.20.0` (currently using 0.21.5)
- ⚠️  GTK3 transitive dependencies still use `glib 0.18.5` (unmaintained)

**Explanation:**
The desktop app uses Tauri, which depends on GTK3-based packages (gtk, webkit2gtk, etc.) version 0.18.x. These packages are unmaintained and locked to `glib ^0.18`. The vulnerability was fixed in `glib 0.20.0`, but upgrading would require migrating to GTK4.

**Mitigation:**
1. Added `glib >= 0.20.0` as a direct dependency to ensure non-vulnerable version is available
2. Dependabot can now track and suggest updates to the safe version
3. Any direct usage of glib in the project will use the safe version (0.21.5)
4. The vulnerable code path in glib 0.18.5 is only accessible through GTK3 packages

**Future Resolution:**
Fully resolving this issue requires:
- Upgrading to Tauri with GTK4 support (when available), OR
- Using a different UI framework, OR
- Creating a custom fork of glib 0.18.5 with the security patch backported

**References:**
- Vulnerability affects: glib >= 0.15.0, < 0.20.0
- Fixed in: glib >= 0.20.0
- Issue type: Undefined behavior in VariantStrIter iterator implementation

## 📝 Version History

- **v1.1** (2026-01-18): Added dependency vulnerability mitigation
  - Documented glib vulnerability in GTK3 packages (CVE affecting versions 0.15.0-0.19.x)
  - Added direct glib >=0.20.0 dependency to enable Dependabot updates
  - Note: GTK3 transitive dependencies still use glib 0.18.5 (unmaintained)
- **v1.0** (2026-01-17): Initial security documentation
  - Required SECRET_KEY enforcement
  - CSP header configuration
  - Production deployment checklist
