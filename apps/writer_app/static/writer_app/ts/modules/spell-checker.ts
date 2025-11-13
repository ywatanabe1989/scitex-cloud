/**
 * Spell Checker Module for Monaco Editor
 *
 * Provides lightweight spell checking for LaTeX documents using Typo.js
 * (Hunspell dictionaries). Intelligently skips LaTeX commands, math environments,
 * and special syntax while checking regular text.
 */

// Import Typo.js - it's a UMD module, so we access it from window
declare global {
  interface Window {
    Typo: any;
  }
}

export interface SpellCheckConfig {
  enabled: boolean;
  language: string; // e.g., 'en-US', 'en-GB'
  skipLaTeXCommands: boolean;
  skipMathMode: boolean;
  skipCodeBlocks: boolean;
  customDictionary?: string[]; // Words to always consider correct
}

export class SpellChecker {
  private monaco: any;
  private editor: any;
  private config: SpellCheckConfig;
  private decorationsCollection: any;
  private spellingCache: Map<string, boolean> = new Map();
  private customWords: Set<string> = new Set();
  private checkingEnabled: boolean = true;
  private dictionary: any = null;
  private dictionaryLoading: boolean = false;
  private dictionaryLoaded: boolean = false;
  private supplementaryWords: Set<string> = new Set();

