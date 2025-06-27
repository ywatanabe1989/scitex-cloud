# Django Project Structure Comparison with airight

**Date:** May 22, 2025

## Overview

This document compares the structure and setup of the `SciTeX-Cloud` project with the `airight` project to identify best practices for Django application deployment and maintenance.

## Project Structure Analysis

### Common Elements

Both projects follow standard Django conventions:
- Django apps in an `apps` directory
- Configuration settings in a `config` directory
- Static files management with collectstatic
- Template organization in folders by app

### Differences and Learnings

1. **Script Organization**
   - airight: Uses comprehensive start/stop scripts with command-line arguments
   - SciTeX-Cloud: Has a more advanced unified startup script that auto-detects which script to run
   - Learning: SciTeX-Cloud's approach is more user-friendly but could benefit from airight's production deployment logic

2. **Environment Configuration**
   - airight: Uses a simpler settings approach with a single settings.py file
   - SciTeX-Cloud: Uses a split settings approach (base, dev, prod) which is more modular
   - Learning: SciTeX-Cloud's approach is better for larger projects, but we need to ensure consistency

3. **Deployment Configuration**
   - airight: Uses uWSGI directly with custom init file
   - SciTeX-Cloud: Has more comprehensive Nginx configuration
   - Learning: We should integrate airight's uWSGI approach with our Nginx setup

4. **Logging**
   - airight: Simpler logging to a single file
   - SciTeX-Cloud: More detailed logging with separate files for different purposes
   - Learning: SciTeX-Cloud's approach is better but we need to ensure logs are properly rotated

## Script Features to Adopt

From the airight project, we should adopt:

1. **Graceful shutdown in production**
   ```bash
   # Clear socket before starting
   echo "Cleaning up existing socket..."
   sudo rm -f "$APP_HOME/uwsgi.sock"
   sudo pkill -f uwsgi -9
   ```

2. **Environment activation check**
   ```bash
   if [ ! -d "env" ]; then
       echo "Creating virtual environment..."
       python3 -m venv env
   fi
   ```

3. **Postgres service start**
   ```bash
   start_postgresql() {
      sudo service postgresql start
   }
   ```

## Deployment Configuration to Adopt

1. **uWSGI Configuration**
   ```ini
   [uwsgi]
   chdir = /path/to/project
   module = config.wsgi
   home = /path/to/project/env
   master = true
   processes = 6
   socket = /path/to/project/uwsgi.sock
   chmod-socket = 666
   vacuum = true
   enable-threads = true
   logto = /path/to/project/uwsgi.log
   ```

2. **Nginx Configuration**
   SciTeX-Cloud already has a good Nginx configuration, but we should ensure it properly connects to the uWSGI socket.

## Logging Improvements

1. **Structured Logging**
   Set up structured logging to make log analysis easier:
   ```python
   LOGGING = {
       'formatters': {
           'standard': {
               'format': '{asctime} [{levelname}] {name}: {message}',
               'style': '{',
           },
       },
       # ... handlers and loggers
   }
   ```

2. **Log Rotation**
   Implement log rotation to prevent logs from growing too large:
   ```python
   'handlers': {
       'file': {
           'level': 'INFO',
           'class': 'logging.handlers.RotatingFileHandler',
           'filename': BASE_DIR / 'logs/app.log',
           'maxBytes': 10 * 1024 * 1024,  # 10 MB
           'backupCount': 5,
           'formatter': 'standard',
       },
   }
   ```

## Next Steps

1. **Fix URL Namespace Issues**
   - We've updated the header to properly use namespaced URLs
   - All URL names should be namespaced to avoid conflicts

2. **Complete the Design System Page**
   - We've added the design system and features pages
   - All pages are now properly linked in the navigation

3. **Improve Deployment Scripts**
   - Our scripts are already well-structured
   - We should add better error handling for production environments

4. **Database Configuration**
   - Consider adopting a more robust database configuration for production

5. **Environment-specific Settings**
   - Ensure all environment-specific settings are properly separated