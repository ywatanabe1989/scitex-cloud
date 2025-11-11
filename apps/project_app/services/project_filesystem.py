"""
SciTeX Cloud - User Directory Management System

This module handles user-specific directory trees with a minimal structure.

Minimal Directory Structure:
./data/users/{username}/
├── {project-slug}/                 # Project directories (1:1 with Django Project + Gitea repo)
│   ├── .git/                       # Git repository
│   ├── README.md
│   ├── scitex/                     # (Optional) SciTeX-specific project metadata
│   │   ├── scholar/                # Bibliography, enriched BibTeX files
│   │   ├── writer/                 # LaTeX compilation artifacts
│   │   ├── code/                   # Analysis tracking
│   │   └── viz/                    # Visualization outputs
│   └── ...                         # User's project structure
└── workspace_info.json             # User workspace metadata

Design Philosophy:
- Projects are self-contained Git repositories
- SciTeX features use project-slug/scitex/ subdirectory (created on-demand)
- No global shared/temp directories - keeps things simple
- Future expansions go under scitex/ to avoid namespace conflicts
"""

import os
import shutil
import json
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.text import slugify
from ..models import Project
# from apps.document_app.models import Document  # Removed - document_app not installed


class ProjectFilesystemManager:
    """Manages user-specific directory structures for SciTeX Cloud."""
    
    # Standardized scientific research project structure
    PROJECT_STRUCTURE = {
        'config': [],  # Configuration files (YAML, JSON, etc.)
        'data': {
            'raw': [],  # Raw datasets
            'processed': [],  # Processed/cleaned data
            'figures': [],  # Generated figures and plots
            'models': []  # Trained models
        },
        'scripts': [],  # Main scripts directory (will contain project-specific subdirs)
        'docs': ['manuscripts', 'notes', 'references'],  # Documentation
        'results': ['outputs', 'reports', 'analysis'],  # Results and analysis
        'temp': ['cache', 'logs', 'tmp']  # Temporary files
    }
    
    def __init__(self, user: User):
        self.user = user
        self.base_path = self._get_user_base_path()
        
    def _get_user_base_path(self) -> Path:
        """
        Get the base directory path for the user.

        Structure: ./data/users/{username}/
        All projects go directly under this directory.
        """
        return Path(settings.BASE_DIR) / 'data' / 'users' / self.user.username
    
    def _ensure_directory(self, path: Path) -> bool:
        """Ensure a directory exists, create if it doesn't."""
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {path}: {e}")
            return False
    
    def initialize_user_workspace(self) -> bool:
        """Initialize minimal user workspace - just the base directory."""
        try:
            # Create base user directory only
            # Projects will be created directly under this directory
            if not self._ensure_directory(self.base_path):
                return False

            # Create user workspace info file
            self._create_workspace_info()

            return True
        except Exception as e:
            print(f"Error initializing user workspace: {e}")
            return False
    
    def create_project_directory(self, project: Project, use_template: bool = False, template_type: str = 'research') -> Tuple[bool, Optional[Path]]:
        """
        Create directory structure for a new repository.

        Path: ./data/users/{username}/{project-slug}/

        Args:
            project: Project instance
            use_template: If True, create full template structure. If False, create empty directory.
            template_type: Type of template to use ('research', 'pip_project', 'singularity')
        """
        try:
            project_slug = project.slug  # Use the generated slug

            # Minimal structure: ./data/users/{username}/{project-slug}/
            project_path = self.base_path / project_slug

            # Ensure user base directory exists
            if not self._ensure_directory(self.base_path):
                return False, None

            # If template requested, try to copy from scitex template
            if use_template and self._copy_from_example_template(project_path, project, template_type):
                # Update project with directory info
                project.data_location = str(project_path.relative_to(self.base_path))
                project.directory_created = True
                project.save()
                return True, project_path

            # Create empty project root directory
            if not self._ensure_directory(project_path):
                return False, None

            # Only create basic README for empty projects
            self._create_minimal_readme(project, project_path)

            # Note: .scitex_project.json removed - metadata already in database
            # self._create_project_metadata(project, project_path)

            # Update project model with directory path
            project.data_location = str(project_path.relative_to(self.base_path))
            project.directory_created = True
            project.save()

            return True, project_path
        except Exception as e:
            print(f"Error creating project directory: {e}")
            return False, None

    def create_project_from_template(self, project: Project, template_type: str = 'research') -> Tuple[bool, Optional[Path]]:
        """
        Create full template structure for an existing project.
        This can be called when user clicks "Create from template" button.

        Args:
            project: Project instance
            template_type: Type of template ('research', 'pip_project', or 'singularity')
        """
        try:
            project_path = self.get_project_root_path(project)
            if not project_path:
                return False, None

            # Try to use scitex template if available
            if self._copy_from_example_template(project_path, project, template_type):
                return True, project_path

            # Fallback: Create manual structure if scitex template fails
            # Create project subdirectories with scientific workflow structure
            for main_dir, sub_structure in self.PROJECT_STRUCTURE.items():
                main_path = project_path / main_dir
                if not self._ensure_directory(main_path):
                    return False, None

                # Create additional subdirectories under scripts for scientific workflow
                if main_dir == 'scripts':
                    script_subdirs = ['analysis', 'preprocessing', 'modeling', 'visualization', 'utils']
                    for subdir in script_subdirs:
                        if not self._ensure_directory(main_path / subdir):
                            return False, None

                if isinstance(sub_structure, dict):
                    # Handle nested structure (like data directory)
                    for sub_dir, sub_sub_dirs in sub_structure.items():
                        sub_path = main_path / sub_dir
                        if not self._ensure_directory(sub_path):
                            return False, None

                        for sub_sub_dir in sub_sub_dirs:
                            if not self._ensure_directory(sub_path / sub_sub_dir):
                                return False, None
                elif isinstance(sub_structure, list):
                    # Handle simple list structure
                    for sub_dir in sub_structure:
                        if not self._ensure_directory(main_path / sub_dir):
                            return False, None

            # Update README with full template info
            self._create_project_readme(project, project_path)

            # Create project configuration files
            self._create_project_config_files(project, project_path)

            # Create requirements.txt
            self._create_requirements_file(project, project_path)

            return True, project_path
        except Exception as e:
            print(f"Error creating project from template: {e}")
            return False, None
    
    def get_project_root_path(self, project: Project) -> Optional[Path]:
        """Get the root directory path for a project.

        Always uses filesystem as the source of truth (data/users/{username}/{project-slug}/).
        This ensures Django always shows the actual filesystem state in real-time.
        """
        # Always use project slug - filesystem is the single source of truth
        project_path = self.base_path / project.slug
        if project_path.exists():
            return project_path
        return None
    
    def store_document(self, document, content: str,
                      doc_type: str = 'manuscripts') -> Tuple[bool, Optional[Path]]:
        """Store a document in the appropriate project directory."""
        try:
            if not document.project:
                # Store in temp if no project
                file_path = self.base_path / 'temp' / f"{document.id}_{document.title}.txt"
            else:
                project_path = self.get_project_root_path(document.project)
                if not project_path:
                    return False, None
                
                # Determine file extension based on document type
                extension = self._get_file_extension(document.document_type)
                filename = f"{slugify(document.title)}{extension}"
                file_path = project_path / 'documents' / doc_type / filename
            
            # Ensure parent directory exists
            if not self._ensure_directory(file_path.parent):
                return False, None
            
            # Write content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Update document model with file path
            document.file_location = str(file_path.relative_to(self.base_path))
            document.save()
            
            return True, file_path
        except Exception as e:
            print(f"Error storing document: {e}")
            return False, None
    
    def store_file(self, project: Project, file_content: bytes, 
                  filename: str, category: str = 'data') -> Tuple[bool, Optional[Path]]:
        """Store a file in the project directory."""
        try:
            project_path = self.get_project_root_path(project)
            if not project_path:
                return False, None
            
            # Determine subcategory based on file type
            subcategory = self._get_subcategory(filename, category)
            file_path = project_path / category / subcategory / filename
            
            # Ensure parent directory exists
            if not self._ensure_directory(file_path.parent):
                return False, None
            
            # Write file content
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            return True, file_path
        except Exception as e:
            print(f"Error storing file: {e}")
            return False, None
    
    def list_project_files(self, project: Project, 
                          category: Optional[str] = None) -> List[Dict]:
        """List files in a project directory."""
        try:
            project_path = self.get_project_root_path(project)
            if not project_path or not project_path.exists():
                return []
            
            files = []
            search_path = project_path / category if category else project_path
            
            for file_path in search_path.rglob('*'):
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        'name': file_path.name,
                        'path': str(file_path.relative_to(project_path)),
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime),
                        'category': file_path.parent.parent.name if file_path.parent.parent != project_path else 'root',
                        'subcategory': file_path.parent.name if file_path.parent != project_path else ''
                    })
            
            return sorted(files, key=lambda x: x['modified'], reverse=True)
        except Exception as e:
            print(f"Error listing project files: {e}")
            return []
    
    def get_project_structure(self, project: Project) -> Dict:
        """Get the complete directory structure for a project."""
        try:
            project_path = self.get_project_root_path(project)
            if not project_path or not project_path.exists():
                return {}
            
            def build_tree(path: Path) -> Dict:
                tree = {
                    'name': path.name,
                    'type': 'directory' if path.is_dir() else 'file',
                    'path': str(path.relative_to(project_path)),
                    'children': []
                }
                
                if path.is_dir():
                    for child in sorted(path.iterdir()):
                        tree['children'].append(build_tree(child))
                else:
                    stat = path.stat()
                    tree.update({
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                
                return tree
            
            return build_tree(project_path)
        except Exception as e:
            print(f"Error getting project structure: {e}")
            return {}
    
    def delete_project_directory(self, project: Project) -> bool:
        """Delete a project directory and all its contents."""
        try:
            project_path = self.get_project_root_path(project)
            if project_path and project_path.exists():
                shutil.rmtree(project_path)
            return True
        except Exception as e:
            print(f"Error deleting project directory: {e}")
            return False
    
    def _copy_from_example_template(self, project_path: Path, project, template_type: str = 'research') -> bool:
        """
        Copy structure from template using scitex package.

        Args:
            project_path: Path where project will be created
            project: Project instance
            template_type: Type of template ('research', 'pip_project', or 'singularity')
        """
        try:
            # Import appropriate template creator based on type
            if template_type == 'research':
                from scitex.template.create_research import create_research as create_template
            elif template_type == 'pip_project':
                from scitex.template.create_pip_project import create_pip_project as create_template
            elif template_type == 'singularity':
                from scitex.template.create_singularity import create_singularity as create_template
            else:
                print(f"Unknown template type: {template_type}, defaulting to research")
                from scitex.template.create_research import create_research as create_template

            # Create the project using scitex template function
            # Note: template functions expect project_name and target_dir
            # They create: target_dir/project_name/
            # So we need to pass parent as target_dir and project_slug as name
            if not project_path.parent.exists():
                project_path.parent.mkdir(parents=True, exist_ok=True)

            # Call scitex to create the project from template
            # Template functions create target_dir/project_name, so pass parent and name
            create_template(project_path.name, str(project_path.parent))

            # Customize copied template for this project
            self._customize_template_for_project(project_path, project, template_type)

            print(f"Successfully created {template_type} project using scitex at {project_path}")
            return True

        except ImportError as e:
            print(f"scitex package not available: {e}")
            print("Fallback: Project will be created with basic structure")
            return False
        except Exception as e:
            print(f"Error creating {template_type} project template: {e}")
            return False
    
    def _customize_template_for_project(self, project_path: Path, project, template_type: str = 'research'):
        """Customize the copied template with project-specific information."""
        try:
            # Update README.md with project info
            readme_path = project_path / 'README.md'
            if readme_path.exists():
                readme_content = readme_path.read_text()
                # Replace template placeholders with actual project info
                readme_content = readme_content.replace(
                    '# SciTeX Example Research Project',
                    f'# {project.name}'
                )
                readme_content = readme_content.replace(
                    'This is an example research project',
                    f'{project.description or "Research project created with SciTeX Cloud"}'
                )
                readme_path.write_text(readme_content)
            
            # Update paper title in LaTeX files if they exist
            paper_dir = project_path / 'paper'
            if paper_dir.exists():
                # Update manuscript title
                title_file = paper_dir / 'manuscript' / 'src' / 'title.tex'
                if title_file.exists():
                    title_file.write_text(f'\\title{{{project.name}}}')
                
                # Update author
                author_file = paper_dir / 'manuscript' / 'src' / 'authors.tex'
                if author_file.exists() and project.owner:
                    author_name = project.owner.get_full_name() or project.owner.username
                    author_file.write_text(f'\\author{{{author_name}}}')
            
            print(f"Customized template for project: {project.name}")
            
        except Exception as e:
            print(f"Error customizing template: {e}")
    
    
    def get_storage_usage(self) -> Dict:
        """Get storage usage statistics for the user."""
        try:
            if not self.base_path.exists():
                return {'total_size': 0, 'project_count': 0, 'file_count': 0}

            total_size = 0
            file_count = 0

            for file_path in self.base_path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    file_count += 1

            # Count projects directly under base_path
            project_count = len([p for p in self.base_path.iterdir() if p.is_dir() and not p.name.startswith('.')])

            return {
                'total_size': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'project_count': project_count,
                'file_count': file_count
            }
        except Exception as e:
            print(f"Error getting storage usage: {e}")
            return {'total_size': 0, 'project_count': 0, 'file_count': 0}
    
    def _create_workspace_info(self):
        """Create workspace information file."""
        info = {
            'user_id': self.user.id,
            'username': self.user.username,
            'created_at': datetime.now().isoformat(),
            'version': '1.0',
            'structure_version': '1.0'
        }
        
        info_path = self.base_path / 'workspace_info.json'
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=2)
    
    def _create_minimal_readme(self, project: Project, project_path: Path):
        """Create minimal README file for empty projects."""
        readme_content = f"""# {project.name}

**Created:** {project.created_at.strftime('%Y-%m-%d')}
**Owner:** {project.owner.get_full_name() or project.owner.username}

## Description

{project.description or 'No description provided.'}

## Getting Started

This is an empty project directory. You can:

1. **Create from template** - Click the "Create from template" button to set up a full SciTeX research project structure
2. **Upload your files** - Upload your existing project files through the web interface
3. **Create manually** - Organize your project structure as you prefer

---
*Created with SciTeX Cloud*
"""

        readme_path = project_path / 'README.md'
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

    def _create_project_readme(self, project: Project, project_path: Path):
        """Create README file for the project."""
        readme_content = f"""# {project.name}

**Created:** {project.created_at.strftime('%Y-%m-%d')}
**Owner:** {project.owner.get_full_name() or project.owner.username}
**Progress:** {getattr(project, 'progress', 0)}%

## Description

{project.description or 'No description provided.'}

## Hypotheses

{project.hypotheses or 'No hypotheses defined.'}

## Directory Structure

This project follows the standardized SciTeX research project structure:

- `config/` - Configuration files (YAML, JSON, etc.)
  - Project-specific configuration files
  - PATH configurations and environment settings
- `data/` - Research data and datasets
  - `raw/` - Original, unprocessed datasets
  - `processed/` - Cleaned and preprocessed data
  - `figures/` - Generated figures and visualizations
  - `models/` - Trained machine learning models
- `scripts/` - Source code and analysis scripts
  - Script-specific output directories with execution logs
  - Individual Python/R scripts for data processing and analysis
  - Execution tracking with RUNNING/FINISHED_SUCCESS markers
- `docs/` - Documentation and manuscripts
  - `manuscripts/` - Draft papers and publications
  - `notes/` - Research notes and documentation
  - `references/` - Citations and reference materials
- `results/` - Analysis outputs and reports
  - `outputs/` - Generated results and analysis outputs
  - `reports/` - Summary reports and findings
  - `analysis/` - Detailed analysis results
- `temp/` - Temporary and cache files
  - `cache/` - Cached computations and intermediate results
  - `logs/` - Execution logs and debugging information
  - `tmp/` - Temporary processing files

The structure supports:
- Symlinked data organization for efficient storage
- Script execution tracking with timestamped logs
- Reproducible research workflows
- Version control integration

## Getting Started

This project directory is managed by SciTeX Cloud. You can:

1. Upload files using the web interface
2. Edit documents in the Writer module
3. Run code in the Code module
4. Create visualizations in the Viz module
5. Manage references in the Scholar module

## Project Management

- Project ID: {project.id}
- Created: {project.created_at.strftime('%Y-%m-%d %H:%M:%S')}
- Last Updated: {project.updated_at.strftime('%Y-%m-%d %H:%M:%S')}

---
*This README was automatically generated by SciTeX Cloud*
"""
        
        readme_path = project_path / 'README.md'
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    # REMOVED: .scitex_project.json is redundant (metadata already in database)
    # def _create_project_metadata(self, project: Project, project_path: Path):
    #     """Create project metadata file."""
    #     metadata = {
    #         'project_id': project.id,
    #         'name': project.name,
    #         'slug': slugify(project.name),
    #         'description': project.description,
    #         'progress': getattr(project, 'progress', 0),
    #         'owner_id': project.owner.id,
    #         'created_at': project.created_at.isoformat(),
    #         'updated_at': project.updated_at.isoformat(),
    #         'directory_created_at': datetime.now().isoformat(),
    #         'structure_version': '1.0'
    #     }
    #
    #     metadata_path = project_path / '.scitex_project.json'
    #     with open(metadata_path, 'w') as f:
    #         json.dump(metadata, f, indent=2)

    def initialize_scitex_writer_template(self, project: Project) -> Tuple[bool, Optional[Path]]:
        """
        Initialize SciTeX Writer template structure for a project.

        Delegates to ensure_writer_directory from writer_app which uses
        scitex.writer.Writer() to properly initialize the complete workspace
        with all required directories, scripts, and configuration files.

        Args:
            project: Project instance

        Returns:
            Tuple of (success: bool, path: Optional[Path])
        """
        try:
            # Initialize Writer workspace using WriterService
            from apps.writer_app.services import WriterService
            import logging
            logger = logging.getLogger(__name__)

            # Create WriterService - this initializes Writer() which creates the complete structure
            writer_service = WriterService(project.id, project.owner.id)

            # Access the writer property - this triggers initialization
            writer = writer_service.writer
            writer_path = writer_service.writer_dir

            if writer_path and writer_path.exists():
                logger.info(f"✓ Writer template initialized successfully at: {writer_path}")
                return True, writer_path
            else:
                logger.warning(f"Writer initialization returned path but directory doesn't exist: {writer_path}")
                return False, None

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error initializing SciTeX Writer template: {e}", exc_info=True)

            # Check if writer directory was created despite the error
            from pathlib import Path
            expected_writer_dir = self.base_path / project.slug / 'scitex' / 'writer'
            if expected_writer_dir.exists() and (expected_writer_dir / '01_manuscript').exists():
                logger.warning(f"Writer directory exists despite error - considering it successful: {expected_writer_dir}")
                return True, expected_writer_dir

            return False, None

    def _get_file_extension(self, doc_type: str) -> str:
        """Get appropriate file extension for document type."""
        extensions = {
            'note': '.md',
            'manuscript': '.tex',
            'paper': '.tex',
            'report': '.md',
            'presentation': '.md',
            'dataset': '.csv',
            'code': '.py'
        }
        return extensions.get(doc_type, '.txt')
    
    def _get_subcategory(self, filename: str, category: str) -> str:
        """Determine subcategory based on file type and category."""
        extension = Path(filename).suffix.lower()
        
        if category == 'data':
            if extension in ['.csv', '.xlsx', '.json', '.xml', '.gz', '.zip']:
                return 'raw'
            elif extension in ['.pkl', '.parquet', '.h5', '.npy', '.npz']:
                return 'processed'
            elif extension in ['.png', '.jpg', '.jpeg', '.svg', '.pdf']:
                return 'figures'
            elif extension in ['.pkl', '.joblib', '.h5', '.pt', '.pth']:
                return 'models'
            else:
                return 'raw'
        elif category == 'scripts':
            # Scripts go directly in scripts directory, subdirs created as needed
            return ''
        elif category == 'docs':
            if extension in ['.tex', '.bib']:
                return 'manuscripts'
            elif extension in ['.md', '.txt', '.rst']:
                return 'notes'
            else:
                return 'references'
        elif category == 'results':
            if extension in ['.csv', '.json', '.txt']:
                return 'outputs'
            elif extension in ['.pdf', '.html']:
                return 'reports'
            else:
                return 'analysis'
        elif category == 'temp':
            if extension in ['.log']:
                return 'logs'
            elif extension in ['.tmp', '.temp']:
                return 'tmp'
            else:
                return 'cache'
        elif category == 'config':
            return ''
        
        return 'misc'
    
    def _create_project_config_files(self, project: Project, project_path: Path):
        """Create essential configuration files for the project."""
        config_path = project_path / 'config'
        
        # Create project.yaml - main project configuration
        project_config = {
            'project': {
                'name': project.name,
                'id': project.id,
                'description': project.description,
                'created': project.created_at.isoformat(),
                'owner': project.owner.username,
                'progress': getattr(project, 'progress', 0)
            },
            'paths': {
                'data_raw': './data/raw',
                'data_processed': './data/processed',
                'data_figures': './data/figures',
                'data_models': './data/models',
                'scripts': './scripts',
                'results': './results',
                'docs': './docs',
                'temp': './temp'
            },
            'execution': {
                'python_version': '3.8+',
                'requirements_file': '../requirements.txt',
                'log_level': 'INFO',
                'cache_enabled': True
            },
            'research': {
                'hypotheses': project.hypotheses or '',
                'keywords': [],
                'collaborators': []
            }
        }
        
        if HAS_YAML:
            with open(config_path / 'project.yaml', 'w') as f:
                yaml.dump(project_config, f, default_flow_style=False, indent=2)
        else:
            # Fallback to JSON if YAML is not available
            with open(config_path / 'project.json', 'w') as f:
                json.dump(project_config, f, indent=2)
        
        # Create paths.json for script access
        paths_config = {
            "data": {
                "raw": str(project_path / 'data' / 'raw'),
                "processed": str(project_path / 'data' / 'processed'),
                "figures": str(project_path / 'data' / 'figures'),
                "models": str(project_path / 'data' / 'models')
            },
            "scripts": str(project_path / 'scripts'),
            "results": {
                "outputs": str(project_path / 'results' / 'outputs'),
                "reports": str(project_path / 'results' / 'reports'),
                "analysis": str(project_path / 'results' / 'analysis')
            },
            "docs": str(project_path / 'docs'),
            "temp": {
                "cache": str(project_path / 'temp' / 'cache'),
                "logs": str(project_path / 'temp' / 'logs'),
                "tmp": str(project_path / 'temp' / 'tmp')
            }
        }
        
        with open(config_path / 'paths.json', 'w') as f:
            json.dump(paths_config, f, indent=2)
        
        # Create environment template
        env_template = f"""# SciTeX Project Environment Configuration
# Project: {project.name}

# Python Environment
PYTHON_PATH=./scripts
PYTHONPATH=${{PYTHONPATH}}:./scripts

# Data Paths
DATA_RAW=./data/raw
DATA_PROCESSED=./data/processed
DATA_FIGURES=./data/figures
DATA_MODELS=./data/models

# Output Paths
RESULTS_OUTPUT=./results/outputs
RESULTS_REPORTS=./results/reports
RESULTS_ANALYSIS=./results/analysis

# Temporary Paths
TEMP_CACHE=./temp/cache
TEMP_LOGS=./temp/logs
TEMP_TMP=./temp/tmp

# Project Settings
PROJECT_NAME="{project.name}"
PROJECT_ID={project.id}
LOG_LEVEL=INFO
CACHE_ENABLED=true

# Add your custom environment variables below
# API_KEY=your_api_key_here
# SCITEX_CLOUD_POSTGRES_URL=your_database_url_here
"""
        
        with open(config_path / '.env.template', 'w') as f:
            f.write(env_template)
    
    def _create_requirements_file(self, project: Project, project_path: Path):
        """Create requirements.txt with essential scientific packages."""
        requirements = """# SciTeX Project Requirements
# Core scientific computing packages
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
scipy>=1.7.0

# Data processing and analysis
scikit-learn>=1.0.0
statsmodels>=0.12.0

# Visualization
plotly>=5.0.0
bokeh>=2.4.0

# Jupyter and interactive computing
jupyter>=1.0.0
ipykernel>=6.0.0
nbformat>=5.1.0

# File I/O and data formats
openpyxl>=3.0.0
xlrd>=2.0.0
h5py>=3.1.0

# Development and testing
pytest>=6.2.0
black>=21.0.0
flake8>=3.9.0

# Documentation
sphinx>=4.0.0
sphinx-rtd-theme>=0.5.0

# Add your project-specific requirements below:
# tensorflow>=2.6.0
# torch>=1.9.0
# transformers>=4.9.0
"""
        
        with open(project_path / 'requirements.txt', 'w') as f:
            f.write(requirements)
    
    def create_script_execution_tracker(self, project: Project, script_name: str) -> Tuple[bool, Optional[Path]]:
        """Create execution tracking for a script with RUNNING/FINISHED_SUCCESS markers."""
        try:
            project_path = self.get_project_root_path(project)
            if not project_path:
                return False, None
            
            # Create script-specific directory
            script_base = Path(script_name).stem  # Remove extension
            script_dir = project_path / 'scripts' / script_base
            
            if not self._ensure_directory(script_dir):
                return False, None
            
            # Create execution tracking structure
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            execution_dir = script_dir / f'execution_{timestamp}'
            
            if not self._ensure_directory(execution_dir):
                return False, None
            
            # Create RUNNING marker
            running_marker = execution_dir / 'RUNNING'
            with open(running_marker, 'w') as f:
                f.write(f"""Script: {script_name}
Started: {datetime.now().isoformat()}
Status: Running
PID: {os.getpid()}
""")
            
            # Create logs directory
            logs_dir = execution_dir / 'logs'
            if not self._ensure_directory(logs_dir):
                return False, None
            
            # Create output directories
            for output_dir in ['outputs', 'figures', 'data']:
                if not self._ensure_directory(execution_dir / output_dir):
                    return False, None
            
            return True, execution_dir
        except Exception as e:
            print(f"Error creating script execution tracker: {e}")
            return False, None
    
    def mark_script_finished(self, execution_dir: Path, success: bool = True, error_msg: str = None) -> bool:
        """Mark script execution as finished with success/failure status."""
        try:
            if not execution_dir.exists():
                return False
            
            # Remove RUNNING marker
            running_marker = execution_dir / 'RUNNING'
            if running_marker.exists():
                running_marker.unlink()
            
            # Create appropriate finish marker
            if success:
                marker = execution_dir / 'FINISHED_SUCCESS'
                status = 'Completed Successfully'
            else:
                marker = execution_dir / 'FINISHED_ERROR'
                status = 'Failed'
            
            with open(marker, 'w') as f:
                f.write(f"""Status: {status}
Finished: {datetime.now().isoformat()}
Duration: {datetime.now().isoformat()}
Error: {error_msg or 'None'}
""")
            
            # Create execution summary
            summary_file = execution_dir / 'execution_summary.json'
            summary = {
                'script_name': execution_dir.parent.name,
                'execution_id': execution_dir.name,
                'started_at': None,  # Would need to read from RUNNING marker
                'finished_at': datetime.now().isoformat(),
                'success': success,
                'error_message': error_msg,
                'output_files': [f.name for f in execution_dir.rglob('*') if f.is_file() and f.name not in ['RUNNING', 'FINISHED_SUCCESS', 'FINISHED_ERROR']],
                'logs_available': (execution_dir / 'logs').exists()
            }
            
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error marking script as finished: {e}")
            return False
    
    def clone_from_git(self, project: Project, git_url: str, use_ssh: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Clone a Git repository into the project directory.

        Args:
            project: Project instance
            git_url: Git repository URL (works with GitHub, GitLab, Bitbucket, etc.)
            use_ssh: If True and SSH key exists, use SSH for cloning

        Returns:
            Tuple of (success, error_message)
        """
        try:
            import subprocess
            import tempfile

            project_path = self.get_project_root_path(project)
            if not project_path or not project_path.exists():
                return False, "Project directory not found"

            # Get SSH environment if available
            env = os.environ.copy()
            ssh_used = False

            if use_ssh:
                from .ssh_manager import SSHKeyManager
                ssh_manager = SSHKeyManager(self.user)

                if ssh_manager.has_ssh_key():
                    env = ssh_manager.get_ssh_env()
                    ssh_used = True

            # Strategy: Clone to a temporary directory, then move contents
            # This avoids the "destination path already exists and is not an empty directory" error

            # Create a temporary directory for cloning
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_clone_path = Path(temp_dir) / 'repo'

                # Clone the repository into the temporary directory
                result = subprocess.run(
                    ['git', 'clone', git_url, str(temp_clone_path)],
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                    env=env
                )

                if result.returncode != 0:
                    error_msg = result.stderr or result.stdout or "Unknown error"
                    return False, error_msg

                # Remove any existing files in the project directory (created during initialization)
                for item in project_path.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)

                # Move all contents from temp clone to project directory
                for item in temp_clone_path.iterdir():
                    dest = project_path / item.name
                    if item.is_file():
                        shutil.copy2(item, dest)
                    elif item.is_dir():
                        shutil.copytree(item, dest)

            # Mark SSH key as used if it was used
            if ssh_used:
                from .ssh_manager import SSHKeyManager
                ssh_manager = SSHKeyManager(self.user)
                ssh_manager.mark_key_used()

            return True, None

        except subprocess.TimeoutExpired:
            return False, "Git clone operation timed out (max 5 minutes)"
        except FileNotFoundError:
            return False, "Git command not found. Please ensure Git is installed."
        except Exception as e:
            return False, str(e)

    def get_script_executions(self, project: Project, script_name: str = None) -> List[Dict]:
        """Get execution history for scripts in the project."""
        try:
            project_path = self.get_project_root_path(project)
            if not project_path:
                return []
            
            scripts_path = project_path / 'scripts'
            if not scripts_path.exists():
                return []
            
            executions = []
            
            # If specific script requested, only check that one
            if script_name:
                script_base = Path(script_name).stem
                script_dirs = [scripts_path / script_base] if (scripts_path / script_base).exists() else []
            else:
                script_dirs = [d for d in scripts_path.iterdir() if d.is_dir()]
            
            for script_dir in script_dirs:
                for execution_dir in script_dir.iterdir():
                    if execution_dir.is_dir() and execution_dir.name.startswith('execution_'):
                        # Check for status markers
                        if (execution_dir / 'RUNNING').exists():
                            status = 'running'
                        elif (execution_dir / 'FINISHED_SUCCESS').exists():
                            status = 'success'
                        elif (execution_dir / 'FINISHED_ERROR').exists():
                            status = 'error'
                        else:
                            status = 'unknown'
                        
                        # Try to load execution summary
                        summary_file = execution_dir / 'execution_summary.json'
                        if summary_file.exists():
                            with open(summary_file, 'r') as f:
                                summary = json.load(f)
                        else:
                            summary = {}
                        
                        executions.append({
                            'script_name': script_dir.name,
                            'execution_id': execution_dir.name,
                            'status': status,
                            'path': str(execution_dir.relative_to(project_path)),
                            'timestamp': execution_dir.name.split('_', 1)[1] if '_' in execution_dir.name else '',
                            'summary': summary
                        })
            
            # Sort by timestamp (newest first)
            executions.sort(key=lambda x: x['timestamp'], reverse=True)
            return executions
        except Exception as e:
            print(f"Error getting script executions: {e}")
            return []


def get_project_filesystem_manager(user: User) -> ProjectFilesystemManager:
    """Get or create a ProjectFilesystemManager for the user."""
    manager = ProjectFilesystemManager(user)
    
    # Initialize workspace if it doesn't exist
    if not manager.base_path.exists():
        manager.initialize_user_workspace()
    
    return manager


def ensure_project_directory(project: Project) -> bool:
    """Ensure a project has a directory structure."""
    manager = get_project_filesystem_manager(project.owner)
    
    # Check if project already has a directory
    if not manager.get_project_root_path(project):
        success, path = manager.create_project_directory(project)
        return success
    
    return True