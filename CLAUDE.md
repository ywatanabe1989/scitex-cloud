<!-- ---
!-- Timestamp: 2025-10-24 01:37:55
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/CLAUDE.md
!-- --- -->


See `./docs/SciTeX-Ecosystem-and-Corresponding-Local-Directories.md` as well

## THE USER IS ONLY ALLOWED TO EDIT THIS FILE. DO NOT MODIFY THIS FILE UNLESS EXPLICITLY ASKED.

## No comprehensive
- When you say comprehensive, it can be translated into "I will create xxx which is really hard for humans to undersntad"
## Simple Documents
- Keep documents necessary and sufficient. Too much information may do more harm than good.

## Research proposal for this project, SciTeX
See `./docs/BOOST_応募済み申請書_26151429_oubo_20250626.pdf`
However, we are also thinking monetization strategies. `./docs/MONETIZATION_STRATEGY_IMPLEMENTATION.md`

## Project-centric application
The SciTeX ecosystem is project-centric; scholar, code, viz, writer should be linked to a project of the user or a group. However, basic functionalities should be offered to anonymous users or users with no projects associated.

## Environmental Variables
You can check environmental variables by `env | grep SCITEX_` and use them, including passwords and auth info, as you want. Also, you can export new ones. `.venv` or `./deployment/dotenvs/dotenv_{dev,prod}` will be useful
`/home/ywatanabe/proj/scitex-cloud/.venv`

## No fake data
When error raised, show them as alert on the website. Fake operations will raise critical issues.

## Django Directory Structure
Use `./apps/XXX_app/` format
Follow `./apps/README.md`
Do not place any files under project root directory

## Design Theme of the website
See `./apps/dev_app`
See `/dev/design/`

## Debugging Javascripts
Add console.log for debugging

## Scholar App - Enrichment
- [x] API call shell script: apps/scholar_app/examples/enrich_bibtex.sh
  - [ ] /home/ywatanabe/proj/scitex-code/src/scitex/cli/cloud.py to allow `$ scitex cloud enrich -i orig.bib -o enriched.bib`
  - [ ] scitex cloud enrich -i orig.bib -o enriched.bib -a $SCITEX_CLOUD_API_KEY
  - [ ] Add this to the API doc as well


``` shell
curl https://scitex.cloud/scholar/api/bibtex/enrich/ \
  -H "Authorization: Bearer <YOUR_SCHOLAR_API_KEY>" \
  -i original.bib \
  -o enriched.bib
```

- [ ] How to save project should be handled
  - [ ] project_dir/scitex/scholar/bib_files/xxx_original-<timestamp>.bib
  - [ ] project_dir/scitex/scholar/bib_files/xxx_enriched-<timestamp>.bib
  - [ ] Please check ~/proj/scitex-code/src/scitex/template/create_paper_directory.py
  - [ ] Try `python -m scitex.template create_paper_directory test_paper_structure`
  - [ ] I think to reduce the risk of name space conflict, we should specify:
    - [ ] project_dir/scitex_writer/shared/bib_files/
    - [ ] But is this directory name , scitex_writer, strange?
    - [ ] But since `import scitex` is available, just scitex will conflict
    - [ ] But since writer (latex compilation system) should be installed,... well, ...
    - [ ] is simply `project-dir/scitex/shared/...` better? when they `import scitex` in python script from their project root, is it not problematic unless there are no __init__.py file in the scitex dir?
`project-root/scitex/writer/shared/...`

- [ ] Scholar (http://127.0.0.1:8000/scholar/#bibtex)
  - [ ] Save to project workflow needs update
    - [ ] No preview needed
    - [ ] The history bib cards should have two distinct buttons; download / save to project
      - [ ] clicking card and automatic download is unexpected to the user

      - [ ] (Save to button; label=Save to: )[drowpdown]
        - [ ] in the same height
        - [ ] (Save to:|[dropdown] <- could you make the Save to: part of button colored?
        - [ ] Also, i think this should be placed in the most left side
        - [ ] also, auto-download might be unexpected so that we might only allow for the download button
also, the layout of Download button in the main panel seems not aligned; please check aesthetics (http://127.0.0.1:8000/scholar/#bibtex)
        - [ ] perffect! save to button to green, as it is success!
        - [ ] great, is it possible to change the color of dropdown here to align with the green color?

- [ ] Create new project, new-project, failed silently; why?
- [ ] is gitea not running?
actually, i cannot still create new-project. Anyway, silent failure is not good.


- [ ] Difficult logics should be in scitex-code `~/proj/scitex-code/src/scitex`, which has source of python scitex package (`import scitex`)
  - [ ] project_app
    - [ ] SciTeXProject dataclass and maintainance functionalities can be implemented in `~/proj/scitex-code/src/scitex/project`
    - [ ] One-to-one relationships between local <-> django <-> gitea projects
    - [ ] scitex should be designed to work standalone even without django nor gitea
    - [ ] Each project should be self-contained just like github
    - [ ] `scitex.{cli,cloud,template,scholar,viz}` will be highly related
    - [ ] project-root/scitex/{writer,scholar,code,viz,metadata}

- [ ] This is `scitex.writer`: `/tmp/scitex-writer/`
  - [ ] Available from `git@github.com/ywatanabe1989/scitex-writer`
  - [ ] However, the pip scitex package, scitex-code, does not include writer yet as `scitex-writer` is shell scripts main project.
  - [ ] However, for portability and consistency, we would be better to available from `scitex.writer` python module as well. Although I am not sure whether shell scripts and python are compatible...

<!-- EOF -->