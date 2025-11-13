# PDF.js Viewer - Scroll & Zoom Persistence Improvements

**Branch**: `feature/pdfjs-viewer`
**Date**: 2025-11-13
**Author**: Claude Code

## Problem Statement

The iframe-based PDF viewer has a fundamental limitation: we cannot access or control the scroll/zoom state of the browser's native PDF viewer inside the iframe due to cross-origin security restrictions. When users scroll or zoom inside the PDF (Ctrl + middle-mouse drag), we have zero visibility into these changes.

## Solution: PDF.js Canvas Rendering

Switched to PDF.js canvas-based rendering which gives us full programmatic control over:
- Scroll position (vertical and horizontal)
- Zoom level
- Theme/color mode
- Page tracking

## Improvements Implemented

### 1. **Scroll Position Persistence** ✅

**Files Modified**:
- `apps/writer_app/static/writer_app/ts/modules/pdf-viewer-pdfjs.ts`

**What was added**:
- Debounced scroll event listener (saves every 500ms)
- `saveScrollPositionDebounced()` - saves current scroll to localStorage
- `restoreScrollPosition()` - restores scroll after PDF loads/re-renders
- Two-tier restoration:
  1. From temporary save (during re-renders to preserve exact position)
  2. From localStorage (when page reloads)

**How it works**:
```typescript
// User scrolls → Auto-saves after 500ms
viewer.addEventListener("scroll", () => {
  this.saveScrollPositionDebounced(); // → localStorage
});

// PDF loads/re-renders → Restores scroll
this.restoreScrollPosition(); // ← localStorage
```

### 2. **Zoom Level Persistence** ✅

**Files Modified**:
- `apps/writer_app/static/writer_app/ts/modules/pdf-viewer-pdfjs.ts`

**What was added**:
- `restoreSavedZoom()` - called in constructor
- `setScale()` - now saves zoom level to localStorage
- Zoom restored on initialization

**How it works**:
```typescript
// On init: restore saved zoom
constructor() {
  this.restoreSavedZoom(); // 125% → scale 1.25
}

// On zoom change: save to localStorage
setScale(scale) {
  statePersistence.savePdfZoom(scale * 100); // 1.25 → 125%
}
```

### 3. **Scroll Preservation During Re-renders** ✅

**Problem**: Theme changes and zoom adjustments completely re-render the PDF canvas, destroying scroll position.

**Solution**: Save scroll position BEFORE re-render, restore AFTER.

**Files Modified**:
- `apps/writer_app/static/writer_app/ts/modules/pdf-viewer-pdfjs.ts`

**What was added**:
- `savedScrollPosition` private field for temporary storage
- Modified `setColorMode()` to save scroll before re-render
- Modified `setScale()` to save scroll before re-render
- Modified `renderAllPages()` to restore scroll after re-render

**Flow**:
```
User changes theme
 ↓
setColorMode() → Save scroll to this.savedScrollPosition
 ↓
renderAllPages() → Destroy DOM, create new canvas elements
 ↓
restoreScrollPosition() → Check this.savedScrollPosition first
 ↓
✓ Scroll position preserved!
```

### 4. **State Persistence Integration** ✅

**Files Modified**:
- `apps/writer_app/static/writer_app/ts/modules/pdf-viewer-pdfjs.ts` (imports)

**What was added**:
- Import statement for `statePersistence` module
- All scroll/zoom operations use `statePersistence.savePdfScrollPosition()` and `statePersistence.savePdfZoom()`
- Methods already existed in `state-persistence.ts` (no changes needed there)

### 5. **Public Getter Methods** ✅

**Files Modified**:
- `apps/writer_app/static/writer_app/ts/modules/pdf-viewer-pdfjs.ts`

**What was added**:
```typescript
getCurrentScale(): number
getCurrentScrollPosition(): { scrollTop, scrollLeft } | null
getColorMode(): "light" | "dark"
```

**Purpose**: Allow external code to query current PDF viewer state without direct DOM access.

### 6. **CSS Styling** ✅

**Files Modified**:
- `apps/writer_app/static/writer_app/css/components/pdfjs-viewer.css`

**What was added**:
- `.pdfjs-viewer` container styles with scrollable overflow
- Custom scrollbar styling (webkit and Firefox)
- Dark theme support via `[data-theme="dark"]`
- Proper height/width to fill container

## Technical Details

### Scroll Position Save Timing

- **During scrolling**: Debounced 500ms after last scroll event
- **Before re-render**: Immediately saved to `this.savedScrollPosition`
- **After re-render**: Restored via `requestAnimationFrame()` for timing

### Zoom Scale Format

- **Internal storage**: Scale multiplier (0.5 - 3.0)
- **localStorage**: Percentage (50% - 300%)
- **Conversion**: `scale * 100` for save, `zoom / 100` for load

