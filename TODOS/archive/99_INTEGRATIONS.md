<!-- ---
!-- Timestamp: 2025-10-17 22:43:48
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/INTEGRATIONS.md
!-- --- -->

## TODO
We are planning to reduce the barrier for tool switching bidirectionally

### Code Hosting & Version Control
- [ ] GitHub
  - [ ] Import: Sync repository structure, issues/PRs, README/docs, CI configs
  - [ ] Export: Push notebooks, manuscripts, visualizations, auto-commit outputs
  - [ ] Link: OAuth, real-time webhooks, status badges, commit cross-references

- [ ] GitLab
  - [ ] Import: Repository structure, merge requests, wiki pages, pipelines
  - [ ] Export: Code exports, documentation, CI/CD integration
  - [ ] Link: OAuth, webhooks, project mirroring

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

- [ ] Google Docs
  - [ ] Import: Document content, comments, suggestions, version history
  - [ ] Export: Formatted manuscripts, collaborative drafts
  - [ ] Link: Real-time collaborative editing, comment synchronization

### Data & Computation
- [ ] Jupyter Hub/Lab
  - [ ] Import: Notebooks, execution history, kernel configurations
  - [ ] Export: SciTeX-Code notebooks as .ipynb, execution environments
  - [ ] Link: Remote kernel connections, live notebook sync

- [ ] Google Colab
  - [ ] Import: Notebooks, cell outputs, runtime configurations
  - [ ] Export: SciTeX notebooks with reproducibility metadata
  - [ ] Link: Cloud compute integration, GPU/TPU access

- [ ] Kaggle
  - [ ] Import: Datasets, notebooks, competition submissions
  - [ ] Export: Analysis notebooks, competition kernels
  - [ ] Link: Dataset versioning, leaderboard integration

### Cloud Storage
- [ ] Google Drive
  - [ ] Import: Documents, spreadsheets, data files
  - [ ] Export: Manuscripts, analysis reports, figures
  - [ ] Link: Automatic backup, shared folder sync

- [ ] Dropbox
  - [ ] Import: Files, shared folders, paper documents
  - [ ] Export: Project backups, collaboration files
  - [ ] Link: Bidirectional sync, version history

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


## EASY WIN
----------------------------------------
● Looking at these integrations from an "easy win" perspective, here are my recommendations:

  Top Easy Wins:

  1. ORCID (Easiest)

  Why:
  - Simple OAuth flow
  - Read-only API for most use cases
  - Just need to fetch user profile data (name, affiliation, ORCID ID)
  - Auto-populate author fields in SciTeX-Writer
  - High perceived value for minimal effort
  - No complex data transformations needed

  2. Slack/Discord Webhooks (Very Easy)

  Why:
  - Just POST requests to webhook URLs
  - No OAuth complexity
  - One-way communication (export only)
  - Can implement basic notifications in a day:
    - "Project created"
    - "Manuscript updated"
    - "Analysis completed"

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

  5. Import/Export .ipynb (Easy)

  Why:
  - Standard JSON format
  - No API calls needed
  - Just file format conversion
  - Can leverage existing libraries (nbformat)
  - Works for both Jupyter and Colab

  My Recommendation for First Implementation:

  Start with: ORCID + Export .bib + Slack Webhooks

  This combo gives you:
  1. ORCID: Professional researcher identity (looks impressive)
  2. .bib export: Immediate practical value for academics
  3. Slack webhooks: Modern dev/team workflow integration

  All three are:
  - Low complexity
  - High perceived value
  - No bidirectional sync complexity
  - Can be implemented in 1-2 weeks total

  Would you like me to start implementing any of these?

<!-- EOF -->