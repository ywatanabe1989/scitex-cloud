<!-- ---
!-- Timestamp: 2025-11-03 14:46:04
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/security.md
!-- --- -->

# SciTeX Cloud Security Guide

## Table of Contents
1. [Security Incident History](#security-incident-history)
2. [Secret Management](#secret-management)
3. [GitHub Security Features](#github-security-features)
4. [Django Security Best Practices](#django-security-best-practices)
5. [Automated Security Checks](#automated-security-checks)
6. [Security Checklist](#security-checklist)
7. [Incident Response](#incident-response)

---

## Security Incident History

### 2025-11-03: GitHub Secret Detection Alert
**Issue**: Checkout.com Production Secret Key detected in deployment/dotenvs/dotenv_dev#L130 (commit 2e4e3d8e)

**Status**: Under Investigation

**Actions Taken**:
- [ ] Review the flagged file and commit
- [ ] Rotate the exposed secret if valid
- [ ] Remove secret from git history using `git filter-repo` or BFG
- [ ] Update .gitignore rules
- [ ] Implement pre-commit hooks

**Root Cause**: Secrets committed to version control

**Prevention**: Implement automated secret scanning before commit

---

## Secret Management

### Current Architecture
- Secrets stored in: `SECRET/` directory (gitignored)
- Environment variables pattern: `SCITEX_CLOUD_*`
- Settings loaded via: `config/settings/settings_{dev,prod}.py`

### Required Environment Variables
```bash
# Django Core
SCITEX_CLOUD_DJANGO_SECRET_KEY=<your-secret-key>
SCITEX_CLOUD_DJANGO_SETTINGS_MODULE=config.settings.settings_dev

# Database
SCITEX_CLOUD_DATABASE_URL=<database-url>

# Redis
SCITEX_CLOUD_REDIS_URL=redis://127.0.0.1:6379/1

# Email
SCITEX_CLOUD_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
SCITEX_CLOUD_EMAIL_HOST=<smtp-host>
SCITEX_CLOUD_EMAIL_PORT=587
SCITEX_CLOUD_EMAIL_USE_TLS=True
SCITEX_CLOUD_EMAIL_HOST_USER=<email>
SCITEX_CLOUD_EMAIL_HOST_PASSWORD=<password>

# OAuth (ORCID)
ORCID_CLIENT_ID=<client-id>
ORCID_CLIENT_SECRET=<client-secret>
ORCID_REDIRECT_URI=<redirect-uri>
```

### Best Practices
1. **Never commit secrets to version control**
   - Use `SECRET/` directory for local secrets
   - Keep `.env` files gitignored
   - Use environment variables in production

2. **Secret Rotation**
   - Rotate secrets immediately if exposed
   - Use strong, randomly generated secrets
   - Document rotation procedures

3. **Access Control**
   - Limit who can access production secrets
   - Use separate secrets for dev/staging/prod
   - Never share secrets via email or chat

### Secret Generation
```bash
# Generate Django SECRET_KEY
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Generate random password
openssl rand -base64 32
```

---

## GitHub Security Features

### Enable GitHub Secret Scanning
Yes, GitHub can periodically check for security issues automatically. Here's how to set it up:

1. **Secret Scanning** (Already Active)
   - GitHub automatically scans public repositories
   - For private repos: Settings → Security → Code security and analysis → Enable secret scanning

2. **Dependabot Alerts**
   - Settings → Security → Enable Dependabot alerts
   - Automatically checks for vulnerable dependencies

3. **Code Scanning (CodeQL)**
   - Settings → Security → Code scanning → Set up CodeQL
   - Scans code for security vulnerabilities

### Recommended GitHub Actions Workflows

#### 1. Secret Scanning Pre-commit
Create `.github/workflows/secret-scanning.yml`:
```yaml
name: Secret Scanning
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: TruffleHog Secret Scan
        uses: trufflesecurity/trufflehog@main
        with:
          extra_args: --only-verified
```

#### 2. Security Audit
Create `.github/workflows/security-audit.yml`:
```yaml
name: Security Audit
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run safety check
        run: |
          pip install safety
          safety check --file requirements.txt
```

---

## Django Security Best Practices

### Current Settings Review

#### ✅ Good Practices (Already Implemented)
- SECRET_KEY loaded from environment variable
- Password validators configured
- CSRF protection enabled
- Session security configured
- Logging configured with rotation

#### ⚠️ Areas for Improvement

1. **Security Headers** (Add to settings_prod.py)
```python
# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SAMESITE = 'Strict'
```

2. **Allowed Hosts** (Production)
```python
ALLOWED_HOSTS = os.getenv('SCITEX_CLOUD_ALLOWED_HOSTS', '').split(',')
```

3. **Admin URL** (Obfuscate in production)
```python
# In urls.py - use random path instead of /admin/
admin_path = os.getenv('SCITEX_CLOUD_ADMIN_PATH', 'admin')
urlpatterns = [
    path(f'{admin_path}/', admin.site.urls),
    # ...
]
```

4. **Rate Limiting**
```python
# Install: pip install django-ratelimit
# Add to views that need protection
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m')
def sensitive_view(request):
    pass
```

### OWASP Top 10 Protection Checklist
- [x] A01:2021 - Broken Access Control (Django permissions in place)
- [x] A02:2021 - Cryptographic Failures (SECRET_KEY from env)
- [ ] A03:2021 - Injection (Add parameterized queries check)
- [x] A04:2021 - Insecure Design (Architecture review needed)
- [ ] A05:2021 - Security Misconfiguration (Add security headers)
- [ ] A06:2021 - Vulnerable Components (Add dependency scanning)
- [x] A07:2021 - Authentication Failures (Strong validators enabled)
- [ ] A08:2021 - Software and Data Integrity (Add checksum verification)
- [x] A09:2021 - Logging Failures (Logging configured)
- [ ] A10:2021 - SSRF (Add URL validation for external requests)

---

## Automated Security Checks

### Pre-commit Hooks
Install pre-commit hooks to prevent secrets from being committed:

1. **Install pre-commit**
```bash
pip install pre-commit
```

2. **Create .pre-commit-config.yaml**
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: detect-private-key
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-r', 'apps/', '-f', 'json', '-o', 'bandit-report.json']
```

3. **Install hooks**
```bash
pre-commit install
pre-commit run --all-files
```

### CI/CD Security Checks
- [ ] Add secret scanning to CI pipeline
- [ ] Run security tests before deployment
- [ ] Implement automated dependency updates
- [ ] Add SAST (Static Application Security Testing)
- [ ] Add DAST (Dynamic Application Security Testing) for staging

---

## Security Checklist

### Before Every Commit
- [ ] No secrets in code
- [ ] No hardcoded credentials
- [ ] No sensitive data in comments
- [ ] Pre-commit hooks passed

### Before Every Deployment
- [ ] Environment variables configured
- [ ] DEBUG = False in production
- [ ] Security headers enabled
- [ ] HTTPS enforced
- [ ] Database backups verified
- [ ] Security audit completed

### Weekly
- [ ] Review GitHub security alerts
- [ ] Check dependency vulnerabilities
- [ ] Review access logs
- [ ] Rotate temporary credentials

### Monthly
- [ ] Full security audit
- [ ] Penetration testing review
- [ ] Update security documentation
- [ ] Review user permissions

### Quarterly
- [ ] Rotate production secrets
- [ ] Security training review
- [ ] Incident response drill
- [ ] Third-party security audit

---

## Incident Response

### Immediate Actions (0-1 hour)
1. **Assess the breach**
   - Identify what was exposed
   - Determine the scope of access
   - Check logs for unauthorized access

2. **Contain the breach**
   - Rotate all potentially compromised secrets
   - Revoke access tokens
   - Block suspicious IPs if applicable

3. **Notify stakeholders**
   - Inform security team
   - Alert affected users if necessary
   - Document the incident

### Short-term Actions (1-24 hours)
1. **Remove secrets from git history**
```bash
# Using git-filter-repo (recommended)
git filter-repo --path deployment/dotenvs/dotenv_dev --invert-paths

# Or using BFG
bfg --delete-files dotenv_dev .
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

2. **Force push cleaned history** (if safe to do so)
```bash
git push --force --all
git push --force --tags
```

3. **Update all secrets**
   - Generate new secrets
   - Update environment variables
   - Deploy with new credentials

### Long-term Actions (1-7 days)
1. **Root cause analysis**
   - Document how the breach occurred
   - Identify process failures
   - Update security procedures

2. **Implement prevention measures**
   - Add pre-commit hooks
   - Enable GitHub secret scanning
   - Train team on security practices

3. **Monitor for abuse**
   - Check for unauthorized access
   - Monitor API usage
   - Review logs for anomalies

### Contacts
- **Security Team**: [Insert contact]
- **GitHub Security**: security@github.com
- **Django Security**: security@djangoproject.com

---

## Resources

### Django Security
- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [Django Security Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [OWASP Django Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Django_Security_Cheat_Sheet.html)

### GitHub Security
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [GitHub Security Advisories](https://docs.github.com/en/code-security/security-advisories)
- [Dependabot](https://docs.github.com/en/code-security/dependabot)

### Tools
- [TruffleHog](https://github.com/trufflesecurity/trufflehog) - Secret scanning
- [detect-secrets](https://github.com/Yelp/detect-secrets) - Pre-commit secret detection
- [bandit](https://github.com/PyCQA/bandit) - Python security linter
- [safety](https://github.com/pyupio/safety) - Dependency vulnerability scanner
- [git-filter-repo](https://github.com/newren/git-filter-repo) - Remove secrets from history

---

## Next Steps

1. **Immediate** (Today)
   - [ ] Investigate the Checkout.com secret alert
   - [ ] Rotate the exposed secret if valid
   - [ ] Remove from git history

2. **This Week**
   - [ ] Set up pre-commit hooks
   - [ ] Enable GitHub secret scanning alerts
   - [ ] Add security headers to production settings
   - [ ] Create GitHub security workflows

3. **This Month**
   - [ ] Complete security audit
   - [ ] Implement rate limiting
   - [ ] Set up automated dependency scanning
   - [ ] Document security procedures

4. **Ongoing**
   - [ ] Monitor security alerts weekly
   - [ ] Review and update security practices monthly
   - [ ] Conduct security training quarterly

---

**Last Updated**: 2025-11-03
**Next Review**: 2025-12-03
**Owner**: Security Team

<!-- EOF -->