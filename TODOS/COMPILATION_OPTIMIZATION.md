<!-- ---
!-- Timestamp: 2025-10-17 22:15:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/COMPILATION_OPTIMIZATION.md
!-- --- -->

# SciTeX Writer Compilation Optimization Plan

## Goal
Match or exceed Overleaf's compilation speed (5-10 seconds) while maintaining SciTeX's advanced features (modular structure, diff generation, archiving).

## Current Performance Analysis

### Current Compilation Time Breakdown
**Full compilation:** ~35-40 seconds
- Pre-processing: ~7s
  - Figure processing: 2-5s
  - Table processing: 1-2s
- **LaTeX compilation: 12s** ⚠️ (3 manual passes)
- Post-processing: ~19s
  - Word counting: 6s (container overhead!)
  - Diff generation: 11s (compiles second PDF!)
  - Archiving: 1s
  - Tree generation: 1s

**Quick mode (--quick --no_figs):** ~12 seconds
- Only runs LaTeX compilation
- Still using 3 manual passes

### Overleaf Compilation Time
**Typical:** 5-10 seconds for similar documents

## Root Causes of Slowness

### 1. Manual 3-Pass pdflatex (12s) ⚠️ PRIMARY BOTTLENECK
**Current approach:**
```bash
pdflatex main.tex          # Pass 1: 4s
bibtex compiled            # BibTeX: variable
pdflatex main.tex          # Pass 2: 4s
pdflatex main.tex          # Pass 3: 4s
```

**Problem:** Always runs all 3 passes even when not needed

**Overleaf's approach:**
```bash
latexmk -pdf -interaction=batchmode main.tex
```

**Benefits:**
- Automatically detects if bibtex is needed
- Only runs necessary passes (sometimes just 1!)
- Smarter dependency tracking
- Industry standard tool

### 2. Container/Environment Overhead (6s)
**Evidence from logs:**
```
WARNING: Environment variable CUDA_VISIBLE_DEVICES already has value []...
WARNING: Environment variable PYTHONPATH already has value []...
```
Repeated 6+ times during word counting!

**Cause:** Launching containers/environments for each script execution

### 3. Unnecessary Features During Compile
- **Diff generation:** Compiles a SECOND full PDF (11s)
- **Word counting:** Runs Python in containers (6s)
- **Archiving/versioning:** Not needed for preview
- **Tree generation:** Not needed for preview

### 4. Modular File Collection
**Impact:** Minimal (< 1s)
- Processing 16 separate .tex files is NOT the bottleneck
- File concatenation is fast

## Optimization Strategy

### Phase 1: Switch to latexmk (HIGH PRIORITY) 🚀
**Goal:** Reduce compilation time from 12s to 4-6s
**Timeline:** 1-2 days
**Impact:** 50-60% faster LaTeX compilation

#### Implementation Steps

**1.1: Update compilation_compiled_tex_to_compiled_pdf.sh**
- Replace manual pdflatex passes with latexmk
- Use Overleaf's proven latexmk configuration
- Keep compatibility with existing workflow

**Before:**
```bash
pdflatex -interaction=nonstopmode compiled.tex
bibtex compiled
pdflatex -interaction=nonstopmode compiled.tex
pdflatex -interaction=nonstopmode compiled.tex
```

**After:**
```bash
latexmk -pdf \
    -interaction=batchmode \
    -jobname=compiled \
    -synctex=1 \
    -time \
    -f \
    compiled.tex
```

**1.2: Add latexmk configuration file**
Create `.latexmkrc` in paper directory:
```perl
# SciTeX Writer latexmk configuration
# Based on Overleaf's proven setup

$pdf_mode = 1;                    # Generate PDF via pdflatex
$postscript_mode = 0;             # Don't generate PostScript
$dvi_mode = 0;                    # Don't generate DVI

# Compiler settings
$pdflatex = 'pdflatex -synctex=1 -interaction=batchmode -file-line-error %O %S';

# BibTeX settings
$bibtex_use = 2;                  # Run bibtex when needed

# Output directory
$out_dir = '.';
$aux_dir = '.';

# Number of passes
$max_repeat = 5;                  # Max LaTeX passes

# Clean up
$clean_ext = 'synctex.gz run.xml';
```

**1.3: Update command_switching.src**
Add latexmk command detection alongside pdflatex:
```bash
get_cmd_latexmk() {
    # Check for latexmk in: native, module, container
    # Similar to existing get_cmd_pdflatex
}
```

