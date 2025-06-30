#!/usr/bin/env python3
"""
Jupyter notebook integration utilities for SciTeX-Code.
Provides secure notebook execution, conversion, and management.
"""

import os
import json
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

import nbformat
from nbconvert import HTMLExporter, PythonExporter, MarkdownExporter
from nbconvert.preprocessors import ExecutePreprocessor, ClearOutputPreprocessor
from jupyter_client import KernelManager
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone

from .models import Notebook, CodeExecutionJob

logger = logging.getLogger(__name__)


class NotebookExecutionError(Exception):
    """Raised when notebook execution fails."""
    pass


class NotebookValidator:
    """Validates and sanitizes Jupyter notebooks."""
    
    @staticmethod
    def validate_notebook(notebook_content: dict) -> Tuple[bool, List[str]]:
        """
        Validate notebook structure and content.
        
        Returns:
            (is_valid, errors)
        """
        errors = []
        
        # Basic structure validation
        required_fields = ['cells', 'metadata', 'nbformat', 'nbformat_minor']
        for field in required_fields:
            if field not in notebook_content:
                errors.append(f"Missing required field: {field}")
        
        # Check nbformat version
        if notebook_content.get('nbformat', 0) < 4:
            errors.append("Unsupported notebook format version")
        
        # Validate cells
        cells = notebook_content.get('cells', [])
        if not isinstance(cells, list):
            errors.append("Cells must be a list")
        
        for i, cell in enumerate(cells):
            if not isinstance(cell, dict):
                errors.append(f"Cell {i} must be a dictionary")
                continue
            
            if 'cell_type' not in cell:
                errors.append(f"Cell {i} missing cell_type")
            
            if cell.get('cell_type') not in ['code', 'markdown', 'raw']:
                errors.append(f"Cell {i} has invalid cell_type")
            
            if 'source' not in cell:
                errors.append(f"Cell {i} missing source")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_notebook(notebook_content: dict) -> dict:
        """Remove potentially dangerous content from notebook."""
        # Create a copy to avoid modifying original
        sanitized = json.loads(json.dumps(notebook_content))
        
        # Remove outputs that might contain sensitive data
        for cell in sanitized.get('cells', []):
            if cell.get('cell_type') == 'code':
                # Clear outputs but preserve execution count
                cell['outputs'] = []
                if 'execution_count' in cell:
                    cell['execution_count'] = None
        
        # Remove potentially sensitive metadata
        metadata = sanitized.get('metadata', {})
        sensitive_keys = ['kernelspec', 'language_info']
        for key in sensitive_keys:
            if key in metadata:
                if key == 'kernelspec':
                    # Keep basic kernelspec but remove paths
                    metadata[key] = {
                        'display_name': metadata[key].get('display_name', 'Python 3'),
                        'language': 'python',
                        'name': 'python3'
                    }
                elif key == 'language_info':
                    # Keep basic language info but remove paths
                    metadata[key] = {
                        'name': 'python',
                        'version': metadata[key].get('version', '3.11.0')
                    }
        
        return sanitized


