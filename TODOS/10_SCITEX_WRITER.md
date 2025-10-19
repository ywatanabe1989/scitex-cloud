<!-- ---
!-- Timestamp: 2025-10-20 10:13:42
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/10_SCITEX_WRITER.md
!-- --- -->

## Writer

### Ease of Use
- [ ] User experience first

### Examples
- [ ] Examples as file comments are too much
- [ ] Prepare examples as templates would be beneficial

### Visual Editor
- [ ] Implement Overleaf's visual editor
  - [ ] ./externals/overleaf

### Integration with Scholar
- [ ] Link scholar library
  - [ ] Currently, scholar create library to ~/.scitex/scholar/library
  - [ ] However, in this django app, we need to prepare library to user directory
    - [ ] Maybe ./data/users/<username>/<projectname>/paper/library
- [ ] Implement from scholar library integrated list
  - [ ] Implement drag-drop interface 

### AI Assistant
- [ ] Implement AI assistant
  - [ ] LlamaIndex, specialist for RAG
    - [ ] Tool use may be integrated to directly file handling
- [ ] Handle accept/reject/diff/tracking interfaces

### Multi User edition
- [ ] I need to confirm multi user editing with ywata1989 and wyusuuke
  - [ ] Collaborator
  - [ ] Gues Collaborator (only email auth; like for Professors who may not want to create an account)

### Word integration
- ./10_SCITEX_WRITER_WORD.md
```

---

<!-- EOF -->