**1.4: Fallback support**
Keep pdflatex 3-pass as fallback if latexmk not available:
```bash
if command -v latexmk &> /dev/null; then
    use_latexmk_compilation
else
    use_legacy_pdflatex_compilation
fi
```

#### Expected Results
- **Compilation time:** 12s → 4-6s (50-60% faster)
- **Smart passes:** Only runs bibtex when citations change
- **First compile:** 3 passes (~6s)
- **Recompile (no bib changes):** 1 pass (~2s)
- **Text-only changes:** 1-2 passes (~3s)

---

### Phase 2: Eliminate Container Overhead (MEDIUM PRIORITY)
**Goal:** Reduce word counting from 6s to < 1s
**Timeline:** 2-3 days
**Impact:** Only affects full compilation (skip in quick mode anyway)

#### Implementation Options

**Option A: Native texcount (Recommended)**
```bash
# Instead of running in container
texcount -brief -nosub main.tex
```

**Option B: Persistent container**
```bash
# Reuse same container instance
docker exec scitex-latex texcount ...
```

**Option C: Skip word count in real-time**
- Only count words on demand (separate button)
- Or run asynchronously after PDF is ready

---

### Phase 3: Incremental Compilation (LOW PRIORITY)
**Goal:** Only recompile changed sections
**Timeline:** 1 week
**Impact:** Moderate (works best for large documents)

#### Approach
1. Track file modification times
2. Use latexmk's built-in dependency tracking
3. Cache compilation artifacts (.aux, .bbl)
4. Only regenerate affected outputs

**Implementation:**
- latexmk already does this automatically!
- Just need to preserve .aux and .bbl files between compiles
- Don't clean between consecutive compiles

---

### Phase 4: Parallel Diff Generation (MEDIUM PRIORITY)
**Goal:** Don't block main PDF on diff generation
**Timeline:** 1 day
**Impact:** User gets PDF faster, diff comes later

#### Current Flow
```
Compile main PDF (12s) → Wait → Compile diff PDF (11s) → Total: 23s
```

#### Optimized Flow
```
Compile main PDF (12s) → Return to user immediately
    └─> Generate diff in background (11s) → Notify when ready
```

**Implementation:**
- Return main PDF as soon as ready
- Start diff compilation in background task
- Send WebSocket notification when diff is ready
- Show "Diff generating..." indicator in UI

---

## Implementation Plan

### Week 1: latexmk Integration
- [x] Quick mode with --quick flag (DONE!)
- [x] Parallel pre/post-processing (DONE!)
- [ ] Research latexmk configuration from Overleaf
- [ ] Create .latexmkrc for SciTeX-Writer template
- [ ] Update compilation_compiled_tex_to_compiled_pdf.sh
- [ ] Add latexmk command detection
- [ ] Test with existing projects
- [ ] Add fallback to pdflatex if latexmk unavailable

### Week 2: Container Optimization
- [ ] Benchmark word counting overhead
- [ ] Implement native texcount support
- [ ] Test persistent container approach
- [ ] Update count_words.sh module
- [ ] Verify word counts match previous implementation

### Week 3: Async Diff Generation
- [ ] Move diff generation to background task
- [ ] Add WebSocket notification for diff completion
- [ ] Update UI to show diff status
- [ ] Test with concurrent users

### Week 4: Testing & Refinement
- [ ] Performance testing across different document sizes
- [ ] Edge case testing (missing bib file, etc.)
- [ ] Verify all features still work
- [ ] Update documentation

---

## Expected Performance Improvements

### After Phase 1 (latexmk)
**Quick mode:**
- Current: ~12s (3-pass pdflatex)
- Target: ~4-6s (smart latexmk)
- **Improvement: 2-3x faster** ⚡

**Full mode:**
- Current: ~35-40s
- Target: ~20-25s (latexmk + parallel processing)
- **Improvement: 40-50% faster**

### After Phase 2 (container optimization)
**Full mode:**
- Target: ~15-20s (latexmk + native tools + parallel)
- **Improvement: 50-60% faster than current**

### After Phase 3 (incremental + async diff)
**Incremental recompile:**
- Target: ~2-3s (latexmk incremental, PDF returned immediately)
- **Improvement: 10x faster than current for minor edits** ⚡⚡⚡

---

## Comparison with Overleaf

### Current State
| Feature | SciTeX-Writer (Current) | Overleaf |
|---------|------------------------|----------|
| First compile | 35-40s | 8-12s |
| Quick compile | 12s | 5-8s |
| Recompile (minor edit) | 35-40s | 3-5s |
| Tool | Manual pdflatex | latexmk |