class NotebookManager:
    """Manages Jupyter notebook operations."""
    
    def __init__(self, user):
        self.user = user
        self.base_path = Path(settings.MEDIA_ROOT) / 'notebooks' / str(user.id)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def create_notebook(self, title: str, description: str = '') -> Notebook:
        """Create a new empty notebook."""
        # Create basic notebook structure
        nb_content = {
            'cells': [
                {
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': [
                        f'# {title}\n',
                        f'\n{description}\n' if description else '\n',
                        'This notebook was created with SciTeX-Code.\n'
                    ]
                },
                {
                    'cell_type': 'code',
                    'execution_count': None,
                    'metadata': {},
                    'outputs': [],
                    'source': [
                        '# Welcome to SciTeX-Code!\n',
                        '# Start coding your analysis here\n',
                        'print("Hello, SciTeX!")'
                    ]
                }
            ],
            'metadata': {
                'kernelspec': {
                    'display_name': 'Python 3',
                    'language': 'python',
                    'name': 'python3'
                },
                'language_info': {
                    'name': 'python',
                    'version': '3.11.0'
                }
            },
            'nbformat': 4,
            'nbformat_minor': 4
        }
        
        # Save to database
        notebook = Notebook.objects.create(
            user=self.user,
            title=title,
            description=description,
            content=nb_content,
            status='draft'
        )
        
        # Save to file system
        notebook_path = self.base_path / f"{notebook.notebook_id}.ipynb"
        with open(notebook_path, 'w') as f:
            json.dump(nb_content, f, indent=2)
        
        notebook.file_path = str(notebook_path)
        notebook.save()
        
        logger.info(f"Created notebook '{title}' for user {self.user.username}")
        return notebook
    
    def load_notebook(self, notebook_id: str) -> Optional[Notebook]:
        """Load notebook from database."""
        try:
            return Notebook.objects.get(
                notebook_id=notebook_id,
                user=self.user
            )
        except Notebook.DoesNotExist:
            return None
    
    def save_notebook(self, notebook_id: str, content: dict) -> bool:
        """Save notebook content."""
        try:
            notebook = self.load_notebook(notebook_id)
            if not notebook:
                return False
            
            # Validate content
            is_valid, errors = NotebookValidator.validate_notebook(content)
            if not is_valid:
                logger.error(f"Invalid notebook content: {errors}")
                return False
            
            # Sanitize content
            sanitized_content = NotebookValidator.sanitize_notebook(content)
            
            # Update database
            notebook.content = sanitized_content
            notebook.updated_at = timezone.now()
            notebook.save()
            
            # Save to file system
            if notebook.file_path and os.path.exists(notebook.file_path):
                with open(notebook.file_path, 'w') as f:
                    json.dump(sanitized_content, f, indent=2)
            
            logger.info(f"Saved notebook {notebook_id} for user {self.user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving notebook {notebook_id}: {e}")
            return False
    
    def duplicate_notebook(self, notebook_id: str, new_title: str) -> Optional[Notebook]:
        """Create a copy of an existing notebook."""
        try:
            original = self.load_notebook(notebook_id)
            if not original:
                return None
            
            # Create new notebook with copied content
            new_notebook = Notebook.objects.create(
                user=self.user,
                title=new_title,
                description=f"Copy of {original.title}",
                content=original.content,
                status='draft'
            )
            
            # Save to file system
            notebook_path = self.base_path / f"{new_notebook.notebook_id}.ipynb"
            with open(notebook_path, 'w') as f:
                json.dump(original.content, f, indent=2)
            
            new_notebook.file_path = str(notebook_path)
            new_notebook.save()
            
            return new_notebook
            
        except Exception as e:
            logger.error(f"Error duplicating notebook {notebook_id}: {e}")
            return None


