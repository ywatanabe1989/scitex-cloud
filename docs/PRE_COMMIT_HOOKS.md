# Pre-commit Hooks for Security

## What Are Pre-commit Hooks?

Pre-commit hooks automatically check your code **before** you commit, preventing secrets and security issues from entering git history.

## Already Installed! ✓

Pre-commit hooks are already installed in this project. They will run automatically every time you commit.

## What Gets Checked

On every commit, these checks run automatically:

1. **Detect Secrets** - Catches API keys, tokens, passwords
2. **Detect Private Keys** - Catches SSH keys, certificates
3. **Check Large Files** - Prevents files > 1MB from being committed
4. **Check Merge Conflicts** - Detects unresolved merge conflict markers
5. **Bandit** - Python security linter
6. **Black** - Python code formatter (optional)
7. **YAML/JSON validation** - Ensures config files are valid

## How It Works

```bash
# Normal git workflow - hooks run automatically
git add .
git commit -m "your message"

# If secrets detected, commit is BLOCKED:
# ❌ Detect secrets.......................Failed
# The commit will be prevented!
```

## Manual Checks

Run checks manually without committing:

```bash
# Check all files
pre-commit run --all-files

# Check specific hook
pre-commit run detect-secrets --all-files

# Check only staged files
pre-commit run
```

## Example: Catching a Secret

```bash
# You accidentally add a secret
echo "API_KEY=sk_live_abc123xyz" > config.py
git add config.py
git commit -m "Add config"

# Pre-commit BLOCKS the commit:
Detect secrets...........................................................Failed
- hook id: detect-secrets
- exit code: 1

❌ Potential secrets detected!
```

## If You Need to Bypass (Use Sparingly!)

```bash
# Skip pre-commit hooks (NOT RECOMMENDED)
git commit --no-verify -m "message"

# Better: Fix the issue, then commit
```

## Updating Hooks

```bash
# Update to latest versions
pre-commit autoupdate

# Clean and reinstall
pre-commit clean
pre-commit install
```

## Configuration

Edit `.pre-commit-config.yaml` to customize:

```yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        # Exclude certain files
        exclude: package-lock.json
```

## Secrets Baseline

The `.secrets.baseline` file contains known "secrets" that are actually okay (like test keys). If you have a false positive:

```bash
# Recreate baseline to include new safe "secrets"
detect-secrets scan > .secrets.baseline
git add .secrets.baseline
git commit -m "Update secrets baseline"
```

## Troubleshooting

### "Hook not found"
```bash
pre-commit install
```

### "Version mismatch"
```bash
pre-commit autoupdate
pre-commit clean
```

### "Too many false positives"
Edit `.secrets.baseline` or add to `.pre-commit-config.yaml`:
```yaml
exclude: |
  (?x)^(
    package-lock.json|
    .*\.min\.js|
    .*\.map
  )$
```

## Benefits

- ✅ **Prevents secrets in git** - Blocks commits with secrets
- ✅ **Catches issues early** - Before they reach remote
- ✅ **Zero effort** - Runs automatically
- ✅ **Fast feedback** - Know immediately if there's an issue
- ✅ **Team consistency** - Everyone uses same checks

## See Also

- Main security docs: `security.md`
- Pre-commit docs: https://pre-commit.com/
- detect-secrets: https://github.com/Yelp/detect-secrets
