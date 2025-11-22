"""
SciTeX Cloud - Filesystem Utilities

Native filesystem operations for seamless local file integration.
This module provides utilities for working directly with the filesystem
without database intermediaries.
"""

import hashlib
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import mimetypes


class NativeFileHandler:
    """
    Handle native filesystem operations with zero database overhead.

    Philosophy: The filesystem IS the source of truth.
    Database only stores metadata and relationships.
    """

    # File extensions to show in UI
    VIEWABLE_EXTENSIONS = {
        ".py",
        ".md",
        ".txt",
        ".json",
        ".yaml",
        ".yml",
        ".csv",
        ".tex",
        ".bib",
        ".sh",
        ".r",
        ".R",
        ".ipynb",
        ".html",
        ".css",
        ".js",
    }

    # Binary files that need special handling
    BINARY_EXTENSIONS = {
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".svg",
        ".zip",
        ".tar",
        ".gz",
        ".pkl",
        ".npy",
        ".npz",
        ".h5",
        ".hdf5",
    }

    # Files to ignore
    IGNORE_PATTERNS = {
        "__pycache__",
        ".git",
        ".svn",
        ".hg",
        "node_modules",
        ".venv",
        "venv",
        ".env",
        ".DS_Store",
        "Thumbs.db",
        "*.pyc",
        "*.pyo",
    }

    @staticmethod
    def get_file_info(file_path: Path) -> Dict:
        """
        Get comprehensive file information directly from filesystem.

        No database queries - pure filesystem operations.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        stat = file_path.stat()

        # Determine file type
        is_text = NativeFileHandler.is_text_file(file_path)
        is_binary = file_path.suffix.lower() in NativeFileHandler.BINARY_EXTENSIONS

        info = {
            "name": file_path.name,
            "path": str(file_path),
            "size": stat.st_size,
            "size_human": NativeFileHandler._format_size(stat.st_size),
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "modified_timestamp": stat.st_mtime,
            "created": datetime.fromtimestamp(stat.st_ctime),
            "is_file": file_path.is_file(),
            "is_dir": file_path.is_dir(),
            "is_symlink": file_path.is_symlink(),
            "is_text": is_text,
            "is_binary": is_binary,
            "extension": file_path.suffix.lower(),
            "mime_type": mimetypes.guess_type(str(file_path))[0],
            "permissions": oct(stat.st_mode)[-3:],
        }

        # Add quick hash for change detection (only for small text files)
        if is_text and stat.st_size < 1024 * 100:  # < 100KB
            info["content_hash"] = NativeFileHandler.quick_hash(file_path)

        return info

    @staticmethod
    def list_directory(
        directory_path: Path, recursive: bool = False, include_hidden: bool = False
    ) -> List[Dict]:
        """
        List directory contents with metadata.

        Args:
            directory_path: Path to directory
            recursive: Include subdirectories
            include_hidden: Include hidden files (starting with .)

        Returns:
            List of file/directory info dictionaries
        """
        if not directory_path.exists() or not directory_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory_path}")

        items = []

        try:
            for item in directory_path.iterdir():
                # Skip hidden files unless requested
                if not include_hidden and item.name.startswith("."):
                    continue

                # Skip ignored patterns
                if NativeFileHandler._should_ignore(item):
                    continue

                try:
                    info = NativeFileHandler.get_file_info(item)
                    items.append(info)

                    # Recursive directory listing
                    if recursive and item.is_dir():
                        sub_items = NativeFileHandler.list_directory(
                            item, recursive=True, include_hidden=include_hidden
                        )
                        items.extend(sub_items)

                except (PermissionError, OSError):
                    # Skip files we can't access
                    continue

            # Sort: directories first, then by name
            items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))

        except PermissionError:
            raise PermissionError(f"Permission denied: {directory_path}")

        return items

    @staticmethod
    def read_file_content(
        file_path: Path, max_size: int = 1024 * 1024
    ) -> Tuple[bool, str]:
        """
        Read file content directly from filesystem.

        Args:
            file_path: Path to file
            max_size: Maximum file size to read (default 1MB)

        Returns:
            Tuple of (success, content or error_message)
        """
        if not file_path.exists():
            return False, "File not found"

        if not file_path.is_file():
            return False, "Not a file"

        # Check file size
        file_size = file_path.stat().st_size
        if file_size > max_size:
            return (
                False,
                f"File too large ({NativeFileHandler._format_size(file_size)}). Max size: {NativeFileHandler._format_size(max_size)}",
            )

        # Check if binary
        if not NativeFileHandler.is_text_file(file_path):
            return False, "Binary file - cannot display as text"

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            return True, content
        except Exception as e:
            return False, f"Error reading file: {str(e)}"

    @staticmethod
    def write_file_content(
        file_path: Path, content: str, create_dirs: bool = True
    ) -> Tuple[bool, str]:
        """
        Write content directly to filesystem.

        Args:
            file_path: Path to file
            content: Content to write
            create_dirs: Create parent directories if they don't exist

        Returns:
            Tuple of (success, message)
        """
        try:
            # Create parent directories if needed
            if create_dirs and not file_path.parent.exists():
                file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            file_path.write_text(content, encoding="utf-8")

            return (
                True,
                f"File saved successfully ({NativeFileHandler._format_size(len(content))})",
            )

        except PermissionError:
            return False, "Permission denied"
        except Exception as e:
            return False, f"Error writing file: {str(e)}"

    @staticmethod
    def is_text_file(file_path: Path) -> bool:
        """
        Determine if file is text (viewable/editable in UI).

        Uses heuristics:
        1. Known text extensions
        2. MIME type
        3. Content sampling (check for null bytes)
        """
        # Check extension
        if file_path.suffix.lower() in NativeFileHandler.VIEWABLE_EXTENSIONS:
            return True

        # Check MIME type
        mime_type = mimetypes.guess_type(str(file_path))[0]
        if mime_type and mime_type.startswith("text/"):
            return True

        # Sample first 8KB and check for null bytes
        try:
            sample_size = min(8192, file_path.stat().st_size)
            with open(file_path, "rb") as f:
                sample = f.read(sample_size)
                # If null byte found, it's binary
                return b"\x00" not in sample
        except (OSError, IOError, ValueError):
            # File access error or invalid path, treat as binary
            return False

    @staticmethod
    def quick_hash(file_path: Path) -> str:
        """
        Calculate quick hash for change detection.
        Uses MD5 of first/last blocks for large files.
        """
        hasher = hashlib.md5()
        file_size = file_path.stat().st_size

        # For small files, hash entire content
        if file_size < 1024 * 100:  # < 100KB
            hasher.update(file_path.read_bytes())
        else:
            # For large files, hash first 64KB + last 64KB
            block_size = 65536
            with open(file_path, "rb") as f:
                # First block
                hasher.update(f.read(block_size))
                # Last block
                f.seek(-min(block_size, file_size), 2)
                hasher.update(f.read())

        return hasher.hexdigest()

    @staticmethod
    def get_directory_stats(directory_path: Path) -> Dict:
        """
        Get statistics for a directory (size, file count, etc.)
        """
        total_size = 0
        file_count = 0
        dir_count = 0

        try:
            for item in directory_path.rglob("*"):
                if NativeFileHandler._should_ignore(item):
                    continue

                if item.is_file():
                    file_count += 1
                    try:
                        total_size += item.stat().st_size
                    except (OSError, IOError):
                        # Unable to stat file, skip its size
                        pass
                elif item.is_dir():
                    dir_count += 1
        except (OSError, IOError, PermissionError):
            # Unable to traverse directory, return partial results
            pass

        return {
            "total_size": total_size,
            "total_size_human": NativeFileHandler._format_size(total_size),
            "file_count": file_count,
            "directory_count": dir_count,
            "total_items": file_count + dir_count,
        }

    @staticmethod
    def find_files(
        directory_path: Path, pattern: str = "*", recursive: bool = True
    ) -> List[Path]:
        """
        Find files matching pattern.

        Args:
            directory_path: Directory to search
            pattern: Glob pattern (e.g., '*.py', '**/*.md')
            recursive: Search subdirectories

        Returns:
            List of matching file paths
        """
        if recursive:
            matches = list(directory_path.rglob(pattern))
        else:
            matches = list(directory_path.glob(pattern))

        # Filter out ignored files
        matches = [m for m in matches if not NativeFileHandler._should_ignore(m)]

        return matches

    @staticmethod
    def _should_ignore(path: Path) -> bool:
        """Check if path should be ignored based on patterns"""
        name = path.name

        # Check exact matches
        if name in NativeFileHandler.IGNORE_PATTERNS:
            return True

        # Check pattern matches (simple)
        for pattern in NativeFileHandler.IGNORE_PATTERNS:
            if pattern.startswith("*") and name.endswith(pattern[1:]):
                return True

        return False

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format byte size in human-readable format"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"


class ProjectFileScanner:
    """
    Scan project directories and provide structured views.
    No database dependencies - pure filesystem scanning.
    """

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.handler = NativeFileHandler()

    def scan_structure(self, max_depth: int = 3) -> Dict:
        """
        Scan project and return structured tree.

        Returns:
            Nested dictionary representing directory structure
        """

        def scan_dir(path: Path, depth: int = 0) -> Dict:
            if depth > max_depth:
                return {"truncated": True}

            try:
                items = self.handler.list_directory(path, recursive=False)

                result = {
                    "name": path.name,
                    "path": str(path.relative_to(self.project_path)),
                    "files": [],
                    "directories": [],
                }

                for item in items:
                    if item["is_dir"]:
                        sub_path = Path(item["path"])
                        sub_tree = scan_dir(sub_path, depth + 1)
                        result["directories"].append(sub_tree)
                    else:
                        result["files"].append(
                            {
                                "name": item["name"],
                                "size": item["size"],
                                "size_human": item["size_human"],
                                "modified": item["modified"].isoformat(),
                                "extension": item["extension"],
                            }
                        )

                return result

            except Exception as e:
                return {"error": str(e)}

        return scan_dir(self.project_path)

    def get_recent_files(self, limit: int = 10) -> List[Dict]:
        """Get most recently modified files"""
        all_files = self.handler.list_directory(self.project_path, recursive=True)

        # Filter to files only
        files = [f for f in all_files if f["is_file"]]

        # Sort by modification time
        files.sort(key=lambda x: x["modified_timestamp"], reverse=True)

        return files[:limit]

    def search_content(
        self, query: str, file_patterns: List[str] = ["*.py", "*.md", "*.txt"]
    ) -> List[Dict]:
        """
        Search file contents for query string.

        Args:
            query: Search string
            file_patterns: File patterns to search

        Returns:
            List of matches with context
        """
        results = []

        for pattern in file_patterns:
            files = self.handler.find_files(self.project_path, pattern)

            for file_path in files:
                try:
                    success, content = self.handler.read_file_content(file_path)
                    if not success:
                        continue

                    # Search for query
                    lines = content.split("\n")
                    for line_no, line in enumerate(lines, 1):
                        if query.lower() in line.lower():
                            results.append(
                                {
                                    "file": str(
                                        file_path.relative_to(self.project_path)
                                    ),
                                    "line": line_no,
                                    "content": line.strip(),
                                    "context": self._get_context(lines, line_no - 1),
                                }
                            )
                except (UnicodeDecodeError, OSError, IOError):
                    # Unable to read or decode file, skip it
                    continue

        return results

    @staticmethod
    def _get_context(
        lines: List[str], line_idx: int, context_lines: int = 2
    ) -> List[str]:
        """Get surrounding lines for context"""
        start = max(0, line_idx - context_lines)
        end = min(len(lines), line_idx + context_lines + 1)
        return lines[start:end]