class NotebookExecutor:
    """Executes Jupyter notebooks safely."""
    
    def __init__(self, timeout: int = 300, memory_limit: int = 512):
        self.timeout = timeout
        self.memory_limit = memory_limit
    
    def execute_notebook(self, notebook: Notebook, 
                        execution_job: Optional[CodeExecutionJob] = None) -> Tuple[bool, Dict]:
        """
        Execute a Jupyter notebook safely.
        
        Returns:
            (success, result_data)
        """
        if execution_job:
            execution_job.status = 'running'
            execution_job.started_at = timezone.now()
            execution_job.save()
        
        try:
            # Load notebook content
            nb_content = notebook.content
            nb = nbformat.from_dict(nb_content)
            
            # Create execution environment
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Set up execution preprocessor
                ep = ExecutePreprocessor(
                    timeout=self.timeout,
                    kernel_name='python3',
                    allow_errors=True
                )
                
                # Execute notebook
                start_time = timezone.now()
                executed_nb, resources = ep.preprocess(nb, {'metadata': {'path': str(temp_path)}})
                end_time = timezone.now()
                
                # Extract results
                execution_time = (end_time - start_time).total_seconds()
                outputs = []
                errors = []
                
                for cell in executed_nb.cells:
                    if cell.cell_type == 'code' and cell.outputs:
                        for output in cell.outputs:
                            if output.output_type == 'stream':
                                outputs.append({
                                    'type': 'stream',
                                    'name': output.name,
                                    'text': ''.join(output.text)
                                })
                            elif output.output_type == 'execute_result':
                                outputs.append({
                                    'type': 'result',
                                    'execution_count': output.execution_count,
                                    'data': output.data
                                })
                            elif output.output_type == 'display_data':
                                outputs.append({
                                    'type': 'display',
                                    'data': output.data
                                })
                            elif output.output_type == 'error':
                                errors.append({
                                    'ename': output.ename,
                                    'evalue': output.evalue,
                                    'traceback': output.traceback
                                })
                
                # Update notebook with execution results
                notebook.content = nbformat.to_dict(executed_nb)
                notebook.last_executed = timezone.now()
                notebook.execution_count += 1
                notebook.status = 'completed' if not errors else 'failed'
                notebook.save()
                
                # Update execution job if provided
                if execution_job:
                    execution_job.status = 'completed' if not errors else 'failed'
                    execution_job.completed_at = timezone.now()
                    execution_job.execution_time = execution_time
                    execution_job.output = json.dumps(outputs, indent=2)
                    if errors:
                        execution_job.error_output = json.dumps(errors, indent=2)
                    execution_job.save()
                
                result_data = {
                    'execution_time': execution_time,
                    'outputs': outputs,
                    'errors': errors,
                    'cells_executed': len([c for c in executed_nb.cells if c.cell_type == 'code'])
                }
                
                logger.info(f"Successfully executed notebook {notebook.notebook_id}")
                return True, result_data
                
        except Exception as e:
            logger.error(f"Error executing notebook {notebook.notebook_id}: {e}")
            
            # Update job status
            if execution_job:
                execution_job.status = 'failed'
                execution_job.completed_at = timezone.now()
                execution_job.error_output = str(e)
                execution_job.save()
            
            # Update notebook status
            notebook.status = 'failed'
            notebook.save()
            
            return False, {'error': str(e)}
    
    def execute_cell(self, notebook: Notebook, cell_index: int) -> Tuple[bool, Dict]:
        """Execute a single cell in the notebook."""
        try:
            nb_content = notebook.content
            if cell_index >= len(nb_content.get('cells', [])):
                return False, {'error': 'Cell index out of range'}
            
            cell = nb_content['cells'][cell_index]
            if cell.get('cell_type') != 'code':
                return False, {'error': 'Can only execute code cells'}
            
            # Create a temporary notebook with just this cell
            temp_nb_content = {
                'cells': [cell],
                'metadata': nb_content.get('metadata', {}),
                'nbformat': nb_content.get('nbformat', 4),
                'nbformat_minor': nb_content.get('nbformat_minor', 4)
            }
            
            temp_nb = nbformat.from_dict(temp_nb_content)
            
            # Execute
            ep = ExecutePreprocessor(
                timeout=60,  # Shorter timeout for single cell
                kernel_name='python3',
                allow_errors=True
            )
            
            executed_nb, _ = ep.preprocess(temp_nb)
            executed_cell = executed_nb.cells[0]
            
            # Extract outputs
            outputs = []
            errors = []
            
            for output in executed_cell.outputs:
                if output.output_type == 'stream':
                    outputs.append({
                        'type': 'stream',
                        'name': output.name,
                        'text': ''.join(output.text)
                    })
                elif output.output_type == 'execute_result':
                    outputs.append({
                        'type': 'result',
                        'execution_count': output.execution_count,
                        'data': output.data
                    })
                elif output.output_type == 'error':
                    errors.append({
                        'ename': output.ename,
                        'evalue': output.evalue,
                        'traceback': output.traceback
                    })
            
            # Update the cell in the original notebook
            nb_content['cells'][cell_index] = nbformat.to_dict(executed_cell)
            notebook.content = nb_content
            notebook.save()
            
            return True, {
                'outputs': outputs,
                'errors': errors,
                'execution_count': executed_cell.execution_count
            }
            
        except Exception as e:
            logger.error(f"Error executing cell {cell_index} in notebook {notebook.notebook_id}: {e}")
            return False, {'error': str(e)}


