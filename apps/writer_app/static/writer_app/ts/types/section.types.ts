/**
 * Section and document-related type definitions
 */

export type DocumentType = 'manuscript' | 'supplementary' | 'revision';

export type SectionName =
  | 'abstract'
  | 'highlights'
  | 'introduction'
  | 'methods'
  | 'results'
  | 'discussion'
  | 'conclusion'
  | 'acknowledgments'
  | 'references'
  | 'supplementary_methods'
  | 'supplementary_results'
  | 'revision_introduction'
  | 'revision_editor'
  | 'revision_reviewer1'
  | 'revision_reviewer2'
  | 'shared_title'
  | 'shared_authors'
  | 'shared_keywords'
  | 'shared_journal_name';

export interface Section {
  name: SectionName;
  title: string;
  content: string;
  wordCount: number;
  docType: DocumentType;
  isDirty: boolean;
  isSaving: boolean;
  lastSaved?: Date;
}

export interface SectionMetadata {
  name: SectionName;
  title: string;
  placeholder: string;
  category: DocumentType;
}

export interface SectionData {
  [docType: string]: {
    [sectionName: string]: string;
  };
}

export interface ActiveSections {
  [docType: string]: SectionName[];
}

export interface AvailableSections {
  [docType: string]: SectionName[];
}

export interface SectionUI {
  element: HTMLElement;
  section: SectionName;
  docType: DocumentType;
}
