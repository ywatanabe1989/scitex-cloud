<!-- ---
!-- Timestamp: 2025-10-20 10:08:47
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/90_INTEGRATIONS_DETAILS.md
!-- --- -->

## TODO
We are planning to reduce the barrier for tool switching bidirectionally

### Reference Management
- [ ] Zotero
  - [ ] Import: Bibliography with collections/tags, PDF annotations, paper metadata
  - [ ] Export: Manuscripts as preprint entries, project metadata, citation files (.bib, .ris)
  - [ ] Link: Live citation insertion, auto-update on library changes, tagged items

- [ ] Mendeley
  - [ ] Import: Reference library, groups, annotations
  - [ ] Export: Bibliography exports, project citations
  - [ ] Link: Real-time citation sync, collaborative groups

### Writing & Collaboration
- [ ] Overleaf
  - [ ] Import: LaTeX projects, document structure, figures/tables, .bib files
  - [ ] Export: Compile manuscripts to LaTeX, push figures, submission packages
  - [ ] Link: Two-way sync with conflict resolution, collaborator mirroring, real-time preview

### Communication & Collaboration
- [ ] Slack
  - [ ] Export: Analysis results, publication notifications, project updates
  - [ ] Link: Webhooks for project events, bot commands for queries

- [ ] Discord
  - [ ] Export: Research updates, collaboration notifications
  - [ ] Link: Bot integration, channel-project mapping

### ORCID & Academic Identity
- [ ] ORCID
  - [ ] Import: Publication list, affiliations, funding information
  - [ ] Link: Author verification, automatic publication updates

### Project Management
- [ ] Notion
  - [ ] Import: Project wikis, task databases, research notes
  - [ ] Export: Project documentation, meeting notes
  - [ ] Link: Bidirectional sync, embedded views

- [ ] Trello
  - [ ] Import: Project boards, task lists
  - [ ] Export: Research workflow cards
  - [ ] Link: Task synchronization, status updates

## Priorities
3. GitHub/GitLab Import (Medium-Easy)

  Why:
  - Well-documented REST APIs
  - OAuth is standard
  - For MVP: just clone repo → create project structure
  - Don't need to handle PRs/issues initially
  - GitHub has excellent Python libraries (PyGithub)
  - Can start with public repos (no auth needed for testing)

4. Export .bib file from Zotero (Easy)

  Why:
  - If your project already stores references, just format as BibTeX
  - No API needed - just file generation
  - Standard format, lots of Python libraries (bibtexparser)

<!-- EOF -->