class NotebookConverter:
    """Converts notebooks to different formats."""
    
    @staticmethod
    def to_html(notebook: Notebook) -> str:
        """Convert notebook to HTML."""
        try:
            nb = nbformat.from_dict(notebook.content)
            html_exporter = HTMLExporter()
            html_content, _ = html_exporter.from_notebook_node(nb)
            return html_content
        except Exception as e:
            logger.error(f"Error converting notebook to HTML: {e}")
            return f"<p>Error converting notebook: {e}</p>"
    
    @staticmethod
    def to_python(notebook: Notebook) -> str:
        """Convert notebook to Python script."""
        try:
            nb = nbformat.from_dict(notebook.content)
            python_exporter = PythonExporter()
            python_content, _ = python_exporter.from_notebook_node(nb)
            return python_content
        except Exception as e:
            logger.error(f"Error converting notebook to Python: {e}")
            return f"# Error converting notebook: {e}"
    
    @staticmethod
    def to_markdown(notebook: Notebook) -> str:
        """Convert notebook to Markdown."""
        try:
            nb = nbformat.from_dict(notebook.content)
            md_exporter = MarkdownExporter()
            md_content, _ = md_exporter.from_notebook_node(nb)
            return md_content
        except Exception as e:
            logger.error(f"Error converting notebook to Markdown: {e}")
            return f"Error converting notebook: {e}"