### After Optimization (All Phases)
| Feature | SciTeX-Writer (Optimized) | Overleaf |
|---------|--------------------------|----------|
| First compile | 15-20s | 8-12s |
| Quick compile | 4-6s | 5-8s |
| Recompile (minor edit) | 2-3s | 3-5s |
| Tool | latexmk + optimizations | latexmk |

**Result:** Competitive with or better than Overleaf!

---

## Technical Details

### latexmk Command Comparison

**Overleaf (from LatexRunner.js:166-175):**
```bash
latexmk \
    -cd \
    -jobname=output \
    -auxdir=$COMPILE_DIR \
    -outdir=$COMPILE_DIR \
    -synctex=1 \
    -interaction=batchmode \
    -time \
    -f \
    -pdf \
    main.tex
```

**Flags explained:**
- `-cd`: Change to directory containing main file
- `-jobname=output`: Name output files as "output.pdf"
- `-auxdir`/`-outdir`: Specify output directories
- `-synctex=1`: Generate SyncTeX data (for PDF↔source sync)
- `-interaction=batchmode`: Non-interactive mode
- `-time`: Record compilation time statistics
- `-f`: Force continue despite errors
- `-pdf`: Use pdflatex to generate PDF

**SciTeX adaptation:**
```bash
latexmk \
    -pdf \
    -interaction=batchmode \
    -synctex=1 \
    -time \
    -f \
    -auxdir=. \
    -outdir=. \
    compiled.tex
```

### Container Strategy

**Current issue:**
Multiple scripts launch containers repeatedly, causing environment variable conflicts.

**Solutions:**

**Option A: Native installation**
```bash
# Check for native latexmk first
if command -v latexmk &> /dev/null; then
    latexmk ...
elif [ -f "$SCITEX_CONTAINER" ]; then
    docker exec scitex-latex latexmk ...
fi
```

**Option B: Persistent container session**
```bash
# Start persistent container once
docker run -d --name scitex-latex-session ...

# Reuse for all commands
docker exec scitex-latex-session pdflatex ...
docker exec scitex-latex-session bibtex ...
docker exec scitex-latex-session texcount ...

# Cleanup when done
docker stop scitex-latex-session
```

---

## File Structure Changes

### Files to Modify (in scitex_template_research)

1. **`paper/scripts/shell/modules/compilation_compiled_tex_to_compiled_pdf.sh`**
   - Replace pdflatex 3-pass with latexmk
   - Add fallback to legacy approach
   - Update timing logic

2. **`paper/scripts/shell/modules/command_switching.src`**
   - Add `get_cmd_latexmk()` function
   - Check native → module → container

3. **`paper/.latexmkrc`** (NEW)
   - Configure latexmk behavior
   - Set compiler, bibtex handling, passes

4. **`paper/scripts/shell/modules/count_words.sh`**
   - Add native texcount detection
   - Avoid container if possible

5. **`paper/scripts/shell/compile_manuscript.sh`**
   - Already updated with --quick flag ✅
   - Already has parallel processing ✅

### Files to Modify (in scitex-cloud Django)

1. **`apps/writer_app/views.py`**
   - Already updated with quick mode ✅
   - No changes needed

2. **`apps/writer_app/templates/writer_app/project_writer.html`**
   - Already has quick compile button ✅
   - No changes needed

---

## Testing Strategy

### Unit Tests
1. Test latexmk with simple document
2. Test latexmk with bibliography
3. Test latexmk with figures
4. Test fallback to pdflatex
5. Test incremental recompilation

### Integration Tests
1. Quick mode end-to-end
2. Full mode with all features
3. Concurrent compilation (multiple users)
4. Error handling (missing .bib, syntax errors)

### Performance Benchmarks
1. Document sizes:
   - Small (< 10 pages): Target < 3s
   - Medium (10-30 pages): Target < 6s
   - Large (> 30 pages): Target < 10s

2. Scenarios:
   - First compile (cold cache)
   - Recompile (warm cache)
   - Text-only change
   - Bibliography change
   - Figure change

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| latexmk not available on server | HIGH | Keep pdflatex fallback, check in CI |
| latexmk behaves differently | MEDIUM | Extensive testing, use Overleaf config |
| Breaking existing workflows | MEDIUM | Gradual rollout, feature flag |
| Cache corruption | LOW | Clear cache on errors, versioned backups |
| Incremental compilation bugs | MEDIUM | Disable for critical submissions |