### Priority System for Scroll Restoration

1. **Temporary save** (`this.savedScrollPosition`) - highest priority
   - Used during theme/zoom changes to preserve exact position
   - Cleared after use

2. **localStorage** (`statePersistence.getSavedPdfScrollPosition()`)
   - Used when page reloads
   - Persists across sessions

## Console Logging

Added comprehensive logging for debugging:

```
[PDFJSViewer] Restored saved zoom: 125% scale: 1.25
[PDFJSViewer] ✓ Scroll listener attached, will save position every 500ms
[PDFJSViewer] 💾 Saved scroll position: { scrollTop: 1234, scrollLeft: 0 }
[PDFJSViewer] Saved scroll position before theme change: { scrollTop: 1234, scrollLeft: 0 }
[PDFJSViewer] Restoring scroll from temporary save: { scrollTop: 1234, scrollLeft: 0 }
[PDFJSViewer] ✓ Scroll restored from temporary save
```

## Benefits Over Iframe Approach

| Feature | Iframe | PDF.js |
|---------|--------|--------|
| Scroll position detection | ❌ | ✅ |
| Zoom level detection | ❌ | ✅ |
| Scroll position persistence | ❌ | ✅ |
| Zoom level persistence | ❌ | ✅ |
| Theme control | ❌ | ✅ |
| Page tracking | ❌ | ✅ |
| Programmatic control | ❌ | ✅ |

## Testing Checklist

- [ ] Load PDF - scroll position should restore from localStorage
- [ ] Scroll PDF - position should save every 500ms (check console)
- [ ] Change zoom - position should be preserved
- [ ] Change theme - position should be preserved
- [ ] Reload page - scroll position should restore
- [ ] Reload page - zoom level should restore
- [ ] Multiple PDFs - each should maintain its own scroll/zoom

### 7. **High-DPI / Print Quality Rendering** ✅

**Problem**: Text appeared blurry/pixelated on high-DPI displays and didn't meet user's 300+ DPI requirement.

**Files Modified**:
- `apps/writer_app/static/writer_app/ts/modules/pdf-viewer-pdfjs.ts`

**What was added**:
- `renderQuality` option in constructor (default: 2.0x)
- Combined DPR (device pixel ratio) with quality multiplier
- Canvas rendered at `viewport × DPR × renderQuality` resolution
- Public methods: `setRenderQuality()` and `getRenderQuality()`

**Quality Settings**:
- `1.0` = Standard (72 DPI × DPR) - basic quality
- `2.0` = Default (144 DPI × DPR) - crisp display quality
- `4.0` = Print quality (~300 DPI × DPR) - ultra-sharp
- `5.0` = Maximum (360 DPI × DPR) - print-ready

**Example**:
```typescript
const viewer = new PDFJSViewer({
  containerId: "pdf-container",
  renderQuality: 4.0  // 300+ DPI print quality
});

// On 2x DPR screen: 72 × 2 × 4 = 576 DPI effective resolution
```

**Console Output**:
```
[PDFJSViewer] Rendering page 1 | DPR: 2 | Quality: 4.0x | Total scale: 8.0x | Effective DPI: 576
```

## Next Steps

1. **Integration**: Connect PDFJSViewer to the main PDF preview system
2. **Testing**: Verify all persistence features work correctly
3. **Performance**: Consider virtual scrolling for large PDFs (100+ pages)
4. **Error Handling**: Add graceful fallback if PDF.js CDN fails
5. **Types**: Add proper TypeScript types for PDF.js objects
6. **Quality UI**: Add quality slider in PDF viewer controls (Low/Medium/High/Print)

## Files Changed

### Modified
- `apps/writer_app/static/writer_app/ts/modules/pdf-viewer-pdfjs.ts` (185 lines changed)
- `apps/writer_app/static/writer_app/css/components/pdfjs-viewer.css` (41 lines added)

### Created
- `docs/PDFJS_SCROLL_ZOOM_IMPROVEMENTS.md` (this file)

## Commit Message

```
feat(writer): Implement scroll/zoom persistence for PDF.js viewer

- Add scroll position auto-save (debounced 500ms)
- Add scroll position restore on load and after re-renders
- Add zoom level persistence to localStorage
- Preserve scroll position during theme/zoom changes
- Add CSS styling for pdfjs-viewer container
- Add public getter methods for current state

Fixes the fundamental limitation of iframe-based PDF viewing where
scroll/zoom state is inaccessible due to cross-origin restrictions.

PDF.js canvas rendering provides full programmatic control over
the PDF display state.
```

---

**Status**: ✅ Implementation Complete
**Next**: Integration & Testing
