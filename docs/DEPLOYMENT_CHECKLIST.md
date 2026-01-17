# Production Deployment Checklist

This checklist ensures all critical configurations and validations are completed before deploying G.F.P.S to production.

## Pre-Deployment

### Environment Configuration
- [ ] Generate and set unique `SECRET_KEY` using `openssl rand -hex 32`
- [ ] Configure production `DATABASE_URL` (PostgreSQL with SSL)
- [ ] Set `ALLOWED_ORIGINS` to production domains only
- [ ] Configure `FRONTEND_BASE_URL` to production URL
- [ ] Set appropriate `RATE_LIMIT_PER_MINUTE` for production traffic
- [ ] Review and configure all API keys:
  - [ ] `APIFOOTBALL_KEY` (if using live data)
  - [ ] `GOOGLE_CLIENT_ID` (if using OAuth)
  - [ ] `FCM_SERVER_KEY` (if using push notifications)
  - [ ] `SMTP_*` credentials (if using email)

### Security Hardening
- [ ] Remove all default/example credentials
- [ ] Verify CSP headers in `tauri.conf.json` (remove localhost references)
- [ ] Enable HTTPS/TLS for all endpoints
- [ ] Configure nginx with SSL certificates (Let's Encrypt recommended)
- [ ] Enable HSTS headers in nginx
- [ ] Review firewall rules (only expose necessary ports)
- [ ] Disable debug mode and verbose logging
- [ ] Set up secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)

### Database
- [ ] Create production database with appropriate resources
- [ ] Enable automated backups
- [ ] Configure connection pooling
- [ ] Set up read replicas (if needed)
- [ ] Run database migrations (if using Alembic)
- [ ] Create database indexes for performance
- [ ] Test database failover procedures

### Application Configuration
- [ ] Set `MODEL_VERSION` to production model version
- [ ] Configure `EV_MIN_THRESHOLD` based on business requirements
- [ ] Set `STREAMER_ENABLED` and `STREAMER_INTERVAL_SEC` appropriately
- [ ] Configure `SNAPSHOT_INTERVAL_SEC` for persistence
- [ ] Set `ALERT_ENGINE` and `ALERT_ENGINE_INTERVAL_SEC` if using alerts
- [ ] Review and adjust all model parameters:
  - [ ] `FORM_WINDOW`
  - [ ] `DIXON_COLES_RHO`
  - [ ] `FORM_ADJUSTMENT_WEIGHT`
  - [ ] `BASE_HOME_GOALS` and `BASE_AWAY_GOALS`
  - [ ] `MARKET_WEIGHT_MIN` and `MARKET_WEIGHT_MAX`

### Infrastructure
- [ ] Set up Docker or container orchestration (Kubernetes, ECS, etc.)
- [ ] Configure load balancer with health checks
- [ ] Set up CDN for static assets (if applicable)
- [ ] Configure auto-scaling policies
- [ ] Test resource limits (CPU, memory)
- [ ] Set up container registry (ECR, DockerHub, etc.)

### Monitoring & Observability
- [ ] Configure Prometheus metrics collection
- [ ] Set up Grafana dashboards
- [ ] Configure alerting rules:
  - [ ] API error rates
  - [ ] Response time degradation
  - [ ] Database connection issues
  - [ ] Rate limit violations
  - [ ] Authentication failures
- [ ] Set up log aggregation (ELK, CloudWatch, Datadog)
- [ ] Configure uptime monitoring (UptimeRobot, Pingdom, etc.)
- [ ] Set up APM (Application Performance Monitoring)

### Testing
- [ ] Run full backend test suite: `pytest backend/tests/`
- [ ] Run frontend tests: `npm test --run`
- [ ] Perform load testing
- [ ] Test authentication flows end-to-end
- [ ] Verify WebSocket connections
- [ ] Test data provider integrations
- [ ] Validate prediction engine outputs
- [ ] Test alert notifications (email/push)
- [ ] Perform security scanning (CodeQL, Snyk, etc.)

### Performance
- [ ] Enable caching where appropriate
- [ ] Configure Redis for session/cache storage
- [ ] Optimize database queries (use EXPLAIN ANALYZE)
- [ ] Enable compression for API responses
- [ ] Set up CDN for static assets
- [ ] Minify and bundle frontend assets
- [ ] Test with production-like data volumes

## Deployment

### Build & Release
- [ ] Tag release in git: `git tag -a v1.0.0 -m "Production release v1.0.0"`
- [ ] Build Docker images with production tag
- [ ] Push images to container registry
- [ ] Build desktop installers (if deploying desktop app):
  - [ ] Windows MSI: `npm run tauri:build`
  - [ ] macOS DMG: `npm run tauri:build`
  - [ ] Linux AppImage: `npm run tauri:build`
- [ ] Sign desktop application binaries (required for macOS/Windows)

### Deployment Process
- [ ] Deploy to staging environment first
- [ ] Smoke test staging deployment
- [ ] Run integration tests on staging
- [ ] Deploy to production using blue-green or rolling deployment
- [ ] Monitor deployment logs for errors
- [ ] Verify all services are healthy
- [ ] Test critical user flows

### Post-Deployment Validation
- [ ] Verify `/health` endpoint returns 200 OK
- [ ] Test authentication (signup, login, OAuth)
- [ ] Verify protected endpoints require valid tokens
- [ ] Test key features:
  - [ ] Predictions API
  - [ ] Odds ingestion
  - [ ] Value bets calculation
  - [ ] WebSocket streaming
  - [ ] Alert generation (if enabled)
- [ ] Check database connectivity and query performance
- [ ] Verify monitoring dashboards show data
- [ ] Test rate limiting behavior
- [ ] Validate CORS configuration

## Post-Deployment

### Documentation
- [ ] Update API documentation with production URLs
- [ ] Document deployment procedures
- [ ] Create runbook for common operations
- [ ] Document incident response procedures
- [ ] Update README with production setup instructions

### Team Coordination
- [ ] Notify stakeholders of deployment completion
- [ ] Share monitoring dashboard links
- [ ] Schedule post-deployment review meeting
- [ ] Document lessons learned

### Ongoing Maintenance
- [ ] Set up weekly security review schedule
- [ ] Configure automated dependency updates (Dependabot, Renovate)
- [ ] Schedule quarterly penetration testing
- [ ] Plan database maintenance windows
- [ ] Review and rotate credentials monthly

## Rollback Plan

If deployment issues occur:

1. **Immediate Actions:**
   - [ ] Stop new traffic to problematic version
   - [ ] Route traffic back to previous stable version
   - [ ] Notify team and stakeholders

2. **Investigation:**
   - [ ] Capture logs and metrics from failed deployment
   - [ ] Identify root cause
   - [ ] Document timeline of events

3. **Recovery:**
   - [ ] Fix identified issues
   - [ ] Test fixes in staging
   - [ ] Prepare new deployment

## Emergency Contacts

- **DevOps Lead:** [Name/Contact]
- **Backend Lead:** [Name/Contact]
- **Security Lead:** [Name/Contact]
- **Database Admin:** [Name/Contact]
- **On-Call Schedule:** [Link to rotation]

## Version History

- **v1.0** (2026-01-17): Initial production deployment checklist
  - Comprehensive pre-deployment validation
  - Security hardening steps
  - Monitoring and observability setup
  - Rollback procedures