---

## Implementation Phases

### Phase 1: latexmk Integration (Priority: P0)
**Timeline:** Week 1
**Target:** Quick compile: 12s → 4-6s

**Tasks:**
1. Create .latexmkrc configuration file
2. Update compilation_compiled_tex_to_compiled_pdf.sh to use latexmk
3. Add get_cmd_latexmk() to command_switching.src
4. Implement fallback to pdflatex
5. Test with existing projects
6. Update documentation

**Deliverables:**
- `.latexmkrc` in template
- Modified `compilation_compiled_tex_to_compiled_pdf.sh`
- Test results showing performance improvement

### Phase 2: Container Optimization (Priority: P1)
**Timeline:** Week 2
**Target:** Word count: 6s → < 1s

**Tasks:**
1. Benchmark current word counting
2. Add native texcount detection
3. Implement persistent container session
4. Update count_words.sh module
5. Test accuracy vs old approach

**Deliverables:**
- Modified `count_words.sh`
- Performance benchmarks
- Accuracy verification

### Phase 3: Async Diff Generation (Priority: P1)
**Timeline:** Week 3
**Target:** User gets PDF immediately, diff comes later

**Tasks:**
1. Refactor diff generation as background task
2. Add WebSocket notification system
3. Update UI to show diff status
4. Handle diff errors gracefully

**Deliverables:**
- Background diff generation
- WebSocket notification
- Updated UI with status indicator

### Phase 4: Incremental Compilation (Priority: P2)
**Timeline:** Week 4
**Target:** Recompiles in 2-3s

**Tasks:**
1. Preserve compilation artifacts between runs
2. Test latexmk's incremental features
3. Add cache management
4. Verify correctness

**Deliverables:**
- Incremental compilation working
- Cache management system
- Performance benchmarks

---

## Success Metrics

### Performance Targets
- ✅ Quick compile: < 6s (currently 12s)
- ✅ Full compile: < 20s (currently 35-40s)
- ✅ Incremental recompile: < 3s
- ✅ Match Overleaf speed for small-medium documents
- ✅ Exceed Overleaf with advanced features (diff, versioning)

### User Experience
- ✅ Compilation feels instant for quick mode
- ✅ Progress feedback during compilation
- ✅ Clear distinction between quick/full compile
- ✅ No regression in features or accuracy

### Technical Quality
- ✅ All existing tests pass
- ✅ Compilation output identical to current approach
- ✅ Error handling maintained
- ✅ Backward compatible with existing projects

---

## Configuration Files Reference

### Overleaf's latexmkrc
Location: `externals/overleaf/server-ce/config/latexmkrc`

Key settings to adopt:
- PDF mode configuration
- Interaction settings
- Auxiliary directory handling
- Clean up rules

### SciTeX-Writer Current Scripts
Base: `~/proj/scitex_template_research/paper/scripts/shell/`

Key files:
- `compile_manuscript.sh` - Main entry point
- `modules/compilation_compiled_tex_to_compiled_pdf.sh` - Needs latexmk
- `modules/command_switching.src` - Command detection
- `modules/count_words.sh` - Needs optimization

---

## Next Actions

### Immediate (This Week)
1. Review Overleaf's latexmkrc configuration
2. Create SciTeX-Writer .latexmkrc
3. Update compilation_compiled_tex_to_compiled_pdf.sh
4. Test with neurovista project

### Short-term (Week 2-3)
1. Optimize word counting
2. Implement async diff generation
3. Update Django backend if needed

### Long-term (Week 4+)
1. Incremental compilation
2. Advanced caching strategies
3. Performance monitoring dashboard

---

## Questions to Resolve

1. Should we support multiple LaTeX engines (XeLaTeX, LuaLaTeX)?
   - Overleaf supports this with compiler flags
   - Current: Only pdflatex

2. Should word counting be on-demand only?
   - Pro: Faster compilation
   - Con: Users might expect it

3. Should diff be optional/on-demand?
   - Pro: Faster default compilation
   - Con: Useful for version tracking

4. Cache management strategy?
   - How long to keep .aux files?
   - When to force clean rebuild?

---

## References

- Overleaf CLSI service: `./externals/overleaf/services/clsi/`
- CompileManager.js: Main compilation orchestration
- LatexRunner.js: latexmk command building
- Current template: `~/proj/scitex_template_research/paper/`

<!-- EOF -->
