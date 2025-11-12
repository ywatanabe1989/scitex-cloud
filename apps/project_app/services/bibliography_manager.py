#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/scitex-cloud/apps/project_app/services/bibliography_manager.py

"""
Bibliography Structure Manager

Ensures consistent bibliography directory structure across projects.
Handles initialization, merging, and symlink management.
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def ensure_bibliography_structure(project_path: Path, force: bool = False) -> dict:
    """
    Ensure bibliography directory structure exists.

    This is a PASSIVE operation - creates directories and symlinks,
    but does NOT parse or merge actual BibTeX files (that's opt-in).

    Args:
        project_path: Path to project git clone directory
        force: If True, recreate symlinks even if they exist

    Returns:
        dict with status and created items
    """
    results = {
        'success': True,
        'directories_created': [],
        'files_created': [],
        'symlinks_created': [],
        'errors': []
    }

    try:
        scitex_root = project_path / 'scitex'
        scitex_root.mkdir(parents=True, exist_ok=True)

        # ============================================================
        # 1. CREATE DIRECTORY STRUCTURE
        # ============================================================
        directories = [
            scitex_root / 'scholar' / 'bib_files',
            scitex_root / 'writer' / 'bib_files',
            scitex_root / 'writer' / '00_shared',
            scitex_root / 'writer' / '01_manuscript' / 'contents',
        ]

        for directory in directories:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                results['directories_created'].append(str(directory.relative_to(project_path)))
                logger.info(f"Created directory: {directory.relative_to(project_path)}")

        # ============================================================
        # 2. CREATE EMPTY PLACEHOLDER FILES (with helpful comments)
        # ============================================================
        scholar_merged = scitex_root / 'scholar' / 'bib_files' / 'merged_scholar.bib'
        writer_merged = scitex_root / 'writer' / 'bib_files' / 'merged_writer.bib'
        bibliography_all = scitex_root / 'bibliography_all.bib'

        placeholder_comment = """% ============================================================
% SciTeX Bibliography File
% ============================================================
% This file will be automatically populated when you:
% 1. Upload BibTeX files through Scholar app, or
% 2. Add .bib files to writer/bib_files/ directory, or
% 3. Click "Regenerate Bibliography" button
%
% For now, this is an empty placeholder.
% ============================================================

"""

        # Create empty merged_scholar.bib if not exists
        if not scholar_merged.exists():
            scholar_merged.write_text(placeholder_comment + "% Scholar bibliography entries will appear here\n")
            results['files_created'].append(str(scholar_merged.relative_to(project_path)))
            logger.info(f"Created placeholder: merged_scholar.bib")

        # Create empty merged_writer.bib if not exists
        if not writer_merged.exists():
            writer_merged.write_text(placeholder_comment + "% Writer bibliography entries will appear here\n")
            results['files_created'].append(str(writer_merged.relative_to(project_path)))
            logger.info(f"Created placeholder: merged_writer.bib")

        # Create bibliography_all.bib (merges both)
        if not bibliography_all.exists() or force:
            bibliography_all.write_text(placeholder_comment + "% Combined scholar + writer bibliography will appear here\n")
            if not bibliography_all.exists():
                results['files_created'].append(str(bibliography_all.relative_to(project_path)))
            logger.info(f"Created master bibliography: bibliography_all.bib")

        # ============================================================
        # 3. CREATE CROSS-SYMLINKS (scholar ↔ writer)
        # ============================================================
        # scholar/bib_files/merged_writer.bib → ../../writer/bib_files/merged_writer.bib
        scholar_to_writer = scitex_root / 'scholar' / 'bib_files' / 'merged_writer.bib'
        if not scholar_to_writer.exists() or force:
            if scholar_to_writer.exists():
                scholar_to_writer.unlink()
            relative_path = os.path.relpath(writer_merged, scholar_to_writer.parent)
            scholar_to_writer.symlink_to(relative_path)
            results['symlinks_created'].append(f"scholar/bib_files/merged_writer.bib → {relative_path}")
            logger.info(f"Created symlink: scholar/bib_files/merged_writer.bib")

        # writer/bib_files/merged_scholar.bib → ../../scholar/bib_files/merged_scholar.bib
        writer_to_scholar = scitex_root / 'writer' / 'bib_files' / 'merged_scholar.bib'
        if not writer_to_scholar.exists() or force:
            if writer_to_scholar.exists():
                writer_to_scholar.unlink()
            relative_path = os.path.relpath(scholar_merged, writer_to_scholar.parent)
            writer_to_scholar.symlink_to(relative_path)
            results['symlinks_created'].append(f"writer/bib_files/merged_scholar.bib → {relative_path}")
            logger.info(f"Created symlink: writer/bib_files/merged_scholar.bib")

        # ============================================================
        # 4. CREATE WRITER SYMLINK CHAIN FOR LATEX (v2.0.0-rc1)
        # ============================================================
        # Writer v2.0.0-rc1 structure:
        # - Multiple .bib files in writer/00_shared/bib_files/
        # - Merge script creates writer/00_shared/bib_files/bibliography.bib
        # - Manuscript expects writer/01_manuscript/contents/bibliography.bib
        #
        # NOTE: Writer directory structure MUST be created by scitex.writer.Writer
        # This section only creates symlinks if the structure already exists

        # Check if writer structure exists (created by scitex.writer.Writer)
        writer_bib_dir = scitex_root / 'writer' / '00_shared' / 'bib_files'
        writer_dir = scitex_root / 'writer'

        if not writer_dir.exists():
            logger.warning(f"Writer directory not initialized yet - skipping writer bibliography setup")
            logger.info(f"✓ Bibliography structure ensured for project: {project_path.name} (scholar only)")
            return results

        if not writer_bib_dir.exists():
            logger.error(f"Writer directory exists but 00_shared/bib_files missing - writer structure incomplete")
            results['errors'].append("Writer structure incomplete: missing 00_shared/bib_files")
            logger.info(f"✓ Bibliography structure ensured for project: {project_path.name} (scholar only)")
            return results

        # Copy merged_scholar.bib into writer's bib_files so merge script picks it up
        writer_scholar_link = writer_bib_dir / 'merged_scholar.bib'
        if not writer_scholar_link.exists() or force:
            if writer_scholar_link.exists() or writer_scholar_link.is_symlink():
                writer_scholar_link.unlink()
            relative_path = os.path.relpath(scholar_merged, writer_scholar_link.parent)
            writer_scholar_link.symlink_to(relative_path)
            results['symlinks_created'].append(f"writer/00_shared/bib_files/merged_scholar.bib → {relative_path}")
            logger.info(f"Created symlink: writer/00_shared/bib_files/merged_scholar.bib")

        # Create symlink from manuscript to merged bibliography
        # writer/01_manuscript/contents/bibliography.bib → ../../00_shared/bib_files/bibliography.bib
        manuscript_bib = scitex_root / 'writer' / '01_manuscript' / 'contents' / 'bibliography.bib'
        writer_merged_bib = writer_bib_dir / 'bibliography.bib'

        if not manuscript_bib.parent.exists():
            logger.error(f"Manuscript contents directory missing - writer structure incomplete")
            results['errors'].append("Writer structure incomplete: missing 01_manuscript/contents")
            logger.info(f"✓ Bibliography structure ensured for project: {project_path.name} (partial)")
            return results

        if not manuscript_bib.exists() or force:
            # Backup existing file if it's a real file with content
            if manuscript_bib.is_file() and not manuscript_bib.is_symlink():
                if manuscript_bib.stat().st_size > 0:
                    backup_path = manuscript_bib.with_suffix('.bib.backup')
                    import shutil
                    shutil.copy(manuscript_bib, backup_path)
                    results['files_created'].append(f"Backup: {backup_path.relative_to(project_path)}")
                    logger.info(f"Backed up existing bibliography.bib")
                manuscript_bib.unlink()
            elif manuscript_bib.is_symlink():
                manuscript_bib.unlink()

            relative_path = os.path.relpath(writer_merged_bib, manuscript_bib.parent)
            manuscript_bib.symlink_to(relative_path)
            results['symlinks_created'].append(f"01_manuscript/contents/bibliography.bib → {relative_path}")
            logger.info(f"Created symlink: 01_manuscript/contents/bibliography.bib")

        logger.info(f"✓ Bibliography structure ensured for project: {project_path.name}")
        return results

    except Exception as e:
        logger.error(f"Error ensuring bibliography structure: {e}", exc_info=True)
        results['success'] = False
        results['errors'].append(str(e))
        return results


def regenerate_bibliography(project_path: Path, project_name: str = None) -> dict:
    """
    Regenerate bibliography_all.bib by merging all .bib files with deduplication.

    This is an ACTIVE operation - actually parses and merges BibTeX files.
    Uses scitex.scholar's DeduplicationManager for intelligent deduplication based on:
    - DOI matching (most reliable)
    - Title + Author + Year fingerprinting
    - Metadata quality scoring

    Should be called when:
    - User clicks "Regenerate Bibliography" button
    - New .bib files are added
    - After scholar enrichment

    Args:
        project_path: Path to project git clone directory
        project_name: Optional project name for logging

    Returns:
        dict with status and statistics including duplicates_removed
    """
    results = {
        'success': True,
        'scholar_count': 0,
        'writer_count': 0,
        'total_count': 0,
        'duplicates_removed': 0,
        'errors': []
    }

    try:
        from scitex.scholar.storage import BibTeXHandler
        from scitex.scholar.storage._DeduplicationManager import DeduplicationManager

        scitex_root = project_path / 'scitex'
        bibtex_handler = BibTeXHandler(project=project_name, config=None)
        dedup_manager = DeduplicationManager()

        # Ensure structure exists first
        ensure_bibliography_structure(project_path)

        # ============================================================
        # 1. MERGE SCHOLAR FILES (Simple concatenation to avoid bugs)
        # ============================================================
        scholar_bib_dir = scitex_root / 'scholar' / 'bib_files'
        scholar_files = [
            f for f in scholar_bib_dir.glob("*.bib")
            if not f.name.startswith("merged_")
        ]

        if scholar_files:
            merged_scholar_path = scholar_bib_dir / "merged_scholar.bib"

            # Parse and deduplicate scholar files using fingerprinting
            all_papers = []
            seen_fingerprints = {}  # fingerprint -> paper

            for scholar_file in scholar_files:
                papers = bibtex_handler.papers_from_bibtex(scholar_file)
                for paper in papers:
                    # Generate fingerprint using DOI or title+year
                    # Access metadata safely with getattr
                    doi = getattr(paper.metadata.identifiers, 'doi', None) if hasattr(paper.metadata, 'identifiers') else None
                    title = getattr(paper.metadata.basic, 'title', None) if hasattr(paper.metadata, 'basic') else None
                    year = getattr(paper.metadata.basic, 'year', None) if hasattr(paper.metadata, 'basic') else None

                    metadata = {
                        'doi': doi,
                        'title': title,
                        'year': year
                    }
                    fingerprint = dedup_manager._generate_paper_fingerprint(metadata)

                    if fingerprint and fingerprint not in seen_fingerprints:
                        all_papers.append(paper)
                        seen_fingerprints[fingerprint] = paper
                    elif fingerprint:
                        logger.debug(f"Skipping duplicate: {paper.metadata.basic.title[:50]}")
                        results['duplicates_removed'] += 1

            # Write deduplicated papers to merged file
            bibtex_handler.papers_to_bibtex(all_papers, merged_scholar_path)
            results['scholar_count'] = len(all_papers)
            logger.info(f"✓ Merged {len(scholar_files)} scholar files → {len(all_papers)} unique entries ({results['duplicates_removed']} duplicates removed)")

        # ============================================================
        # 2. MERGE WRITER FILES (Simple concatenation to avoid bugs)
        # ============================================================
        writer_bib_dir = scitex_root / 'writer' / 'bib_files'
        writer_files = [
            f for f in writer_bib_dir.glob("*.bib")
            if not f.name.startswith("merged_")
        ]

        if writer_files:
            merged_writer_path = writer_bib_dir / "merged_writer.bib"

            # Parse and deduplicate writer files using fingerprinting
            all_papers = []
            seen_fingerprints = {}

            for writer_file in writer_files:
                papers = bibtex_handler.papers_from_bibtex(writer_file)
                for paper in papers:
                    # Access metadata safely
                    doi = getattr(paper.metadata.identifiers, 'doi', None) if hasattr(paper.metadata, 'identifiers') else None
                    title = getattr(paper.metadata.basic, 'title', None) if hasattr(paper.metadata, 'basic') else None
                    year = getattr(paper.metadata.basic, 'year', None) if hasattr(paper.metadata, 'basic') else None

                    metadata = {
                        'doi': doi,
                        'title': title,
                        'year': year
                    }
                    fingerprint = dedup_manager._generate_paper_fingerprint(metadata)

                    if fingerprint and fingerprint not in seen_fingerprints:
                        all_papers.append(paper)
                        seen_fingerprints[fingerprint] = paper
                    elif fingerprint:
                        title_preview = title[:50] if title else 'Unknown'
                        logger.debug(f"Skipping duplicate: {title_preview}")
                        results['duplicates_removed'] += 1

            # Write deduplicated papers to merged file
            bibtex_handler.papers_to_bibtex(all_papers, merged_writer_path)
            results['writer_count'] = len(all_papers)
            logger.info(f"✓ Merged {len(writer_files)} writer files → {len(all_papers)} unique entries")

        # ============================================================
        # 3. CREATE MASTER bibliography_all.bib (Deduplicated merge)
        # ============================================================
        merged_scholar_path = scholar_bib_dir / "merged_scholar.bib"
        merged_writer_path = writer_bib_dir / "merged_writer.bib"
        bibliography_all_path = scitex_root / "bibliography_all.bib"

        files_to_merge = []
        if merged_scholar_path.exists() and merged_scholar_path.stat().st_size > 100:
            files_to_merge.append(merged_scholar_path)
        if merged_writer_path.exists() and merged_writer_path.stat().st_size > 100:
            files_to_merge.append(merged_writer_path)

        if files_to_merge:
            # Parse and deduplicate across scholar + writer using fingerprinting
            all_papers = []
            seen_fingerprints = {}

            for merge_file in files_to_merge:
                papers = bibtex_handler.papers_from_bibtex(merge_file)
                for paper in papers:
                    # Access metadata safely
                    doi = getattr(paper.metadata.identifiers, 'doi', None) if hasattr(paper.metadata, 'identifiers') else None
                    title = getattr(paper.metadata.basic, 'title', None) if hasattr(paper.metadata, 'basic') else None
                    year = getattr(paper.metadata.basic, 'year', None) if hasattr(paper.metadata, 'basic') else None

                    metadata = {
                        'doi': doi,
                        'title': title,
                        'year': year
                    }
                    fingerprint = dedup_manager._generate_paper_fingerprint(metadata)

                    if fingerprint and fingerprint not in seen_fingerprints:
                        all_papers.append(paper)
                        seen_fingerprints[fingerprint] = paper
                    elif fingerprint:
                        title_preview = title[:50] if title else 'Unknown'
                        logger.debug(f"Skipping duplicate in final merge: {title_preview}")
                        results['duplicates_removed'] += 1

            # Write deduplicated master bibliography
            bibtex_handler.papers_to_bibtex(all_papers, bibliography_all_path)
            results['total_count'] = len(all_papers)
            logger.info(f"✓ Created bibliography_all.bib with {len(all_papers)} unique entries (total {results['duplicates_removed']} duplicates removed)")
        else:
            logger.info("No BibTeX files to merge yet")

        return results

    except Exception as e:
        logger.error(f"Error regenerating bibliography: {e}", exc_info=True)
        results['success'] = False
        results['errors'].append(str(e))
        return results


# EOF
