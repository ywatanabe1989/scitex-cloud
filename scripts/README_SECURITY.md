# Security Monitoring Scripts

## Quick Start

### Check GitHub Security Alerts
```bash
./scripts/check_github_security.sh
```

This will:
1. Fetch all GitHub security alerts (secrets, Dependabot, code scanning)
2. Save them to `logs/security/security-<timestamp>.txt`
3. Create a symlink to `logs/security/security-latest.txt`
4. Exit with error code if alerts found (useful for CI/CD)

## Setup

### Install GitHub CLI
```bash
# Ubuntu/Debian
sudo apt install gh

# macOS
brew install gh
```

### Authenticate
```bash
gh auth login
```

## Automated Checks

### Option 1: Cron Job (Recommended)
Check security alerts daily at 9 AM:

```bash
# Edit crontab
crontab -e

# Add this line:
0 9 * * * cd /home/ywatanabe/proj/scitex-cloud && ./scripts/check_github_security.sh
```

### Option 2: GitHub Actions
The script can also run in GitHub Actions (already configured in `.github/workflows/security-audit.yml`)

### Option 3: Manual
Run whenever you want:
```bash
./scripts/check_github_security.sh
```

## Output Files

All security reports are saved to:
```
logs/security/
├── security-20251103_120000.txt  # Timestamped report
├── security-20251103_150000.txt  # Another report
└── security-latest.txt           # Symlink to most recent
```

## Agent Workflow

1. **Check for alerts**:
   ```bash
   ./scripts/check_github_security.sh
   ```

2. **If alerts found** (exit code 1):
   - Read `logs/security/security-latest.txt`
   - Agents work on fixing issues
   - Re-run script to verify fixes

3. **If no alerts** (exit code 0):
   - Continue with other tasks

## Integration with Claude Code

Agents can check for security issues:
```bash
# Check if security alerts exist
if ./scripts/check_github_security.sh; then
    echo "No security issues"
else
    echo "Security alerts found!"
    cat logs/security/security-latest.txt
    # Agent can now read the file and work on fixes
fi
```

## What Gets Checked

1. **Secret Scanning** - Exposed API keys, tokens, passwords
2. **Dependabot** - Vulnerable dependencies (CVEs)
3. **Code Scanning** - Security vulnerabilities in code (CodeQL)

## Example Output

```
=== GitHub Security Alerts Report ===
Generated: 2025-11-03 12:00:00
Repository: SciTeX-AI/scitex-cloud

==========================================

### SECRET SCANNING ALERTS ###

- [open] Checkout.com Production Secret Key
  Location: deployment/dotenvs/dotenv_dev:130
  URL: https://github.com/SciTeX-AI/scitex-cloud/security/secret-scanning/1

==========================================

### DEPENDABOT VULNERABILITY ALERTS ###

- [open] HIGH: Django SQL Injection vulnerability
  Package: django
  CVE: CVE-2024-12345
  URL: https://github.com/SciTeX-AI/scitex-cloud/security/dependabot/1

==========================================

### SUMMARY ###

Total open alerts: 2

⚠️  ACTION REQUIRED: Security issues found!
Review the alerts above and take appropriate action.
```

## Troubleshooting

### "gh: command not found"
Install GitHub CLI: https://cli.github.com/

### "Not authenticated with GitHub CLI"
Run: `gh auth login`

### No alerts showing but you got an email
- Check repository permissions
- Ensure features are enabled in Settings → Security
- Try running: `gh secret list --repo owner/repo`

## Next Steps

After reviewing alerts:
1. Fix the security issue
2. Run the script again to verify
3. Update `security.md` with incident details
