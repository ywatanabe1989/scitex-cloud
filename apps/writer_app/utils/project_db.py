#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project-specific SQLite database for figures/tables metadata.

This module provides fast, portable indexing of media files in SciTeX projects.
The database is stored in scitex/metadata.db within each project directory.
"""

import sqlite3
import json
import time
from pathlib import Path
from contextlib import contextmanager
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ProjectDatabase:
    """
    Project-specific SQLite database for figures/tables metadata.

    Provides fast querying (<50ms) of figures and tables without scanning
    the file system. Database is portable and stored within the project.

    Location: {project_root}/scitex/metadata.db
    """

    def __init__(self, project_path: Path):
        """
        Initialize project database.

        Args:
            project_path: Root path of the project
        """
        self.project_path = Path(project_path)
        self.scitex_dir = self.project_path / 'scitex'
        self.db_path = self.scitex_dir / 'metadata.db'
        self.thumbnails_dir = self.scitex_dir / 'thumbnails'

        # Ensure directories exist
        self.scitex_dir.mkdir(exist_ok=True)
        self.thumbnails_dir.mkdir(exist_ok=True)

        # Initialize database
        self._initialize_db()

        # Run migrations
        self._run_migrations()

        logger.info(f"[ProjectDB] Initialized database at {self.db_path}")

    def _initialize_db(self):
        """Create tables if they don't exist."""
        with self.connection() as conn:
            conn.executescript('''
                -- Figures metadata table
                CREATE TABLE IF NOT EXISTS figures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_name TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    file_type TEXT NOT NULL,

                    -- Metadata
                    last_modified REAL NOT NULL,
                    thumbnail_path TEXT,

                    -- Auto-extracted
                    tags TEXT,
                    is_referenced INTEGER DEFAULT 0,
                    reference_count INTEGER DEFAULT 0,

                    -- Discovery info
                    source TEXT,
                    location TEXT,

                    -- Index tracking
                    indexed_at REAL NOT NULL,

                    UNIQUE(file_path)
                );

                -- Indexes for fast queries
                CREATE INDEX IF NOT EXISTS idx_file_hash ON figures(file_hash);
                CREATE INDEX IF NOT EXISTS idx_last_modified ON figures(last_modified);
                CREATE INDEX IF NOT EXISTS idx_is_referenced ON figures(is_referenced);
                CREATE INDEX IF NOT EXISTS idx_source ON figures(source);
                CREATE INDEX IF NOT EXISTS idx_file_type ON figures(file_type);

                -- LaTeX references tracking
                CREATE TABLE IF NOT EXISTS latex_references (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    figure_id INTEGER NOT NULL,
                    tex_file TEXT NOT NULL,
                    line_number INTEGER,
                    context TEXT,
                    FOREIGN KEY (figure_id) REFERENCES figures(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_latex_ref_figure ON latex_references(figure_id);

                -- Full-text search (FTS5)
                CREATE VIRTUAL TABLE IF NOT EXISTS figures_fts USING fts5(
                    file_name,
                    location,
                    tags,
                    content='figures',
                    content_rowid='id'
                );

                -- Trigger to keep FTS in sync
                CREATE TRIGGER IF NOT EXISTS figures_fts_insert AFTER INSERT ON figures BEGIN
                    INSERT INTO figures_fts(rowid, file_name, location, tags)
                    VALUES (new.id, new.file_name, new.location, new.tags);
                END;

                CREATE TRIGGER IF NOT EXISTS figures_fts_update AFTER UPDATE ON figures BEGIN
                    UPDATE figures_fts SET file_name = new.file_name, location = new.location, tags = new.tags
                    WHERE rowid = new.id;
                END;

                CREATE TRIGGER IF NOT EXISTS figures_fts_delete AFTER DELETE ON figures BEGIN
                    DELETE FROM figures_fts WHERE rowid = old.id;
                END;

                -- Tables metadata table (similar to figures)
                CREATE TABLE IF NOT EXISTS tables (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_name TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    caption TEXT,

                    -- Metadata
                    last_modified REAL NOT NULL,
                    thumbnail_path TEXT,

                    -- Auto-extracted
                    tags TEXT,
                    is_referenced INTEGER DEFAULT 0,
                    reference_count INTEGER DEFAULT 0,

                    -- Discovery info
                    source TEXT,
                    location TEXT,

                    -- Index tracking
                    indexed_at REAL NOT NULL,

                    UNIQUE(file_path)
                );

                CREATE INDEX IF NOT EXISTS idx_table_is_referenced ON tables(is_referenced);
                CREATE INDEX IF NOT EXISTS idx_table_source ON tables(source);
            ''')

    def _run_migrations(self):
        """Run database migrations for schema updates."""
        with self.connection() as conn:
            # Migration: Add thumbnail_path to tables (2025-01-14)
            try:
                conn.execute('SELECT thumbnail_path FROM tables LIMIT 1')
            except sqlite3.OperationalError:
                # Column doesn't exist, add it
                conn.execute('ALTER TABLE tables ADD COLUMN thumbnail_path TEXT')
                logger.info("[ProjectDB] Migration: Added thumbnail_path column to tables")

    @contextmanager
    def connection(self):
        """
        Context manager for database connection.

        Yields:
            sqlite3.Connection with row_factory set to Row
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dicts
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"[ProjectDB] Database error: {e}")
            raise e
        finally:
            conn.close()

    def upsert_figure(self, metadata: dict):
        """
        Insert or update figure metadata.

        Args:
            metadata: Dictionary with keys:
                - file_path: Relative path from project root
                - file_name: Just the filename
                - file_hash: SHA256 hash for change detection
                - file_size: Size in bytes
                - file_type: Extension (png, pdf, etc.)
                - last_modified: Unix timestamp
                - thumbnail_path: Relative path to thumbnail (optional)
                - tags: List of tags (optional)
                - is_referenced: Boolean (optional, default False)
                - reference_count: Integer (optional, default 0)
                - source: Category (paper, pool, data, scripts)
                - location: Directory path
        """
        with self.connection() as conn:
            conn.execute('''
                INSERT INTO figures (
                    file_path, file_name, file_hash, file_size, file_type,
                    last_modified, thumbnail_path, tags,
                    is_referenced, reference_count,
                    source, location, indexed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(file_path) DO UPDATE SET
                    file_name = excluded.file_name,
                    file_hash = excluded.file_hash,
                    file_size = excluded.file_size,
                    last_modified = excluded.last_modified,
                    thumbnail_path = excluded.thumbnail_path,
                    tags = excluded.tags,
                    is_referenced = excluded.is_referenced,
                    reference_count = excluded.reference_count,
                    indexed_at = excluded.indexed_at
            ''', (
                metadata['file_path'],
                metadata['file_name'],
                metadata['file_hash'],
                metadata['file_size'],
                metadata['file_type'],
                metadata['last_modified'],
                metadata.get('thumbnail_path'),
                json.dumps(metadata.get('tags', [])),
                metadata.get('is_referenced', 0),
                metadata.get('reference_count', 0),
                metadata['source'],
                metadata['location'],
                time.time(),
            ))

            logger.debug(f"[ProjectDB] Upserted figure: {metadata['file_name']}")

    def get_all_figures(self, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Get all figures with optional filters.

        Args:
            filters: Optional dictionary with keys:
                - source: Filter by source (paper, pool, data, scripts)
                - is_referenced: Filter by reference status (True/False)
                - file_type: Filter by file type (png, pdf, etc.)

        Returns:
            List of figure dictionaries
        """
        query = 'SELECT * FROM figures WHERE 1=1'
        params = []

        if filters:
            if filters.get('source'):
                query += ' AND source = ?'
                params.append(filters['source'])

            if filters.get('is_referenced') is not None:
                query += ' AND is_referenced = ?'
                params.append(int(filters['is_referenced']))

            if filters.get('file_type'):
                query += ' AND file_type = ?'
                params.append(filters['file_type'])

        query += ' ORDER BY last_modified DESC'

        with self.connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            figures = []
            for row in rows:
                fig = dict(row)
                # Parse JSON tags
                fig['tags'] = json.loads(fig['tags']) if fig['tags'] else []
                figures.append(fig)

            logger.debug(f"[ProjectDB] Retrieved {len(figures)} figures")
            return figures

    def search_figures(self, query: str) -> List[Dict]:
        """
        Full-text search across figures.

        Args:
            query: Search query string

        Returns:
            List of matching figure dictionaries
        """
        with self.connection() as conn:
            cursor = conn.execute('''
                SELECT figures.* FROM figures
                JOIN figures_fts ON figures.id = figures_fts.rowid
                WHERE figures_fts MATCH ?
                ORDER BY rank
            ''', (query,))

            rows = cursor.fetchall()
            figures = []
            for row in rows:
                fig = dict(row)
                fig['tags'] = json.loads(fig['tags']) if fig['tags'] else []
                figures.append(fig)

            logger.debug(f"[ProjectDB] Search '{query}' found {len(figures)} figures")
            return figures

    def upsert_table(self, metadata: dict):
        """
        Insert or update table metadata.

        Args:
            metadata: Dictionary with keys:
                - file_path: Relative path from project root
                - file_name: Just the filename
                - file_hash: SHA256 hash for change detection
                - caption: Table caption (optional)
                - last_modified: Unix timestamp
                - tags: List of tags (optional)
                - is_referenced: Boolean (optional, default False)
                - reference_count: Integer (optional, default 0)
                - source: Category (paper, pool, data, scripts)
                - location: Directory path
        """
        with self.connection() as conn:
            conn.execute('''
                INSERT INTO tables (
                    file_path, file_name, file_hash, caption,
                    last_modified, thumbnail_path, tags,
                    is_referenced, reference_count,
                    source, location, indexed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(file_path) DO UPDATE SET
                    file_name = excluded.file_name,
                    file_hash = excluded.file_hash,
                    caption = excluded.caption,
                    last_modified = excluded.last_modified,
                    thumbnail_path = excluded.thumbnail_path,
                    tags = excluded.tags,
                    is_referenced = excluded.is_referenced,
                    reference_count = excluded.reference_count,
                    indexed_at = excluded.indexed_at
            ''', (
                metadata['file_path'],
                metadata['file_name'],
                metadata['file_hash'],
                metadata.get('caption'),
                metadata['last_modified'],
                metadata.get('thumbnail_path'),
                json.dumps(metadata.get('tags', [])),
                metadata.get('is_referenced', 0),
                metadata.get('reference_count', 0),
                metadata['source'],
                metadata['location'],
                time.time()
            ))

    def get_all_tables(self, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Get all tables with optional filters.

        Args:
            filters: Optional dictionary with keys:
                - source: Filter by source (paper, pool, data, scripts)
                - is_referenced: Filter by reference status (True/False)

        Returns:
            List of table dictionaries
        """
        query = 'SELECT * FROM tables WHERE 1=1'
        params = []

        if filters:
            if filters.get('source'):
                query += ' AND source = ?'
                params.append(filters['source'])

            if filters.get('is_referenced') is not None:
                query += ' AND is_referenced = ?'
                params.append(int(filters['is_referenced']))

        query += ' ORDER BY last_modified DESC'

        with self.connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            tables = []
            for row in rows:
                table = dict(row)
                # Parse JSON tags
                table['tags'] = json.loads(table['tags']) if table['tags'] else []
                tables.append(table)

            logger.debug(f"[ProjectDB] Retrieved {len(tables)} tables")
            return tables

    def get_stats(self) -> Dict:
        """
        Get statistics about figures.

        Returns:
            Dictionary with stats:
                - total: Total number of figures
                - referenced: Number of referenced figures
                - sources: Number of distinct sources
                - total_size: Total size in bytes
        """
        with self.connection() as conn:
            cursor = conn.execute('''
                SELECT
                    COUNT(*) as total,
                    SUM(is_referenced) as referenced,
                    COUNT(DISTINCT source) as sources,
                    SUM(file_size) as total_size
                FROM figures
            ''')
            stats = dict(cursor.fetchone())

            # Handle NULL values
            stats['referenced'] = stats['referenced'] or 0
            stats['sources'] = stats['sources'] or 0
            stats['total_size'] = stats['total_size'] or 0

            return stats

    def check_if_indexed(self, file_path: str, file_hash: str, table_type: str = 'figure') -> bool:
        """
        Check if file is already indexed with same hash.

        Args:
            file_path: Relative file path
            file_hash: SHA256 hash of file
            table_type: 'figure' or 'table' (default: 'figure')

        Returns:
            True if file is indexed with same hash (no need to re-index)
        """
        table_name = 'tables' if table_type == 'table' else 'figures'
        with self.connection() as conn:
            cursor = conn.execute(
                f'SELECT file_hash FROM {table_name} WHERE file_path = ?',
                (file_path,)
            )
            row = cursor.fetchone()
            return row is not None and row['file_hash'] == file_hash

    def delete_figure(self, file_path: str):
        """
        Delete figure from database.

        Args:
            file_path: Relative file path
        """
        with self.connection() as conn:
            conn.execute('DELETE FROM figures WHERE file_path = ?', (file_path,))
            logger.debug(f"[ProjectDB] Deleted figure: {file_path}")

    def update_references(self, figure_id: int, is_referenced: bool, reference_count: int):
        """
        Update reference status for a figure.

        Args:
            figure_id: Figure ID
            is_referenced: Whether figure is referenced
            reference_count: Number of references
        """
        with self.connection() as conn:
            conn.execute('''
                UPDATE figures
                SET is_referenced = ?, reference_count = ?
                WHERE id = ?
            ''', (int(is_referenced), reference_count, figure_id))

    def add_latex_reference(self, figure_id: int, tex_file: str, line_number: int = None, context: str = None):
        """
        Add a LaTeX reference record.

        Args:
            figure_id: Figure ID
            tex_file: Path to .tex file
            line_number: Line number (optional)
            context: Context text (optional)
        """
        with self.connection() as conn:
            conn.execute('''
                INSERT INTO latex_references (figure_id, tex_file, line_number, context)
                VALUES (?, ?, ?, ?)
            ''', (figure_id, tex_file, line_number, context))

    def clear_latex_references(self, figure_id: int):
        """
        Clear all LaTeX references for a figure.

        Args:
            figure_id: Figure ID
        """
        with self.connection() as conn:
            conn.execute('DELETE FROM latex_references WHERE figure_id = ?', (figure_id,))


def get_project_db(project) -> ProjectDatabase:
    """
    Get ProjectDatabase instance for a project.

    Args:
        project: Project model instance

    Returns:
        ProjectDatabase instance
    """
    from pathlib import Path

    # Determine project path based on git_clone_path or filesystem manager
    if hasattr(project, 'git_clone_path') and project.git_clone_path:
        # Use git_clone_path if available (for authenticated users)
        project_path = Path(project.git_clone_path)
        logger.debug(f"[ProjectDB] Using git_clone_path for project {project.id}: {project_path}")
    else:
        # Use ProjectFilesystemManager for visitor projects or projects without git_clone_path
        try:
            from apps.project_app.services.project_filesystem import get_project_filesystem_manager

            if not hasattr(project, 'owner') or not project.owner:
                raise ValueError(f"Project {project.id} has no owner")

            manager = get_project_filesystem_manager(project.owner)
            project_path = manager.get_project_root_path(project)

            if not project_path:
                raise ValueError(f"Project path not found for project {project.id} (slug: {project.slug})")

            logger.info(f"[ProjectDB] Using filesystem manager path for project {project.id}: {project_path}")
        except Exception as e:
            logger.error(f"[ProjectDB] Could not determine project path: {e}", exc_info=True)
            raise ValueError(f"Cannot determine project path for project {project.id}: {e}")

    return ProjectDatabase(project_path)


# EOF
