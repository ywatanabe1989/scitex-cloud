<!-- ---
!-- Timestamp: 2025-11-05 23:22:59
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/JAVASCRIPT_MIGRATION_STEPS.md
!-- --- -->

Migration from javascript to typescript is not complete yet. Please understand the rules:
  /home/ywatanabe/proj/scitex-cloud/RULES:
  drwxr-xr-x  3 ywatanabe ywatanabe 4.0K Nov  5 22:05 .
  drwxr-xr-x 32 ywatanabe ywatanabe 4.0K Nov  5 23:05 ..
  -rw-r--r--  1 ywatanabe ywatanabe  44K Nov  4 13:50 00_DJANGO_ORGANIZATION_FULLSTACK.md
  -rw-r--r--  1 ywatanabe ywatanabe 9.8K Nov  4 14:14 01_DJANGO_ORGANIZATION_FULLSTACK_CHECKLIST.md
  -rw-r--r--  1 ywatanabe ywatanabe 1.4K Nov  5 19:56 02_TYPESCRIPT_HOT_BUILDING_IN_DEVELOPMENT.md
  -rw-r--r--  1 ywatanabe ywatanabe 6.3K Nov  5 21:25 03_TYPESCRIPT_WATCH_MECHANISM.md
  -rw-r--r--  1 ywatanabe ywatanabe 6.8K Nov  5 22:05 04_CONSOLE_LOG_FEEDBACK_IN_DEVELOPMENT.md

## How to migrate

1. Writing pure javascirpt is prohibited.
2. Old javascript codes are moved to js-potentiall-legacy directories
3. When not found error raised:
   1. Check subdirectories. Typescript is more organized. Type script structure is correct and follow all the time.
   2. If only legacy javascript found, please implement typescript equivalent (and improvement), update path in template if needed, and recompile typescript.

## Example
Error found:

```
GET http://127.0.0.1:8000/static/project_app/js/profile.js net::ERR_ABORTED 404 (Not Found)
```

Then, we might find:

`/static/project_app/js-potentially-legacy/profile.js`

but also, we realize 

`/static/project_app/ts/users/profile.ts`.

In that case, the ts is correct!

<!-- EOF -->