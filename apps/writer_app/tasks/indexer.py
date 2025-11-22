#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Background tasks for indexing figures and tables in SciTeX projects.

These tasks run asynchronously to build and maintain the SQLite metadata
database without blocking the UI.
"""

try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    # Celery not available - use direct function calls
    CELERY_AVAILABLE = False
    def shared_task(func):
        """Decorator stub when Celery is not available"""
        return func

import hashlib
import re
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Supported file extensions
SUPPORTED_FIGURE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.pdf', '.tiff', '.tif', '.svg', '.pptx', '.mmd'}
SUPPORTED_TABLE_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.tsv', '.ods'}


@shared_task
def index_project_figures(project_id):
    """
    Index all figures in project to local SQLite DB.

    This task scans the project directory for figure files and stores
    their metadata in the project's SQLite database for fast querying.

    Args:
        project_id: Project ID
    """
    from apps.project_app.models import Project
    from ..utils.project_db import get_project_db
    from ..services import WriterService

    try:
        project = Project.objects.get(id=project_id)

        # Get project path
        if hasattr(project, 'git_clone_path') and project.git_clone_path:
            project_path = Path(project.git_clone_path)
        else:
            # Handle visitor projects
            from apps.project_app.services.project_filesystem import get_project_filesystem_manager
            if not hasattr(project, 'owner') or not project.owner:
                logger.error(f"[Indexer] Cannot determine user for project {project_id}")
                return
            manager = get_project_filesystem_manager(project.owner)
            project_path = manager.get_project_root_path(project)
            if not project_path:
                logger.error(f"[Indexer] Project path not found for project {project_id}")
                return

        db = get_project_db(project)

        logger.info(f"[Indexer] Starting indexing for project {project_id} at {project_path}")

        # Search patterns for figures
        search_patterns = [
            'scitex/writer/**/figures/**/*',
            'scitex/writer/**/tables/**/*',
            'scitex/writer/00_shared/figures_pool/*',
            'scitex/writer/00_shared/tables_pool/*',
            'scitex/writer/uploads/figures/*',  # User uploads
            'data/**/figures/**/*',
            'data/**/plots/**/*',
            'data/**/*.png',
            'data/**/*.jpg',
            'data/**/*.pdf',
            'scripts/**/*_out/**/*',
            'scripts/**/figures/**/*',
        ]

        indexed_count = 0
        skipped_count = 0

        for pattern in search_patterns:
            for file_path in project_path.glob(pattern):
                if not file_path.is_file():
                    continue

                if file_path.suffix.lower() in SUPPORTED_FIGURE_EXTENSIONS:
                    try:
                        # Check if already indexed with same hash
                        relative_path = str(file_path.relative_to(project_path))
                        file_hash = compute_file_hash(file_path)

                        if db.check_if_indexed(relative_path, file_hash):
                            skipped_count += 1
                            continue  # Skip unchanged files

                        # Check for duplicate content (same hash, different path)
                        existing = db.check_hash_exists(file_hash, table_type='figure')
                        if existing:
                            # Compare filenames - prefer longer, more descriptive names
                            current_name = file_path.name
                            existing_name = existing['file_name']

                            if len(current_name) <= len(existing_name):
                                # Current file has shorter/same length name - skip it as duplicate
                                logger.debug(f"[Indexer] Skipping duplicate: {current_name} (keeping {existing_name})")
                                skipped_count += 1
                                continue
                            else:
                                # Current file has longer name - remove old entry and index new one
                                logger.info(f"[Indexer] Replacing duplicate: {existing_name} -> {current_name}")
                                db.delete_figure(existing['file_path'])

                        # Extract metadata
                        metadata = extract_figure_metadata(file_path, project_path)
                        db.upsert_figure(metadata)
                        indexed_count += 1

                        # Generate thumbnail asynchronously
                        if CELERY_AVAILABLE:
                            generate_thumbnail.delay(project_id, relative_path)
                        else:
                            generate_thumbnail(project_id, relative_path)

                    except Exception as e:
                        logger.error(f"[Indexer] Error indexing {file_path}: {e}")
                        continue

        logger.info(f"[Indexer] Completed for project {project_id}: {indexed_count} indexed, {skipped_count} skipped")

        # Update LaTeX references
        if CELERY_AVAILABLE:
            update_latex_references.delay(project_id)
        else:
            update_latex_references(project_id)

    except Exception as e:
        logger.error(f"[Indexer] Error indexing project {project_id}: {e}")
        raise


@shared_task
def index_project_tables(project_id):
    """
    Index all table files (CSV, Excel) in project to local SQLite DB.

    Tables are discovered in:
    - scitex/writer/**/tables/**/* (manuscript tables)
    - scitex/writer/00_shared/tables_pool/* (shared pool)
    - data/**/tables/**/* (data tables)
    - data/**/*.{csv,xlsx,xls,tsv} (data files)
    - scripts/**/*_out/**/* (script outputs)

    Args:
        project_id: Project ID
    """
    try:
        from apps.project_app.models import Project
        from ..utils.project_db import get_project_db

        project = Project.objects.get(id=project_id)

        # Get project path
        if hasattr(project, 'git_clone_path') and project.git_clone_path:
            project_path = Path(project.git_clone_path)
        else:
            from apps.project_app.services.project_filesystem import get_project_filesystem_manager
            if not hasattr(project, 'owner') or not project.owner:
                logger.error(f"[TableIndexer] Cannot determine user for project {project_id}")
                return
            manager = get_project_filesystem_manager(project.owner)
            project_path = manager.get_project_root_path(project)
            if not project_path:
                logger.error(f"[TableIndexer] Project path not found for project {project_id}")
                return

        db = get_project_db(project)

        logger.info(f"[TableIndexer] Starting table indexing for project {project_id} at {project_path}")

        # Search patterns for tables
        search_patterns = [
            'scitex/writer/**/tables/**/*',
            'scitex/writer/00_shared/tables_pool/*',
            'scitex/writer/uploads/tables/*',  # User uploads
            'data/**/tables/**/*',
            'data/**/*.csv',
            'data/**/*.xlsx',
            'data/**/*.xls',
            'data/**/*.tsv',
            'scripts/**/*_out/**/*.csv',
            'scripts/**/*_out/**/*.xlsx',
        ]

        indexed_count = 0
        skipped_count = 0

        for pattern in search_patterns:
            for file_path in project_path.glob(pattern):
                if not file_path.is_file():
                    continue

                if file_path.suffix.lower() in SUPPORTED_TABLE_EXTENSIONS:
                    try:
                        # Check if already indexed with same hash
                        relative_path = str(file_path.relative_to(project_path))
                        file_hash = compute_file_hash(file_path)

                        if db.check_if_indexed(relative_path, file_hash, table_type='table'):
                            skipped_count += 1
                            continue  # Skip unchanged files

                        # Check for duplicate content (same hash, different path)
                        existing = db.check_hash_exists(file_hash, table_type='table')
                        if existing:
                            # Compare filenames - prefer longer, more descriptive names
                            current_name = file_path.name
                            existing_name = existing['file_name']

                            if len(current_name) <= len(existing_name):
                                # Current file has shorter/same length name - skip it as duplicate
                                logger.debug(f"[TableIndexer] Skipping duplicate: {current_name} (keeping {existing_name})")
                                skipped_count += 1
                                continue
                            else:
                                # Current file has longer name - remove old entry and index new one
                                logger.info(f"[TableIndexer] Replacing duplicate: {existing_name} -> {current_name}")
                                db.delete_table(existing['file_path'])

                        # Extract metadata
                        metadata = extract_table_metadata(file_path, project_path)
                        db.upsert_table(metadata)
                        indexed_count += 1

                        # Generate thumbnail asynchronously
                        if CELERY_AVAILABLE:
                            generate_table_thumbnail.delay(project_id, relative_path)
                        else:
                            generate_table_thumbnail(project_id, relative_path)

                    except Exception as e:
                        logger.error(f"[TableIndexer] Error indexing {file_path}: {e}")
                        continue

        logger.info(f"[TableIndexer] Completed for project {project_id}: {indexed_count} indexed, {skipped_count} skipped")

    except Exception as e:
        logger.error(f"[TableIndexer] Error indexing project {project_id}: {e}")
        raise


def compute_file_hash(file_path: Path) -> str:
    """
    Compute SHA256 hash of file for change detection.

    Args:
        file_path: Path to file

    Returns:
        SHA256 hex digest
    """
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def extract_figure_metadata(file_path: Path, project_path: Path) -> dict:
    """
    Extract metadata from figure file.

    Args:
        file_path: Absolute path to figure
        project_path: Project root path

    Returns:
        Dictionary with figure metadata
    """
    stat = file_path.stat()
    relative_path = str(file_path.relative_to(project_path))

    return {
        'file_path': relative_path,
        'file_name': file_path.name,
        'file_hash': compute_file_hash(file_path),
        'file_size': stat.st_size,
        'file_type': file_path.suffix[1:].lower(),
        'last_modified': stat.st_mtime,
        'source': detect_source(relative_path),
        'location': str(file_path.parent.relative_to(project_path)),
        'tags': extract_tags(file_path, relative_path),
    }


def extract_table_metadata(file_path: Path, project_path: Path) -> dict:
    """
    Extract metadata from table file (CSV, Excel).

    Args:
        file_path: Absolute path to table
        project_path: Project root path

    Returns:
        Dictionary with table metadata
    """
    stat = file_path.stat()
    relative_path = str(file_path.relative_to(project_path))

    # Try to extract caption from filename or parent directory
    caption = file_path.stem.replace('_', ' ').replace('-', ' ').title()

    return {
        'file_path': relative_path,
        'file_name': file_path.name,
        'file_hash': compute_file_hash(file_path),
        'caption': caption,
        'last_modified': stat.st_mtime,
        'source': detect_source(relative_path),
        'location': str(file_path.parent.relative_to(project_path)),
        'tags': extract_tags(file_path, relative_path),
    }


def detect_source(relative_path: str) -> str:
    """
    Detect source category from file path.

    Args:
        relative_path: Relative path from project root

    Returns:
        Source category: 'paper', 'pool', 'data', 'scripts', 'other'
    """
    if 'scitex/writer/00_shared/figures_pool' in relative_path:
        return 'pool'
    elif 'scitex/writer/00_shared/tables_pool' in relative_path:
        return 'pool'
    elif 'scitex/writer/' in relative_path:
        return 'paper'
    elif 'data/' in relative_path:
        return 'data'
    elif 'scripts/' in relative_path:
        return 'scripts'
    else:
        return 'other'


def extract_tags(file_path: Path, relative_path: str) -> list:
    """
    Auto-extract tags from file path and name.

    Args:
        file_path: Path object
        relative_path: Relative path string

    Returns:
        List of tags
    """
    tags = []

    # Document type tags
    if '01_manuscript' in relative_path:
        tags.append('manuscript')
    elif '02_supplementary' in relative_path:
        tags.append('supplementary')
    elif '03_revision' in relative_path:
        tags.append('revision')

    # Source type tags
    if 'data/' in relative_path:
        tags.append('data-analysis')
        # Extract dataset name (e.g., mnist, imagenet)
        parts = relative_path.split('data/')[1].split('/')
        if parts:
            tags.append(f'dataset:{parts[0]}')

    if 'scripts/' in relative_path:
        tags.append('script-output')

    if 'pool' in relative_path:
        tags.append('curated')

    # File type tags
    if file_path.suffix.lower() == '.pptx':
        tags.append('needs-conversion')

    if file_path.suffix.lower() == '.mmd':
        tags.append('diagram')

    if file_path.suffix.lower() in ['.svg']:
        tags.append('vector')

    if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
        tags.append('raster')

    if file_path.suffix.lower() in ['.pdf']:
        tags.append('pdf')

    return tags


@shared_task
def update_latex_references(project_id):
    """
    Check which figures are referenced in LaTeX files.

    Scans all .tex files for \\includegraphics{} commands and updates
    the database with reference information.

    Args:
        project_id: Project ID
    """
    from apps.project_app.models import Project
    from ..utils.project_db import get_project_db

    try:
        project = Project.objects.get(id=project_id)

        # Get project path
        if hasattr(project, 'git_clone_path') and project.git_clone_path:
            project_path = Path(project.git_clone_path)
        else:
            from apps.project_app.services.project_filesystem import get_project_filesystem_manager
            if not hasattr(project, 'owner') or not project.owner:
                logger.error(f"[RefTracker] Cannot determine user for project {project_id}")
                return
            manager = get_project_filesystem_manager(project.owner)
            project_path = manager.get_project_root_path(project)
            if not project_path:
                logger.error(f"[RefTracker] Project path not found for project {project_id}")
                return

        db = get_project_db(project)

        logger.info(f"[RefTracker] Starting reference tracking for project {project_id}")

        # Get all figures from DB
        figures = db.get_all_figures()

        # Scan all .tex files
        tex_files = list(project_path.glob('scitex/writer/**/*.tex'))

        references_updated = 0

        for figure in figures:
            file_name = figure['file_name']
            file_stem = Path(file_name).stem

            ref_count = 0
            references = []

            # Search in .tex files
            for tex_file in tex_files:
                try:
                    content = tex_file.read_text()

                    # Pattern 1: \includegraphics{...filename...}
                    pattern1 = rf'\\includegraphics[^{{]*\{{[^}}]*{re.escape(file_name)}[^}}]*\}}'
                    matches1 = re.findall(pattern1, content, re.IGNORECASE)

                    # Pattern 2: \includegraphics{...stem...} (without extension)
                    pattern2 = rf'\\includegraphics[^{{]*\{{[^}}]*{re.escape(file_stem)}[^}}]*\}}'
                    matches2 = re.findall(pattern2, content, re.IGNORECASE)

                    matches = matches1 + matches2

                    if matches:
                        ref_count += len(matches)
                        references.append({
                            'tex_file': str(tex_file.relative_to(project_path)),
                            'count': len(matches),
                        })
                except Exception as e:
                    logger.debug(f"[RefTracker] Error reading {tex_file}: {e}")
                    continue

            # Update database
            db.update_references(
                figure['id'],
                is_referenced=(ref_count > 0),
                reference_count=ref_count
            )

            # Clear and add new references
            db.clear_latex_references(figure['id'])
            for ref in references:
                db.add_latex_reference(
                    figure['id'],
                    ref['tex_file'],
                    context=f"Referenced {ref['count']} times"
                )

            if ref_count > 0:
                references_updated += 1

        logger.info(f"[RefTracker] Completed for project {project_id}: {references_updated} figures referenced")

    except Exception as e:
        logger.error(f"[RefTracker] Error tracking references for project {project_id}: {e}")


@shared_task
def generate_thumbnail(project_id, file_path):
    """
    Generate thumbnail for figure.

    Supports: PNG, JPG, JPEG, TIFF, PDF
    TODO: Add support for SVG, PPTX, MMD

    Args:
        project_id: Project ID
        file_path: Relative path to figure
    """
    from apps.project_app.models import Project
    from ..utils.project_db import get_project_db

    try:
        from PIL import Image

        project = Project.objects.get(id=project_id)

        # Get project path
        if hasattr(project, 'git_clone_path') and project.git_clone_path:
            project_path = Path(project.git_clone_path)
        else:
            from apps.project_app.services.project_filesystem import get_project_filesystem_manager
            if not hasattr(project, 'owner') or not project.owner:
                logger.error(f"[Thumbnail] Cannot determine user for project {project_id}")
                return
            manager = get_project_filesystem_manager(project.owner)
            project_path = manager.get_project_root_path(project)
            if not project_path:
                logger.error(f"[Thumbnail] Project path not found for project {project_id}")
                return

        db = get_project_db(project)

        full_path = project_path / file_path
        if not full_path.exists():
            logger.warning(f"[Thumbnail] File not found: {file_path}")
            return

        # Generate thumbnail filename
        file_hash = compute_file_hash(full_path)
        thumb_name = f"{file_hash[:16]}_thumb.jpg"
        thumb_path = db.thumbnails_dir / thumb_name

        # Generate based on file type
        file_type = full_path.suffix.lower()

        if file_type in ['.png', '.jpg', '.jpeg', '.tiff', '.tif']:
            with Image.open(full_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                img.save(thumb_path, 'JPEG', quality=85)

        elif file_type == '.pdf':
            try:
                from pdf2image import convert_from_path
                images = convert_from_path(full_path, first_page=1, last_page=1, size=(200, 200))
                if images:
                    images[0].save(thumb_path, 'JPEG', quality=85)
            except ImportError:
                logger.warning("[Thumbnail] pdf2image not installed, skipping PDF thumbnail")
                return
            except Exception as e:
                logger.error(f"[Thumbnail] Error generating PDF thumbnail: {e}")
                return

        else:
            logger.debug(f"[Thumbnail] Unsupported file type: {file_type}")
            return

        # Update DB with thumbnail path
        relative_thumb_path = str(thumb_path.relative_to(project_path))

        with db.connection() as conn:
            conn.execute('''
                UPDATE figures SET thumbnail_path = ? WHERE file_path = ?
            ''', (relative_thumb_path, file_path))

        logger.debug(f"[Thumbnail] Generated for {file_path}")

    except Exception as e:
        logger.error(f"[Thumbnail] Error generating for {file_path}: {e}")


def generate_table_thumbnail(project_id, file_path):
    """
    Generate thumbnail preview for table files (CSV, Excel).

    Reads first few rows and renders as table image.

    Args:
        project_id: Project ID
        file_path: Relative path to table file
    """
    from apps.project_app.models import Project
    from ..utils.project_db import get_project_db

    try:
        import pandas as pd
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        from PIL import Image

        project = Project.objects.get(id=project_id)

        # Get project path
        if hasattr(project, 'git_clone_path') and project.git_clone_path:
            project_path = Path(project.git_clone_path)
        else:
            from apps.project_app.services.project_filesystem import get_project_filesystem_manager
            if not hasattr(project, 'owner') or not project.owner:
                logger.error(f"[TableThumbnail] Cannot determine user for project {project_id}")
                return
            manager = get_project_filesystem_manager(project.owner)
            project_path = manager.get_project_root_path(project)
            if not project_path:
                logger.error(f"[TableThumbnail] Project path not found for project {project_id}")
                return

        db = get_project_db(project)

        full_path = project_path / file_path
        if not full_path.exists():
            logger.warning(f"[TableThumbnail] File not found: {file_path}")
            return

        # Generate thumbnail filename
        file_hash = compute_file_hash(full_path)
        thumb_name = f"{file_hash[:16]}_thumb.jpg"
        thumb_path = db.thumbnails_dir / thumb_name

        # Read table data - show top-left corner only
        file_type = full_path.suffix.lower()
        df = None

        if file_type == '.csv':
            df = pd.read_csv(full_path, nrows=5)  # First 5 rows
        elif file_type in ['.xlsx', '.xls']:
            df = pd.read_excel(full_path, nrows=5)
        elif file_type == '.tsv':
            df = pd.read_csv(full_path, sep='\t', nrows=5)
        elif file_type == '.ods':
            df = pd.read_excel(full_path, engine='odf', nrows=5)
        else:
            logger.debug(f"[TableThumbnail] Unsupported file type: {file_type}")
            return

        if df is None or df.empty:
            logger.warning(f"[TableThumbnail] Empty table: {file_path}")
            return

        # Show only first 4 columns (top-left corner)
        if len(df.columns) > 4:
            df = df.iloc[:, :4]
            # Add ellipsis column to indicate more columns
            df['...'] = '...'

        # Truncate long values to fit in thumbnail
        df = df.map(lambda x: str(x)[:15] + '...' if len(str(x)) > 15 else str(x))

        # Create figure and render table - optimized for small thumbnail
        fig, ax = plt.subplots(figsize=(5, 3), facecolor='white')
        ax.axis('tight')
        ax.axis('off')

        # Create table with better spacing
        table = ax.table(
            cellText=df.values,
            colLabels=df.columns,
            cellLoc='center',
            loc='center',
            bbox=[0, 0, 1, 1]
        )

        # Style table for better readability
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)  # Increase row height for better readability

        # Header and cell styling
        for (i, j), cell in table.get_celld().items():
            cell.set_edgecolor('#cccccc')
            cell.set_linewidth(1)
            cell.PAD = 0.05

            if i == 0:  # Header row
                cell.set_facecolor('#4A90E2')
                cell.set_text_props(weight='bold', color='white', size=9)
            else:  # Data rows
                cell.set_facecolor('#f8f9fa' if i % 2 == 0 else 'white')
                cell.set_text_props(size=8)

        # Save to file with white background
        plt.savefig(thumb_path, format='jpeg', dpi=120, bbox_inches='tight',
                   pad_inches=0.15, facecolor='white', edgecolor='none')
        plt.close(fig)

        # Update DB with thumbnail path
        relative_thumb_path = str(thumb_path.relative_to(project_path))

        with db.connection() as conn:
            conn.execute('''
                UPDATE tables SET thumbnail_path = ? WHERE file_path = ?
            ''', (relative_thumb_path, file_path))

        logger.debug(f"[TableThumbnail] Generated for {file_path}")

    except ImportError as e:
        logger.warning(f"[TableThumbnail] Missing dependency for {file_path}: {e}")
    except Exception as e:
        logger.error(f"[TableThumbnail] Error generating for {file_path}: {e}")


# EOF
