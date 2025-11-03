<!-- ---
!-- Timestamp: 2025-11-03 16:34:18
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/10_SCITEX_WRITER_03.md
!-- --- -->

# Writer - Collaboration & Commands

## Phase 1: Keyboard Shortcuts & Commands

### Step 1: Investigate Available Keystrokes
- [ ] Document Monaco Editor reserved keys
- [ ] Document browser reserved keys (Ctrl+T, Ctrl+W, etc.)
- [ ] Test keystroke conflicts in actual environment
- [ ] Create "Available Keystrokes" reference doc

### Step 2: Create Modular Command Functions
- [ ] Citation commands
  - [ ] `toggleComment()` - Add/remove % prefix
  - [ ] `quickCite()` - Open BibTeX search modal
  - [ ] `addReference()` - Insert to bibliography

- [ ] LaTeX commands
  - [ ] `wrapBold()` - Wrap selection in `\textbf{}`
  - [ ] `wrapItalic()` - Wrap selection in `\emph{}`
  - [ ] `wrapMath()` - Wrap selection in `$$`

- [ ] Navigation commands
  - [ ] `jumpToSection(index)` - Jump to section 1-7
  - [ ] `navigateSection(direction)` - Up/Down
  - [ ] `showCommandPalette()` - Open palette

### Step 3: Design Keybinding Config Structure
- [ ] Config file location: `.scitex/writer/keybindings.json`
- [ ] Structure: `{ "preset": "emacs", "custom": {...} }`
- [ ] Command registry with default bindings
- [ ] Validation system for conflicts

### Step 4: Implement Keybinding Allocation System
- [ ] Load config from file/database
- [ ] Register commands with Monaco
- [ ] Handle conflicts gracefully
- [ ] Save user customizations

### Step 5: Create Preset Configs
- [ ] Default preset (VS Code-style)
- [ ] Emacs preset
- [ ] Vim preset
- [ ] VS Code preset (explicit)

### Step 6: Settings UI & Discovery
- [ ] Keybindings settings page
- [ ] Preset selector dropdown
- [ ] Custom binding editor
- [ ] Reset to defaults button
- [ ] **`describe-bindings`** (Emacs-style)
  - [ ] Show all active keybindings in searchable list
  - [ ] Group by category (Citation, LaTeX, Navigation, etc.)
  - [ ] Show command name + description + keystroke
  - [ ] Bind to: `Ctrl+H B` (Emacs) or `Ctrl+K Ctrl+S` (VS Code)
  - [ ] Help modal with keyboard shortcut reference

### Step 7: Symbol Insertion System
- [ ] **Auto-replace** (type → symbol)
  - [ ] `-->` → `→` (arrow)
  - [ ] `<--` → `←` (arrow)
  - [ ] `+-` → `±` (plus-minus)
  - [ ] `<=` → `≤` (less than or equal)
  - [ ] `>=` → `≥` (greater than or equal)
  - [ ] `~=` → `≈` (approximately)
  - [ ] `---` → `—` (em-dash)
  - [ ] `--` → `–` (en-dash)

- [ ] **Symbol palette** (click to insert)
  - [ ] Math: `− × ÷ ± ≈ ≤ ≥ ≠ ∞`
  - [ ] Greek: `α β γ δ ε θ λ μ π σ ω`
  - [ ] Arrows: `→ ← ↑ ↓ ↔`
  - [ ] Units: `° µ Å`
  - [ ] Organized by category

- [ ] **Symbol search** (`Ctrl+K`)
  - [ ] Type "arrow" → see `→ ← ↑ ↓`
  - [ ] Type "alpha" → see `α`
  - [ ] Fuzzy search support

## Phase 2: Collaboration Features
- [ ] Presence indicators
  - [ ] Show who's online -> Modern light indicators
  - [ ] Show which section they're viewing -> Yes, in the dropdown section directly (so, only visible when user wants to check unless in the current section)
  - [ ] Colored badges per user -> User icons + color

- [ ] Comments system
  - [ ] Select text → add comment
  - [ ] Threaded discussions
  - [ ] Resolve/reopen comments
  - [ ] `Ctrl+/` - Add comment
  - [ ] `Ctrl+Shift+/` - Resolve thread

- [ ] Change awareness
  - [ ] "New changes available" badge
  - [ ] Pull changes manually
  - [ ] Auto-save sync (30s)

- [ ] DM, shared chat space

## Phase 3: Enhanced Collaboration
- [ ] Voice comments
  - [ ] Record audio note on selection
  - [ ] Play back comments
  - [ ] Async feedback

- [ ] Guest collaborators
  - [ ] Email-only authentication
    - [ ] Accept by organizer with permission settings
  - [ ] No account required

- [ ] Video integration (optional)
  - [ ] "Start video call" button -> Yes, just like slack
  - [ ] Link to Google Meet/Zoom -> Great
  - [ ] Share document URL

## Skip (Use existing tools)
- [ ] ~~Built-in video conferencing~~
- [ ] ~~Real-time text cursors~~
- [ ] ~~Chat system~~

<!-- EOF -->