class NotebookTemplates:
    """Provides pre-built notebook templates."""
    
    @staticmethod
    def get_data_analysis_template() -> dict:
        """Get data analysis notebook template."""
        return {
            'cells': [
                {
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': [
                        '# Data Analysis with SciTeX\n',
                        '\n',
                        'This notebook template provides a structured approach to data analysis.\n',
                        '\n',
                        '## Objectives\n',
                        '- [ ] Data loading and exploration\n',
                        '- [ ] Data preprocessing\n',
                        '- [ ] Analysis and visualization\n',
                        '- [ ] Results and conclusions\n'
                    ]
                },
                {
                    'cell_type': 'code',
                    'execution_count': None,
                    'metadata': {},
                    'outputs': [],
                    'source': [
                        '# Import required libraries\n',
                        'import pandas as pd\n',
                        'import numpy as np\n',
                        'import matplotlib.pyplot as plt\n',
                        'import seaborn as sns\n',
                        '\n',
                        '# Set plotting style\n',
                        'plt.style.use("default")\n',
                        'sns.set_palette("husl")\n'
                    ]
                },
                {
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## 1. Data Loading\n']
                },
                {
                    'cell_type': 'code',
                    'execution_count': None,
                    'metadata': {},
                    'outputs': [],
                    'source': [
                        '# Load your data here\n',
                        '# df = pd.read_csv("your_data.csv")\n',
                        '# print(f"Data shape: {df.shape}")\n'
                    ]
                },
                {
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## 2. Data Exploration\n']
                },
                {
                    'cell_type': 'code',
                    'execution_count': None,
                    'metadata': {},
                    'outputs': [],
                    'source': [
                        '# Explore your data\n',
                        '# df.head()\n',
                        '# df.info()\n',
                        '# df.describe()\n'
                    ]
                },
                {
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## 3. Analysis and Results\n']
                },
                {
                    'cell_type': 'code',
                    'execution_count': None,
                    'metadata': {},
                    'outputs': [],
                    'source': [
                        '# Your analysis code here\n'
                    ]
                }
            ],
            'metadata': {
                'kernelspec': {
                    'display_name': 'Python 3',
                    'language': 'python',
                    'name': 'python3'
                },
                'language_info': {
                    'name': 'python',
                    'version': '3.11.0'
                }
            },
            'nbformat': 4,
            'nbformat_minor': 4
        }
    
    @staticmethod
    def get_machine_learning_template() -> dict:
        """Get machine learning notebook template."""
        return {
            'cells': [
                {
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': [
                        '# Machine Learning Project\n',
                        '\n',
                        'This template provides a structured approach to machine learning projects.\n'
                    ]
                },
                {
                    'cell_type': 'code',
                    'execution_count': None,
                    'metadata': {},
                    'outputs': [],
                    'source': [
                        '# Import ML libraries\n',
                        'import pandas as pd\n',
                        'import numpy as np\n',
                        'from sklearn.model_selection import train_test_split\n',
                        'from sklearn.preprocessing import StandardScaler\n',
                        'from sklearn.metrics import classification_report, confusion_matrix\n',
                        'import matplotlib.pyplot as plt\n',
                        'import seaborn as sns\n'
                    ]
                },
                {
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## 1. Data Preparation\n']
                },
                {
                    'cell_type': 'code',
                    'execution_count': None,
                    'metadata': {},
                    'outputs': [],
                    'source': [
                        '# Load and prepare your data\n'
                    ]
                },
                {
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## 2. Feature Engineering\n']
                },
                {
                    'cell_type': 'code',
                    'execution_count': None,
                    'metadata': {},
                    'outputs': [],
                    'source': [
                        '# Feature selection and engineering\n'
                    ]
                },
                {
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## 3. Model Training\n']
                },
                {
                    'cell_type': 'code',
                    'execution_count': None,
                    'metadata': {},
                    'outputs': [],
                    'source': [
                        '# Train your models\n'
                    ]
                },
                {
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## 4. Model Evaluation\n']
                },
                {
                    'cell_type': 'code',
                    'execution_count': None,
                    'metadata': {},
                    'outputs': [],
                    'source': [
                        '# Evaluate model performance\n'
                    ]
                }
            ],
            'metadata': {
                'kernelspec': {
                    'display_name': 'Python 3',
                    'language': 'python',
                    'name': 'python3'
                },
                'language_info': {
                    'name': 'python',
                    'version': '3.11.0'
                }
            },
            'nbformat': 4,
            'nbformat_minor': 4
        }
    
    @staticmethod
    def get_visualization_template() -> dict:
        """Get data visualization notebook template."""
        return {
            'cells': [
                {
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': [
                        '# Data Visualization Project\n',
                        '\n',
                        'Create publication-ready visualizations with this template.\n'
                    ]
                },
                {
                    'cell_type': 'code',
                    'execution_count': None,
                    'metadata': {},
                    'outputs': [],
                    'source': [
                        '# Import visualization libraries\n',
                        'import matplotlib.pyplot as plt\n',
                        'import seaborn as sns\n',
                        'import plotly.express as px\n',
                        'import plotly.graph_objects as go\n',
                        'import pandas as pd\n',
                        'import numpy as np\n',
                        '\n',
                        '# Set style for publication-ready plots\n',
                        'plt.rcParams["figure.figsize"] = (10, 6)\n',
                        'plt.rcParams["font.size"] = 12\n',
                        'plt.rcParams["axes.linewidth"] = 1.5\n'
                    ]
                },
                {
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## Static Plots with Matplotlib/Seaborn\n']
                },
                {
                    'cell_type': 'code',
                    'execution_count': None,
                    'metadata': {},
                    'outputs': [],
                    'source': [
                        '# Create static visualizations\n'
                    ]
                },
                {
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': ['## Interactive Plots with Plotly\n']
                },
                {
                    'cell_type': 'code',
                    'execution_count': None,
                    'metadata': {},
                    'outputs': [],
                    'source': [
                        '# Create interactive visualizations\n'
                    ]
                }
            ],
            'metadata': {
                'kernelspec': {
                    'display_name': 'Python 3',
                    'language': 'python',
                    'name': 'python3'
                },
                'language_info': {
                    'name': 'python',
                    'version': '3.11.0'
                }
            },
            'nbformat': 4,
            'nbformat_minor': 4
        }