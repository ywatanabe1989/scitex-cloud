/**
 * SectionService manages section operations and document structure
 */

import {
  SectionName,
  DocumentType,
  Section,
  SectionMetadata,
  SectionData,
  ActiveSections,
  AvailableSections,
} from '@/types';
import { writerStorage } from '@/utils/storage';

export class SectionService {
  private sectionData: SectionData = {};
  private activeSections: ActiveSections = {};
  private availableSections: AvailableSections = {};

  private sectionMetadata: Record<SectionName, SectionMetadata> = {
    // Shared sections
    shared_title: {
      name: 'shared_title',
      title: 'Title',
      placeholder: 'Enter paper title...',
      category: 'manuscript' as DocumentType,
    },
    shared_authors: {
      name: 'shared_authors',
      title: 'Authors',
      placeholder: 'Enter author names...',
      category: 'manuscript' as DocumentType,
    },
    shared_keywords: {
      name: 'shared_keywords',
      title: 'Keywords',
      placeholder: 'Enter keywords separated by commas...',
      category: 'manuscript' as DocumentType,
    },
    shared_journal_name: {
      name: 'shared_journal_name',
      title: 'Journal Name',
      placeholder: 'Enter target journal name...',
      category: 'manuscript' as DocumentType,
    },

    // Manuscript sections
    abstract: {
      name: 'abstract',
      title: 'Abstract',
      placeholder: 'Enter abstract...',
      category: 'manuscript' as DocumentType,
    },
    highlights: {
      name: 'highlights',
      title: 'Highlights',
      placeholder: 'Enter highlights...',
      category: 'manuscript' as DocumentType,
    },
    introduction: {
      name: 'introduction',
      title: 'Introduction',
      placeholder: 'Enter introduction...',
      category: 'manuscript' as DocumentType,
    },
    methods: {
      name: 'methods',
      title: 'Methods',
      placeholder: 'Enter methods...',
      category: 'manuscript' as DocumentType,
    },
    results: {
      name: 'results',
      title: 'Results',
      placeholder: 'Enter results...',
      category: 'manuscript' as DocumentType,
    },
    discussion: {
      name: 'discussion',
      title: 'Discussion',
      placeholder: 'Enter discussion...',
      category: 'manuscript' as DocumentType,
    },
    conclusion: {
      name: 'conclusion',
      title: 'Conclusion',
      placeholder: 'Enter conclusion...',
      category: 'manuscript' as DocumentType,
    },
    acknowledgments: {
      name: 'acknowledgments',
      title: 'Acknowledgments',
      placeholder: 'Enter acknowledgments...',
      category: 'manuscript' as DocumentType,
    },
    references: {
      name: 'references',
      title: 'References',
      placeholder: 'Enter references...',
      category: 'manuscript' as DocumentType,
    },

    // Supplementary sections
    supplementary_methods: {
      name: 'supplementary_methods',
      title: 'Supplementary Methods',
      placeholder: 'Enter supplementary methods...',
      category: 'supplementary' as DocumentType,
    },
    supplementary_results: {
      name: 'supplementary_results',
      title: 'Supplementary Results',
      placeholder: 'Enter supplementary results...',
      category: 'supplementary' as DocumentType,
    },

    // Revision sections
    revision_introduction: {
      name: 'revision_introduction',
      title: 'Response to Introduction Comments',
      placeholder: 'Enter response...',
      category: 'revision' as DocumentType,
    },
    revision_editor: {
      name: 'revision_editor',
      title: 'Response to Editor Comments',
      placeholder: 'Enter response...',
      category: 'revision' as DocumentType,
    },
    revision_reviewer1: {
      name: 'revision_reviewer1',
      title: 'Response to Reviewer 1',
      placeholder: 'Enter response...',
      category: 'revision' as DocumentType,
    },
    revision_reviewer2: {
      name: 'revision_reviewer2',
      title: 'Response to Reviewer 2',
      placeholder: 'Enter response...',
      category: 'revision' as DocumentType,
    },
  };

  constructor() {
    this.loadFromStorage();
  }

  /**
   * Initialize sections from server data
   */
  initializeFromServer(
    data: SectionData,
    active: ActiveSections,
    available: AvailableSections
  ): void {
    this.sectionData = JSON.parse(JSON.stringify(data));
    this.activeSections = JSON.parse(JSON.stringify(active));
    this.availableSections = JSON.parse(JSON.stringify(available));
    this.saveToStorage();
  }

