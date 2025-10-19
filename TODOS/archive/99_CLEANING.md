<!-- ---
!-- Timestamp: 2025-10-18 21:58:49
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/CLEANING.md
!-- --- -->

- [x] ./scripts should be organized with subdirectories like ./scripts/{deployment,utils}
  - ✅ Created subdirectories: deployment/, server/, dev/, prod/, docs/, demo/, utils/
  - ✅ Moved all scripts to appropriate locations
  - ✅ Updated all documentation references
  - ✅ Tested scripts work from new locations
- [x] Consolidate overlapping deployment documentation
  - ✅ Moved file organization content → deployment/README.md
  - ✅ Streamlined 00_QUICK_START.md to minimal checklist only
  - ✅ Removed redundant 99_FILE_ORGANIZATION.md
  - ✅ Updated all cross-references
  - **Final structure**: 4 focused docs + comprehensive README
    - 00_QUICK_START.md (~175 lines) - Minimal step-by-step checklist
    - 01_ENVIRONMENT_VARIABLES.md - Complete env var reference
    - 02_POSTGRESQL_SETUP.md - Database configuration deep dive
    - 03_UWSGI_SETUP.md - Application server details
    - README.md - Overview, file organization, dev/prod differences

<!-- EOF -->