  // LaTeX patterns to skip
  private readonly LATEX_COMMAND_REGEX = /\\[a-zA-Z@]+/g;
  private readonly LATEX_INLINE_MATH = /\$[^$]+\$/g;
  private readonly LATEX_DISPLAY_MATH = /\$\$[^$]+\$\$/g;
  private readonly LATEX_ENV_MATH = /\\begin\{(equation|align|gather|multline|displaymath)\*?\}[\s\S]*?\\end\{\1\*?\}/g;
  private readonly CITATION_REGEX = /\\cite[tp]?\{[^}]+\}/g;
  private readonly REF_REGEX = /\\(ref|label|eqref)\{[^}]+\}/g;

  constructor(monaco: any, editor: any, config: Partial<SpellCheckConfig> = {}) {
    this.monaco = monaco;
    this.editor = editor;
    this.config = {
      enabled: true,
      language: 'en-US',
      skipLaTeXCommands: true,
      skipMathMode: true,
      skipCodeBlocks: true,
      ...config,
    };

    // Initialize custom dictionary
    if (this.config.customDictionary) {
      this.customWords = new Set(this.config.customDictionary.map(w => w.toLowerCase()));
    }

    // Create decorations collection
    this.decorationsCollection = this.editor.createDecorationsCollection();

    // Initialize Typo.js dictionary
    this.initializeDictionary();

    console.log('[SpellChecker] Initialized with config:', this.config);
  }

  /**
   * Initialize Typo.js dictionary by loading .aff and .dic files
   */
  private async initializeDictionary(): Promise<void> {
    if (this.dictionaryLoading || this.dictionaryLoaded) {
      return;
    }

    this.dictionaryLoading = true;
    console.log('[SpellChecker] Loading dictionary files...');

    try {
      const lang = this.config.language.replace('-', '_'); // en-US -> en_US
      const basePath = '/static/writer_app/dictionaries';

      // Load .aff and .dic files
      const [affResponse, dicResponse] = await Promise.all([
        fetch(`${basePath}/${lang}.aff`),
        fetch(`${basePath}/${lang}.dic`)
      ]);

      if (!affResponse.ok || !dicResponse.ok) {
        throw new Error(`Failed to load dictionary files: ${affResponse.status}, ${dicResponse.status}`);
      }

      const affData = await affResponse.text();
      const dicData = await dicResponse.text();

      // Check if Typo is available
      if (!window.Typo) {
        console.error('[SpellChecker] Typo.js not loaded! Loading from CDN...');
        await this.loadTypoFromCDN();
      }

      // Initialize Typo dictionary
      this.dictionary = new window.Typo(lang, affData, dicData);
      this.dictionaryLoaded = true;
      this.dictionaryLoading = false;

      console.log('[SpellChecker] ✓ Dictionary loaded successfully');

      // Re-check spelling now that dictionary is loaded
      if (this.checkingEnabled) {
        this.checkSpelling();
      }
    } catch (error) {
      console.error('[SpellChecker] Failed to load dictionary:', error);
      console.warn('[SpellChecker] Falling back to permissive mode');
      this.dictionaryLoading = false;
    }
  }

  /**
   * Load Typo.js from CDN if not already available
   */
  private async loadTypoFromCDN(): Promise<void> {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/typo-js@1.2.4/typo.js';
      script.onload = () => {
        console.log('[SpellChecker] Typo.js loaded from CDN');
        resolve();
      };
      script.onerror = () => {
        reject(new Error('Failed to load Typo.js from CDN'));
      };
      document.head.appendChild(script);
    });
  }

  /**
   * Start spell checking
   */
  enable(): void {
    if (!this.config.enabled) {
      console.log('[SpellChecker] Spell checking is disabled');
      return;
    }

    this.checkingEnabled = true;

    // Check on content change (debounced)
    let debounceTimer: number | undefined;
    this.editor.onDidChangeModelContent(() => {
      if (!this.checkingEnabled) return;

      if (debounceTimer) {
        clearTimeout(debounceTimer);
      }

      debounceTimer = window.setTimeout(() => {
        this.checkSpelling();
      }, 500); // 500ms debounce
    });

    // Initial check (will wait for dictionary if not loaded)
    this.checkSpelling();

    // Register code action provider for spelling suggestions
    this.registerCodeActionProvider();

    console.log('[SpellChecker] Enabled');
  }

  /**
   * Manually trigger spell checking (useful for re-checking existing content)
   */
  recheckAll(): void {
    if (this.checkingEnabled) {
      console.log('[SpellChecker] Manually re-checking all content');
      this.checkSpelling();
    }
  }

  /**
   * Disable spell checking
   */
  disable(): void {
    this.checkingEnabled = false;
    this.decorationsCollection.clear();
    console.log('[SpellChecker] Disabled');
  }

  /**
   * Main spell checking logic
   */
  private async checkSpelling(): Promise<void> {
    if (!this.checkingEnabled) return;

    const model = this.editor.getModel();
    if (!model) return;

    const content = model.getValue();
    const misspelledRanges: any[] = [];

    // Extract checkable text regions
    const textRegions = this.extractCheckableRegions(content);

    // Check each word in each region
    for (const region of textRegions) {
      const words = this.extractWords(region.text);

      for (const word of words) {
        const isCorrect = await this.isWordCorrect(word.text);

        if (!isCorrect) {
          // Calculate absolute position in document
          const startPos = model.getPositionAt(region.startOffset + word.startIndex);
          const endPos = model.getPositionAt(region.startOffset + word.endIndex);

          misspelledRanges.push({
            range: new this.monaco.Range(
              startPos.lineNumber,
              startPos.column,
              endPos.lineNumber,
              endPos.column
            ),
            options: {
              isWholeLine: false,
              className: 'spell-error',
              glyphMarginClassName: '',
              hoverMessage: { value: `**Spelling**: "${word.text}" may be misspelled` },
              overviewRuler: {
                color: 'rgba(255, 0, 0, 0.3)',
                position: this.monaco.editor.OverviewRulerLane.Right,
              },
              minimap: {
                color: 'rgba(255, 0, 0, 0.3)',
                position: this.monaco.editor.MinimapPosition.Inline,
              },
              // Red squiggly underline
              inlineClassName: 'spell-error-inline',
            },
          });
        }
      }
    }

    // Apply decorations
    this.decorationsCollection.set(misspelledRanges);

    console.log(`[SpellChecker] Found ${misspelledRanges.length} potential spelling errors`);
  }

  /**
   * Extract regions of text that should be spell-checked
   * (skipping LaTeX commands, math mode, etc.)
   */
  private extractCheckableRegions(content: string): Array<{ text: string; startOffset: number }> {
    const regions: Array<{ text: string; startOffset: number }> = [];

    // Build list of ranges to skip
    const skipRanges: Array<{ start: number; end: number }> = [];

    if (this.config.skipLaTeXCommands) {
      // Skip LaTeX commands
      let match;
      while ((match = this.LATEX_COMMAND_REGEX.exec(content)) !== null) {
        skipRanges.push({ start: match.index, end: match.index + match[0].length });
      }
    }

    if (this.config.skipMathMode) {
      // Skip inline math
      let match;
      const inlineMathRegex = new RegExp(this.LATEX_INLINE_MATH.source, 'g');
      while ((match = inlineMathRegex.exec(content)) !== null) {
        skipRanges.push({ start: match.index, end: match.index + match[0].length });
      }

      // Skip display math
      const displayMathRegex = new RegExp(this.LATEX_DISPLAY_MATH.source, 'g');
      while ((match = displayMathRegex.exec(content)) !== null) {
        skipRanges.push({ start: match.index, end: match.index + match[0].length });
      }

      // Skip math environments
      const envMathRegex = new RegExp(this.LATEX_ENV_MATH.source, 'g');
      while ((match = envMathRegex.exec(content)) !== null) {
        skipRanges.push({ start: match.index, end: match.index + match[0].length });
      }
    }

    // Skip citations and references
    const citationRegex = new RegExp(this.CITATION_REGEX.source, 'g');
    let match;
    while ((match = citationRegex.exec(content)) !== null) {
      skipRanges.push({ start: match.index, end: match.index + match[0].length });
    }

    const refRegex = new RegExp(this.REF_REGEX.source, 'g');
    while ((match = refRegex.exec(content)) !== null) {
      skipRanges.push({ start: match.index, end: match.index + match[0].length });
    }

    // Sort and merge overlapping ranges
    skipRanges.sort((a, b) => a.start - b.start);
    const mergedSkipRanges = this.mergeRanges(skipRanges);

    // Extract checkable regions (everything not in skip ranges)
    let currentPos = 0;
    for (const skipRange of mergedSkipRanges) {
      if (currentPos < skipRange.start) {
        const text = content.substring(currentPos, skipRange.start);
        regions.push({ text, startOffset: currentPos });
      }
      currentPos = skipRange.end;
    }

    // Add final region
    if (currentPos < content.length) {
      const text = content.substring(currentPos);
      regions.push({ text, startOffset: currentPos });
    }

    return regions;
  }

  /**
   * Merge overlapping ranges
   */
  private mergeRanges(ranges: Array<{ start: number; end: number }>): Array<{ start: number; end: number }> {
    if (ranges.length === 0) return [];

    const merged: Array<{ start: number; end: number }> = [ranges[0]];

    for (let i = 1; i < ranges.length; i++) {
      const current = ranges[i];
      const last = merged[merged.length - 1];

      if (current.start <= last.end) {
        // Overlapping, merge
        last.end = Math.max(last.end, current.end);
      } else {
        // Non-overlapping, add new range
        merged.push(current);
      }
    }

    return merged;
  }

  /**
   * Extract individual words from text
   */
  private extractWords(text: string): Array<{ text: string; startIndex: number; endIndex: number }> {
    const words: Array<{ text: string; startIndex: number; endIndex: number }> = [];

    // Match words (including contractions like "don't", "it's")
    const wordRegex = /\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b/g;
    let match;

    while ((match = wordRegex.exec(text)) !== null) {
      words.push({
        text: match[0],
        startIndex: match.index,
        endIndex: match.index + match[0].length,
      });
    }

    return words;
  }

  /**
   * Check if a word is spelled correctly
   * Uses browser's native spell check API (experimental)
   */
  private async isWordCorrect(word: string): Promise<boolean> {
    // Skip very short words (1-2 chars)
    if (word.length <= 2) return true;

    // Skip capitalized words (likely proper nouns)
    if (word[0] === word[0].toUpperCase() && word.slice(1) === word.slice(1).toLowerCase()) {
      return true;
    }

    // Check custom dictionary
    if (this.customWords.has(word.toLowerCase())) {
      return true;
    }

    // Check cache
    const cacheKey = word.toLowerCase();
    if (this.spellingCache.has(cacheKey)) {
      return this.spellingCache.get(cacheKey)!;
    }

    // Use browser's experimental spell check API if available
    // Note: This is not widely supported yet, so we fall back to a simple check
    let isCorrect = true;

    // For now, we'll use a simple heuristic: common English words are correct
    // In production, you'd integrate with a proper spell check library like Typo.js or Nspell
    isCorrect = await this.checkWordWithBrowser(word);

    // Cache result
    this.spellingCache.set(cacheKey, isCorrect);

    return isCorrect;
  }

  /**
   * Check word using Typo.js dictionary
   */
  private async checkWordWithBrowser(word: string): Promise<boolean> {
    const lowerWord = word.toLowerCase();

    // Skip very short words (likely articles, prepositions)
    if (word.length <= 2) {
      return true;
    }

    // Accept words with numbers (like "figure1", "table2", "2020")
    if (/\d/.test(word)) {
      return true;
    }

    // Accept hyphenated words - check each part separately
    if (word.includes('-')) {
      const parts = word.split('-');
      // If all parts are valid, accept the whole word
      for (const part of parts) {
        if (part.length > 2 && this.dictionary && !this.dictionary.check(part)) {
          // Check each part, but be lenient
          return true; // Accept hyphenated words for now
        }
      }
      return true;
    }

    // Use Typo.js dictionary if loaded
    if (this.dictionary && this.dictionaryLoaded) {
      return this.dictionary.check(word);
    }

    // Dictionary not loaded yet - be permissive to avoid false positives
    // Accept words ending in common suffixes
    const commonSuffixes = [
      'ing', 'ed', 'er', 'est', 'ly', 'tion', 'sion', 'ment', 'ness', 'ity', 'ful',
      'less', 'ous', 'ive', 'able', 'ible', 'al', 'ic', 'ical', 'ize', 'ise',
      'ized', 'ised', 'izing', 'ising', 'ization', 'isation'
    ];

    if (commonSuffixes.some(suffix => lowerWord.endsWith(suffix))) {
      return true;
    }

    // Accept words starting with common prefixes
    const commonPrefixes = [
      'un', 're', 'pre', 'post', 'non', 'anti', 'de', 'dis', 'en', 'em',
      'fore', 'in', 'im', 'inter', 'mid', 'mis', 'over', 'out', 'super',
      'trans', 'under', 'sub', 'co', 'multi', 'semi', 'auto', 'bio', 'micro',
      'macro', 'nano', 'neuro', 'psycho', 'photo', 'electro', 'hydro', 'geo'
    ];

    if (commonPrefixes.some(prefix => lowerWord.startsWith(prefix) && lowerWord.length > prefix.length + 2)) {
      return true;
    }

    // Common misspelling patterns - flag these as errors even without dictionary
    const commonMisspellings = new Set([
      'teh', 'adn', 'taht', 'thsi', 'fo', 'waht', 'wiht', 'wtih',
      'recieve', 'recieved', 'occured', 'occuring', 'seperate', 'definately',
      'goverment', 'enviroment', 'recomend', 'begining', 'untill',
      'wich', 'wether', 'wheather', 'beleive', 'belive'
    ]);

    if (commonMisspellings.has(lowerWord)) {
      return false;
    }

    // Fallback: accept most words while dictionary is loading
    return true;
  }

  /**
   * Register code action provider for spelling suggestions
   */
  private registerCodeActionProvider(): void {
    this.monaco.languages.registerCodeActionProvider('latex', {
      provideCodeActions: (model: any, range: any, context: any) => {
        const actions: any[] = [];

        // Check if this is a spelling error
        const decorations = model.getDecorationsInRange(range);
        const hasSpellingError = decorations.some((d: any) =>
          d.options.className === 'spell-error'
        );

        if (!hasSpellingError) {
          return { actions: [], dispose: () => {} };
        }

        const word = model.getValueInRange(range);

        // Add to custom dictionary action
        actions.push({
          title: `Add "${word}" to dictionary`,
          kind: 'quickfix',
          isPreferred: false,
          edit: {
            edits: [],
          },
          command: {
            id: 'spellchecker.addToCustomDictionary',
            title: 'Add to Dictionary',
            arguments: [word],
          },
        });

        // TODO: Add spelling suggestions here
        // For now, just provide the "add to dictionary" option

        return { actions, dispose: () => {} };
      },
    });

    // Register command for adding words to custom dictionary
    this.editor.addAction({
      id: 'spellchecker.addToCustomDictionary',
      label: 'Add to Custom Dictionary',
      run: (editor: any, word: string) => {
        this.addToCustomDictionary(word);
      },
    });

    console.log('[SpellChecker] Code action provider registered');
  }

  /**
   * Add word to custom dictionary
   */
  addToCustomDictionary(word: string): void {
    this.customWords.add(word.toLowerCase());
    this.spellingCache.set(word.toLowerCase(), true);

    // Save to localStorage
    const stored = localStorage.getItem('scitex_custom_dictionary');
    const customDict = stored ? JSON.parse(stored) : [];
    if (!customDict.includes(word.toLowerCase())) {
      customDict.push(word.toLowerCase());
      localStorage.setItem('scitex_custom_dictionary', JSON.stringify(customDict));
    }

    // Re-check spelling to clear the error
    this.checkSpelling();

    console.log(`[SpellChecker] Added "${word}" to custom dictionary`);

    // Show toast notification
    const showToast = (window as any).showToast;
    if (showToast) {
      showToast(`Added "${word}" to dictionary`, 'success');
    }
  }

  /**
   * Load custom dictionary from localStorage
   */
  loadCustomDictionary(): void {
    const stored = localStorage.getItem('scitex_custom_dictionary');
    if (stored) {
      const customDict = JSON.parse(stored);
      this.customWords = new Set(customDict);
      console.log(`[SpellChecker] Loaded ${this.customWords.size} words from custom dictionary`);
    }
  }

  /**
   * Clear custom dictionary
   */
  clearCustomDictionary(): void {
    this.customWords.clear();
    this.spellingCache.clear();
    localStorage.removeItem('scitex_custom_dictionary');
    this.checkSpelling();
    console.log('[SpellChecker] Custom dictionary cleared');
  }
}

/**
 * Add CSS for spell error decorations
 */
export function injectSpellCheckStyles(): void {
  const styleId = 'spell-checker-styles';

  // Check if styles already injected
  if (document.getElementById(styleId)) {
    return;
  }

  const style = document.createElement('style');
  style.id = styleId;
  style.textContent = `
    /* Squiggly underline for spelling errors using theme error color */
    .spell-error-inline {
      background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 6 3" enable-background="new 0 0 6 3" height="3" width="6"><path fill="rgb(192, 136, 136)" d="M5.5,0 Q5.5,3 3,3 T0.5,0"/></svg>');
      background-repeat: repeat-x;
      background-position: left bottom;
      padding-bottom: 2px;
    }
  `;

  document.head.appendChild(style);
  console.log('[SpellChecker] Styles injected');
}