  /**
   * Get section content
   */
  getSectionContent(section: SectionName, docType?: DocumentType): string {
    if (!docType) {
      const metadata = this.sectionMetadata[section];
      docType = metadata.category;
    }
    return this.sectionData[docType]?.[section] ?? '';
  }

  /**
   * Set section content
   */
  setSectionContent(section: SectionName, docType: DocumentType, content: string): void {
    if (!this.sectionData[docType]) {
      this.sectionData[docType] = {};
    }
    this.sectionData[docType][section] = content;
    this.saveToStorage();
  }

  /**
   * Get section metadata
   */
  getSectionMetadata(section: SectionName): SectionMetadata {
    return this.sectionMetadata[section];
  }

  /**
   * Get sections for a document type
   */
  getAvailableSections(docType: DocumentType): SectionName[] {
    return this.availableSections[docType] ?? [];
  }

  /**
   * Get active sections for a document type
   */
  getActiveSections(docType: DocumentType): SectionName[] {
    return this.activeSections[docType] ?? [];
  }

  /**
   * Set active sections for a document type
   */
  setActiveSections(docType: DocumentType, sections: SectionName[]): void {
    this.activeSections[docType] = sections;
    this.saveToStorage();
  }

  /**
   * Add section to active list
   */
  addActiveSection(docType: DocumentType, section: SectionName): void {
    if (!this.activeSections[docType]) {
      this.activeSections[docType] = [];
    }
    if (!this.activeSections[docType].includes(section)) {
      this.activeSections[docType].push(section);
      this.saveToStorage();
    }
  }

  /**
   * Remove section from active list
   */
  removeActiveSection(docType: DocumentType, section: SectionName): void {
    if (this.activeSections[docType]) {
      this.activeSections[docType] = this.activeSections[docType].filter(s => s !== section);
      this.saveToStorage();
    }
  }

  /**
   * Check if section is active
   */
  isActive(docType: DocumentType, section: SectionName): boolean {
    return this.activeSections[docType]?.includes(section) ?? false;
  }

  /**
   * Get all sections data
   */
  getAllSectionData(): SectionData {
    return JSON.parse(JSON.stringify(this.sectionData));
  }

  /**
   * Get sections for a document type as array
   */
  getSectionsForDocType(docType: DocumentType): Section[] {
    const sections = this.activeSections[docType] ?? [];
    return sections.map(name => ({
      name,
      title: this.sectionMetadata[name].title,
      content: this.sectionData[docType]?.[name] ?? '',
      wordCount: 0, // Will be set by WordCountService
      docType,
      isDirty: false,
      isSaving: false,
    }));
  }

  /**
   * Check if any section has unsaved changes
   */
  hasUnsavedChanges(originalData: SectionData): boolean {
    for (const docType of Object.keys(this.sectionData)) {
      for (const section of Object.keys(this.sectionData[docType])) {
        if (
          this.sectionData[docType][section] !==
          originalData[docType]?.[section]
        ) {
          return true;
        }
      }
    }
    return false;
  }

  /**
   * Clear all section data
   */
  clear(): void {
    this.sectionData = {};
    this.activeSections = {};
    writerStorage.remove('sectionData');
    writerStorage.remove('activeSections');
  }

  /**
   * Save to localStorage
   */
  private saveToStorage(): void {
    writerStorage.save('sectionData', this.sectionData);
    writerStorage.save('activeSections', this.activeSections);
  }

  /**
   * Load from localStorage
   */
  private loadFromStorage(): void {
    const data = writerStorage.load<SectionData>('sectionData');
    const active = writerStorage.load<ActiveSections>('activeSections');

    if (data) this.sectionData = data;
    if (active) this.activeSections = active;
  }

  /**
   * Get all section names for a category
   */
  getAllSectionNames(category?: DocumentType): SectionName[] {
    if (category) {
      return Object.values(this.sectionMetadata)
        .filter(meta => meta.category === category)
        .map(meta => meta.name);
    }
    return Object.keys(this.sectionMetadata) as SectionName[];
  }
}

// Global SectionService instance
export const sectionService = new SectionService();
