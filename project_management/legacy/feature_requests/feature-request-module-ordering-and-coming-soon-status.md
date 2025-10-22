<!-- ---
!-- Timestamp: 2025-06-28 02:09:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Cloud/project_management/feature_requests/feature-request-module-ordering-and-coming-soon-status.md
!-- --- -->

# Feature Request: Module Ordering and Coming Soon Status

## Summary
Standardize module ordering across the website and implement "Coming Soon" status for modules that are not yet available.

## Feature Request Details

### Module Ordering
- **Requirement**: All modules should be displayed in the natural scientific project workflow order:
  1. **Scholar** (Literature discovery)
  2. **Viz** (Data visualization) 
  3. **Code** (Analysis and computation)
  4. **Writer** (Manuscript preparation)

- **Scope**: This ordering should be consistent across:
  - Navigation menus
  - Dashboard module cards
  - Landing page sections
  - Footer links
  - Any other module listings

### Coming Soon Status
- **Requirement**: Viz and Code modules should be explicitly marked as "Coming Soon"
- **Implementation**: Clear visual indicators that these modules are in development
- **User Experience**: Users should understand these features are planned but not yet available

### Hero Section Consistency
- **Requirement**: All pages should have hero sections matching the landing page design
- **Exception**: Dashboard page should maintain its current design
- **Scope**: Scholar, Writer, Viz, and Code module pages

## Technical Implementation

### Priority: High
This affects user experience and navigation consistency across the platform.

### Implementation Areas:
1. **Navigation Components**:
   - Update main navigation order
   - Update footer module links
   - Update mobile menu order

2. **Dashboard**:
   - Reorder module cards
   - Add "Coming Soon" badges to Viz and Code cards
   - Ensure consistent ordering in statistics

3. **Landing Page**:
   - Verify module section ordering
   - Update any inconsistent displays

4. **Individual Module Pages**:
   - Add hero sections to Scholar and Writer pages
   - Create placeholder pages for Viz and Code with "Coming Soon" status
   - Ensure consistent hero design across all module pages

5. **Template Updates**:
   - Create reusable hero component
   - Update base templates for consistent ordering
   - Add coming soon functionality

## User Story
As a researcher using SciTeX Cloud, I want to see modules organized in the natural workflow order (Scholar → Viz → Code → Writer) so that I can easily follow the scientific research process from literature review to final manuscript preparation.

## Acceptance Criteria
- [ ] All module listings show Scholar, Viz, Code, Writer order consistently
- [ ] Viz and Code modules display "Coming Soon" status
- [ ] Hero sections are consistent across all module pages (except dashboard)
- [ ] Navigation maintains the standard order
- [ ] Dashboard module cards follow the standard order
- [ ] Footer links follow the standard order

## Related Files
- Navigation templates
- Dashboard templates  
- Module page templates
- Footer templates
- CSS/styling files

## Impact Assessment
- **User Experience**: High positive impact - clearer workflow understanding
- **Development Effort**: Medium - template updates and component creation
- **Testing Required**: UI/UX testing across all affected pages

## Request Status
- **Status**: Open
- **Priority**: High
- **Assigned To**: TBD
- **Created By**: User via /home/ywatanabe/proj/scitex-cloud/docs/from_user/module_orders.md
- **Created Date**: 2025-06-28

<!-- EOF -->