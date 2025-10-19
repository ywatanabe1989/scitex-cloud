<!-- ---
<<<<<<< HEAD
!-- Timestamp: 2025-10-20 10:08:40
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/00_OUR_CODE_REFERENCES.md
!-- --- -->

## Our Actual locally working code references

```
SCITEX_SCHOLAR="$HOME/proj/scitex-code/src/scitex/scholar"
SCITEX_WRITER="$HOME/proj/neurovista/paper"
SCITEX_CODE="$HOME/proj/scitex-code/src/scitex"
SCITEX_VIZ="$HOME/win/documents/SciTeX-Viz"
SCITEX_ENGINE="$HOME/.emacs.d/lisp/emacs-claude-code"
SCITEX_CLOUD="$HOME/proj/scitex-cloud"
```

## Research Proposals Submitted
```
RISE_DIR="$HOME/proj/grant/2025-07-XX---2026-04-2030-03---NN-PERC---500---SMBC-RISE-PROJECT/drafts"
=======
!-- Timestamp: 2025-10-16 21:00:24
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODO.md
!-- --- -->

## TODO

#### Writer



## Code references

```
SCITEX_SCHOLAR="$HOME/proj/scitex_repo/src/scitex/scholar"
# https://github.com/ywatanabe1989/scitex
SCITEX_WRITER="$HOME/proj/neurovista/paper"
SCITEX_CODE="$HOME/proj/scitex_repo/src/scitex"
SCITEX_VIZ="$HOME/win/documents/SciTeX-Viz"
SCITEX_ENGINE="$HOME/.emacs.d/lisp/emacs-claude-code"
SCITEX_CLOUD="$HOME/proj/scitex-cloud"

RISE_DIR="$HOME/proj/grant/2025-07-XX---2026-04-2030-03---NN-PERC---500---SMBC-RISE-PROJECT/drafts"

>>>>>>> eceef43b75a04385549d09f1d8dc7f9cb808b57e
SCITEX_PROPOSAL_JST_BOOST="$RISE_DIR/JST_BOOST_申請書_Human-in-the-Environment 型論文執筆自動化システムの開発_渡邉裕亮.pdf"
SCITEX_PROPOSAL_SMBC_RISE="$RISE_DIR/SMBC_RISE_PROJECT_申請書_論文執筆自動化システム SciTeX の事業化_渡邉裕亮.pdf"
SCITEX_SCHOLAR_CROSSREF_LOCAL="/mnt/nas_ug/crossref_local"
```
<<<<<<< HEAD
- [ ] Will receive their feedback/decision after 21 Oct 2025
=======

## Documentation building
Directories below is associated with `.env` and when cd there, `source .env/bin/activate` called. They are installed via `pip install -e .`
cd $SCITEX_SCHOLAR="$HOME/proj/scitex_repo/src/scitex/scholar"
cd $SCITEX_WRITER="$HOME/proj/neurovista/paper"
cd $SCITEX_CODE="$HOME/proj/scitex_repo/"
cd $SCITEX_VIZ="$HOME/win/documents/SciTeX-Viz"
cd $SCITEX_ENGINE="$HOME/.emacs.d/lisp/emacs-claude-code"
cd $SCITEX_CLOUD="$HOME/proj/scitex-cloud"

We need to prepare docs in docs_app and add link to the landing page: /home/ywatanabe/proj/scitex-cloud/apps/cloud_app/templates/cloud_app/landing_partials/landing_demos.html
Now, the docs of writer and viz are rendered; however, the footer is not in the bottom; the width of the main contents is narrow
Regarding scitex code and scholar; no, they are not rendered.
When side panel contents clicked, the positionnig of the main contents are wrong; they are overlapped with the side bar
>>>>>>> eceef43b75a04385549d09f1d8dc7f9cb808b57e

<!-- EOF -->