# Feature Request: Legal and Contact Pages

## Description
Create essential pages for the SciTeX Web platform:
1. Contact page with a contact form and company information
2. Privacy Policy page outlining data handling practices
3. Terms of Use page detailing usage terms and conditions

These pages are necessary for legal compliance and providing users with essential information about the platform.

## Justification
- Legal requirement for privacy policy and terms of use for web applications
- Necessary for building user trust and transparency
- Provides users with a clear way to contact the company
- Protects both users and the company by clearly defining rights and responsibilities

## Acceptance Criteria
- [ ] Contact page with:
  - [ ] Contact form with name, email, subject, and message fields
  - [ ] Form validation
  - [ ] Company contact information (email, address)
  - [ ] Links to social media profiles
  - [ ] Map showing company location (optional)

- [ ] Privacy Policy page with:
  - [ ] Clear explanation of data collection practices
  - [ ] Information on cookies and tracking
  - [ ] Third-party service providers
  - [ ] User rights regarding their data
  - [ ] Contact information for privacy concerns
  - [ ] Last updated date

- [ ] Terms of Use page with:
  - [ ] Clear explanation of acceptable use
  - [ ] User responsibilities
  - [ ] Intellectual property rights
  - [ ] Limitations of liability
  - [ ] Dispute resolution process
  - [ ] Modification terms
  - [ ] Last updated date

- [ ] All pages should:
  - [ ] Be responsive and accessible
  - [ ] Use consistent styling with the rest of the site
  - [ ] Be linked in the site footer
  - [ ] Have clear, readable content formatted for easy scanning

## Progress
- [x] Create feature branch (feature/legal-and-contact-pages)
- [x] Design and implement Contact page
  - Created contact.html with contact form
  - Added company contact information
  - Implemented form validation
  - Added Google Maps integration
- [x] Design and implement Privacy Policy page
  - Created privacy_policy.html with all required sections
  - Added comprehensive content following legal standards
  - Made the content easy to read and scan
- [x] Design and implement Terms of Use page
  - Created terms_of_use.html with all required sections
  - Added comprehensive content following legal standards
  - Made the content easy to read and scan
- [x] Add links to pages in the site footer
  - Added links in the base.html template
  - Created a dedicated Legal section in the footer
- [x] Add form handling for Contact page
  - Implemented form submission handling in views.py
  - Added error and success message display
  - Added client-side validation with JavaScript
- [x] Create base template for consistent layout
  - Created base.html with header and footer
  - Set up template inheritance for all pages
  - Implemented responsive design with mobile support
- [x] Test pages for responsiveness and accessibility
  - Added skip-to-content link for keyboard navigation
  - Improved focus styles for keyboard users
  - Added proper ARIA attributes for screen readers
  - Fixed form validation accessibility issues
  - Added semantic HTML elements (article, address, time)
  - Added ID anchors for all section headings
  - Improved social media icon accessibility
  - Added aria-labels to improve link context
  - Converted emoji icons to Font Awesome icons
- [ ] Review legal content with appropriate stakeholders
- [ ] Merge feature branch to develop