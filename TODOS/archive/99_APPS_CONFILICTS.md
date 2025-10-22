<!-- ---
!-- Timestamp: 2025-10-18 13:26:12
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/APPS_CONFILICTS.md
!-- --- -->

- [ ] We have factored out profile_app from workspace_app
- [ ] During the migration, I renamed workspace_app to profile_app in a bulky manner
  - [ ] I think here, I renamed migration histories as well, using ~/.bin/utils/rename.sh
- [ ] This might have caused model conflicts or database corruption
- [ ] Fortunatelly, the user is only me, ywatanabe (ywata1989@gmail.com). So, we can start database freshly

Thus, I want you to:
1. fix the codeabse
2. teach me what happened, what i should have done, how to prevent this in the future when database cannot start fresh

[INFO] Admin panel: http://localhost:8000/admin
[INFO] Hot reload enabled
[INFO] Press Ctrl+C to stop
Redis not available in development, using local memory cache
 SciTeX Cloud settings loaded: DEVELOPMENT
Redis not available in development, using local memory cache
 SciTeX Cloud settings loaded: DEVELOPMENT
2025-10-18 02:00:22,496 [INFO] django.utils.autoreload: Watching for file changes with StatReloader
Performing system checks...

⚠️ SciTeX-Scholar package not available: No module named 'scitex_scholar'
   Falling back to database-only search
System check identified some issues:

WARNINGS:
?: (urls.W005) URL namespace 'cloud_app' isn't unique. You may not be able to reverse all URLs in this namespace

System check identified 1 issue (0 silenced).
October 18, 2025 - 02:00:23
Django version 5.2.7, using settings 'config.settings'
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.

WARNING: This is a development server. Do not use it in a production setting. Use a production WSGI or ASGI server instead.
For more information on production servers see: https://docs.djangoproject.com/en/5.2/howto/deployment/
2025-10-18 02:01:39,981 [ERROR] django.request: Internal Server Error: /auth/login/
Traceback (most recent call last):
  File "/home/ywatanabe/.env-3.11/lib/python3.11/site-packages/django/core/handlers/exception.py", line 55, in inner
    response = get_response(request)
               ^^^^^^^^^^^^^^^^^^^^^
  File "/home/ywatanabe/.env-3.11/lib/python3.11/site-packages/django/core/handlers/base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ywatanabe/proj/scitex-cloud/apps/auth_app/views.py", line 108, in login_view
    user_obj = User.objects.get(email=username)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ywatanabe/.env-3.11/lib/python3.11/site-packages/django/db/models/manager.py", line 87, in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ywatanabe/.env-3.11/lib/python3.11/site-packages/django/db/models/query.py", line 636, in get
    raise self.model.MultipleObjectsReturned(
django.contrib.auth.models.User.MultipleObjectsReturned: get() returned more than one User -- it returned 2!

