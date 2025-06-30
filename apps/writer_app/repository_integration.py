"""
Repository integration for Writer manuscripts.
Integrates manuscript submissions with research data repositories for 
data sharing, supplementary materials, and reproducible research.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from django.utils import timezone
from django.core.files.base import ContentFile
from django.db import transaction

from .models import Manuscript, Citation, ArxivSubmission
from apps.scholar_app.models import (
    Dataset, DatasetFile, RepositoryConnection, SearchIndex
)
from apps.scholar_app.repository_services import (
    RepositoryServiceFactory, upload_dataset_to_repository
)

logger = logging.getLogger(__name__)


class ManuscriptRepositoryIntegrator:
    """Service for integrating manuscripts with research data repositories"""
    
    def __init__(self, manuscript: Manuscript, repository_connection: Optional[RepositoryConnection] = None):
        self.manuscript = manuscript
        self.repository_connection = repository_connection or self._get_default_connection()
        
    def _get_default_connection(self) -> Optional[RepositoryConnection]:
        """Get user's default repository connection"""
        return RepositoryConnection.objects.filter(
            user=self.manuscript.owner,
            is_default=True,
            status='active'
        ).first()
    
    def create_supplementary_dataset(self, title: str = None, 
                                   description: str = None,
                                   auto_upload: bool = True) -> Optional[Dataset]:
        """Create a supplementary dataset for the manuscript"""
        
        if not self.repository_connection:
            logger.warning(f"No repository connection available for user {self.manuscript.owner.username}")
            return None
        
        try:
            with transaction.atomic():
                # Create dataset
                dataset_title = title or f"Supplementary Data for: {self.manuscript.title}"
                dataset_description = description or self._generate_dataset_description()
                
                dataset = Dataset.objects.create(
                    title=dataset_title,
                    description=dataset_description,
                    dataset_type='supplementary',
                    owner=self.manuscript.owner,
                    repository_connection=self.repository_connection,
                    keywords=self._generate_keywords(),
                    status='draft',
                    license='CC-BY-4.0'  # Default open license
                )
                
                # Link dataset to manuscript
                dataset.cited_in_manuscripts.add(self.manuscript)
                
                # Add manuscript files to dataset
                self._add_manuscript_files_to_dataset(dataset)
                
                # Auto-upload if requested
                if auto_upload:
                    upload_dataset_to_repository(dataset)
                
                logger.info(f"Created supplementary dataset {dataset.id} for manuscript {self.manuscript.slug}")
                return dataset
                
        except Exception as e:
            logger.error(f"Failed to create supplementary dataset: {e}")
            return None
    
    def create_replication_dataset(self, code_outputs: List = None,
                                 analysis_data: List = None,
                                 auto_upload: bool = True) -> Optional[Dataset]:
        """Create a replication dataset with code and data for reproducibility"""
        
        if not self.repository_connection:
            logger.warning(f"No repository connection available for user {self.manuscript.owner.username}")
            return None
        
        try:
            with transaction.atomic():
                dataset = Dataset.objects.create(
                    title=f"Replication Data for: {self.manuscript.title}",
                    description=self._generate_replication_description(),
                    dataset_type='replication_data',
                    owner=self.manuscript.owner,
                    repository_connection=self.repository_connection,
                    keywords=f"replication, reproducibility, {self._generate_keywords()}",
                    status='draft',
                    license='CC-BY-4.0'
                )
                
                # Link dataset to manuscript
                dataset.cited_in_manuscripts.add(self.manuscript)
                
                # Add replication materials
                self._add_replication_materials_to_dataset(dataset, code_outputs, analysis_data)
                
                # Auto-upload if requested
                if auto_upload:
                    upload_dataset_to_repository(dataset)
                
                logger.info(f"Created replication dataset {dataset.id} for manuscript {self.manuscript.slug}")
                return dataset
                
        except Exception as e:
            logger.error(f"Failed to create replication dataset: {e}")
            return None
    
    def link_existing_datasets(self, dataset_ids: List[str]) -> int:
        """Link existing datasets to the manuscript"""
        
        linked_count = 0
        
        for dataset_id in dataset_ids:
            try:
                dataset = Dataset.objects.get(
                    id=dataset_id,
                    owner=self.manuscript.owner
                )
                dataset.cited_in_manuscripts.add(self.manuscript)
                linked_count += 1
                
            except Dataset.DoesNotExist:
                logger.warning(f"Dataset {dataset_id} not found or not owned by user")
        
        logger.info(f"Linked {linked_count} datasets to manuscript {self.manuscript.slug}")
        return linked_count
    
    def generate_data_availability_statement(self) -> str:
        """Generate a data availability statement for the manuscript"""
        
        linked_datasets = Dataset.objects.filter(
            cited_in_manuscripts=self.manuscript
        ).select_related('repository_connection__repository')
        
        if not linked_datasets.exists():
            return "No datasets are associated with this manuscript."
        
        statement = "Data Availability Statement:\n\n"
        
        for dataset in linked_datasets:
            if dataset.repository_doi:
                statement += f"• {dataset.title}: {dataset.repository_doi}\n"
            elif dataset.repository_url:
                statement += f"• {dataset.title}: {dataset.repository_url}\n"
            else:
                statement += f"• {dataset.title}: Available in {dataset.repository_connection.repository.name}\n"
        
        statement += "\nAll datasets are made available under their respective licenses. "
        statement += "Please cite the datasets when reusing the data."
        
        return statement
    
    def get_citation_entries_for_datasets(self) -> List[Dict]:
        """Generate citation entries for linked datasets"""
        
        linked_datasets = Dataset.objects.filter(
            cited_in_manuscripts=self.manuscript
        ).select_related('repository_connection__repository')
        
        citations = []
        
        for dataset in linked_datasets:
            citation = {
                'type': 'dataset',
                'title': dataset.title,
                'author': dataset.owner.get_full_name() or dataset.owner.username,
                'year': dataset.published_at.year if dataset.published_at else dataset.created_at.year,
                'publisher': dataset.repository_connection.repository.name,
                'doi': dataset.repository_doi,
                'url': dataset.repository_url,
                'version': dataset.version,
                'keywords': dataset.keywords
            }
            
            # Add collaborators as additional authors
            collaborators = dataset.collaborators.all()
            if collaborators:
                authors = [dataset.owner.get_full_name() or dataset.owner.username]
                authors.extend([c.get_full_name() or c.username for c in collaborators])
                citation['author'] = ' and '.join(authors)
            
            citations.append(citation)
        
        return citations
    
    def create_arxiv_dataset_for_submission(self, arxiv_submission: ArxivSubmission) -> Optional[Dataset]:
        """Create a dataset for arXiv submission materials"""
        
        if not self.repository_connection:
            logger.warning(f"No repository connection available for user {self.manuscript.owner.username}")
            return None
        
        try:
            with transaction.atomic():
                dataset = Dataset.objects.create(
                    title=f"arXiv Submission Materials: {arxiv_submission.title}",
                    description=self._generate_arxiv_dataset_description(arxiv_submission),
                    dataset_type='supplementary',
                    owner=self.manuscript.owner,
                    repository_connection=self.repository_connection,
                    keywords=f"arxiv, preprint, {self._generate_keywords()}",
                    status='draft',
                    license='CC-BY-4.0'
                )
                
                # Link dataset to manuscript
                dataset.cited_in_manuscripts.add(self.manuscript)
                
                # Add arXiv submission files
                self._add_arxiv_files_to_dataset(dataset, arxiv_submission)
                
                logger.info(f"Created arXiv dataset {dataset.id} for submission {arxiv_submission.submission_id}")
                return dataset
                
        except Exception as e:
            logger.error(f"Failed to create arXiv dataset: {e}")
            return None
    
    def _generate_dataset_description(self) -> str:
        """Generate a description for the supplementary dataset"""
        
        description = f"Supplementary data and materials for the manuscript:\n\n"
        description += f"Title: {self.manuscript.title}\n"
        description += f"Authors: {self.manuscript.owner.get_full_name() or self.manuscript.owner.username}"
        
        collaborators = self.manuscript.collaborators.all()
        if collaborators:
            collab_names = [c.get_full_name() or c.username for c in collaborators]
            description += f", {', '.join(collab_names)}"
        
        description += f"\n\nAbstract:\n{self.manuscript.abstract}\n\n"
        description += f"Keywords: {self.manuscript.keywords}\n\n"
        description += f"This dataset contains supplementary materials, data, and other resources "
        description += f"that support the findings presented in the manuscript."
        
        if self.manuscript.target_journal:
            description += f"\n\nTarget Journal: {self.manuscript.target_journal}"
        
        return description
    
    def _generate_replication_description(self) -> str:
        """Generate a description for the replication dataset"""
        
        description = f"Replication materials for the manuscript:\n\n"
        description += f"Title: {self.manuscript.title}\n"
        description += f"Authors: {self.manuscript.owner.get_full_name() or self.manuscript.owner.username}"
        
        collaborators = self.manuscript.collaborators.all()
        if collaborators:
            collab_names = [c.get_full_name() or c.username for c in collaborators]
            description += f", {', '.join(collab_names)}"
        
        description += f"\n\nAbstract:\n{self.manuscript.abstract}\n\n"
        description += f"This dataset contains all the data, code, and analysis scripts needed "
        description += f"to reproduce the results presented in the manuscript. It includes:\n\n"
        description += f"• Source code and analysis scripts\n"
        description += f"• Raw and processed data files\n"
        description += f"• Configuration files and parameters\n"
        description += f"• Documentation and README files\n"
        description += f"• Figures and visualization outputs\n\n"
        description += f"The materials are organized to support computational reproducibility "
        description += f"and enable other researchers to verify and build upon the findings."
        
        return description
    
    def _generate_arxiv_dataset_description(self, arxiv_submission: ArxivSubmission) -> str:
        """Generate a description for the arXiv dataset"""
        
        description = f"Materials associated with arXiv submission:\n\n"
        description += f"Title: {arxiv_submission.title}\n"
        description += f"arXiv ID: {arxiv_submission.arxiv_id or 'Pending'}\n"
        description += f"Authors: {arxiv_submission.authors}\n"
        description += f"Primary Category: {arxiv_submission.primary_category.code}\n"
        
        if arxiv_submission.secondary_categories.exists():
            secondary = [cat.code for cat in arxiv_submission.secondary_categories.all()]
            description += f"Secondary Categories: {', '.join(secondary)}\n"
        
        description += f"\nAbstract:\n{arxiv_submission.abstract}\n\n"
        description += f"This dataset contains the submission materials for this arXiv preprint, "
        description += f"including LaTeX source files, PDF, and any supplementary materials."
        
        if arxiv_submission.comments:
            description += f"\n\nComments: {arxiv_submission.comments}"
        
        return description
    
    def _generate_keywords(self) -> str:
        """Generate keywords for the dataset"""
        
        keywords = []
        
        if self.manuscript.keywords:
            keywords.extend([k.strip() for k in self.manuscript.keywords.split(',') if k.strip()])
        
        # Add manuscript-specific keywords
        keywords.extend(['manuscript', 'research data', 'supplementary materials'])
        
        if self.manuscript.target_journal:
            keywords.append(self.manuscript.target_journal.lower().replace(' ', '_'))
        
        return ', '.join(keywords[:10])  # Limit to 10 keywords
    
    def _add_manuscript_files_to_dataset(self, dataset: Dataset):
        """Add manuscript files to the dataset"""
        
        # Add compiled PDF if available
        if self.manuscript.compiled_pdf:
            try:
                with self.manuscript.compiled_pdf.open('rb') as f:
                    pdf_content = f.read()
                
                pdf_file = DatasetFile.objects.create(
                    dataset=dataset,
                    filename=f"{self.manuscript.slug}.pdf",
                    file_path="manuscript/",
                    file_type='documentation',
                    file_format='pdf',
                    size_bytes=len(pdf_content),
                    description="Compiled manuscript PDF",
                    local_file=ContentFile(pdf_content, name=f"{self.manuscript.slug}.pdf")
                )
                
            except Exception as e:
                logger.error(f"Failed to add manuscript PDF to dataset: {e}")
        
        # Add LaTeX source if using modular structure
        if self.manuscript.is_modular:
            self._add_modular_manuscript_files(dataset)
        else:
            # Add main content as LaTeX file
            if self.manuscript.content:
                latex_content = self.manuscript.content.encode('utf-8')
                latex_file = DatasetFile.objects.create(
                    dataset=dataset,
                    filename=f"{self.manuscript.slug}.tex",
                    file_path="manuscript/",
                    file_type='documentation',
                    file_format='tex',
                    size_bytes=len(latex_content),
                    description="Manuscript LaTeX source",
                    local_file=ContentFile(latex_content, name=f"{self.manuscript.slug}.tex")
                )
        
        # Add manuscript metadata
        self._add_manuscript_metadata_to_dataset(dataset)
        
        # Update dataset stats
        self._update_dataset_stats(dataset)
    
    def _add_modular_manuscript_files(self, dataset: Dataset):
        """Add modular manuscript files to dataset"""
        
        # This would interact with the manuscript's modular structure
        # For now, we'll add a placeholder implementation
        
        manuscript_info = {
            'title': self.manuscript.title,
            'abstract': self.manuscript.abstract,
            'keywords': self.manuscript.keywords,
            'is_modular': self.manuscript.is_modular,
            'paper_directory': self.manuscript.paper_directory,
            'word_counts': {
                'abstract': self.manuscript.word_count_abstract,
                'introduction': self.manuscript.word_count_introduction,
                'methods': self.manuscript.word_count_methods,
                'results': self.manuscript.word_count_results,
                'discussion': self.manuscript.word_count_discussion,
                'total': self.manuscript.word_count_total,
            },
            'citation_count': self.manuscript.citation_count,
            'created_at': self.manuscript.created_at.isoformat(),
            'updated_at': self.manuscript.updated_at.isoformat(),
        }
        
        info_content = json.dumps(manuscript_info, indent=2).encode('utf-8')
        info_file = DatasetFile.objects.create(
            dataset=dataset,
            filename="manuscript_info.json",
            file_path="metadata/",
            file_type='metadata',
            file_format='json',
            size_bytes=len(info_content),
            description="Manuscript structure and metadata",
            local_file=ContentFile(info_content, name="manuscript_info.json")
        )
    
    def _add_replication_materials_to_dataset(self, dataset: Dataset, 
                                            code_outputs: List = None, 
                                            analysis_data: List = None):
        """Add replication materials to dataset"""
        
        # Add linked code execution outputs
        if self.manuscript.project:
            from apps.code_app.models import CodeExecutionJob
            
            # Get code jobs from the project
            code_jobs = CodeExecutionJob.objects.filter(
                user=self.manuscript.owner,
                status='completed'
            )
            
            for job in code_jobs[:5]:  # Limit to recent jobs
                # Add job metadata
                job_info = {
                    'job_id': str(job.job_id),
                    'execution_type': job.execution_type,
                    'execution_time': job.execution_time,
                    'cpu_time': job.cpu_time,
                    'memory_peak': job.memory_peak,
                    'created_at': job.created_at.isoformat(),
                    'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                    'output_files': job.output_files,
                    'plot_files': job.plot_files,
                }
                
                job_content = json.dumps(job_info, indent=2).encode('utf-8')
                job_file = DatasetFile.objects.create(
                    dataset=dataset,
                    filename=f"code_job_{job.job_id}.json",
                    file_path="replication/code_outputs/",
                    file_type='metadata',
                    file_format='json',
                    size_bytes=len(job_content),
                    description=f"Code execution job metadata for {job.job_id}",
                    local_file=ContentFile(job_content, name=f"code_job_{job.job_id}.json")
                )
        
        # Add manuscript metadata for replication
        self._add_manuscript_metadata_to_dataset(dataset)
        
        # Create replication README
        readme_content = self._generate_replication_readme()
        readme_file_content = readme_content.encode('utf-8')
        readme_file = DatasetFile.objects.create(
            dataset=dataset,
            filename="README.md",
            file_path="",
            file_type='readme',
            file_format='md',
            size_bytes=len(readme_file_content),
            description="Replication instructions and documentation",
            local_file=ContentFile(readme_file_content, name="README.md")
        )
        
        # Update dataset stats
        self._update_dataset_stats(dataset)
    
    def _add_arxiv_files_to_dataset(self, dataset: Dataset, arxiv_submission: ArxivSubmission):
        """Add arXiv submission files to dataset"""
        
        # Add LaTeX source if available
        if arxiv_submission.latex_source:
            try:
                with arxiv_submission.latex_source.open('rb') as f:
                    latex_content = f.read()
                
                latex_file = DatasetFile.objects.create(
                    dataset=dataset,
                    filename=f"arxiv_source_{arxiv_submission.submission_id}.zip",
                    file_path="arxiv/",
                    file_type='code',
                    file_format='zip',
                    size_bytes=len(latex_content),
                    description="arXiv LaTeX source files",
                    local_file=ContentFile(latex_content, name=f"arxiv_source_{arxiv_submission.submission_id}.zip")
                )
                
            except Exception as e:
                logger.error(f"Failed to add arXiv LaTeX source to dataset: {e}")
        
        # Add PDF if available
        if arxiv_submission.pdf_file:
            try:
                with arxiv_submission.pdf_file.open('rb') as f:
                    pdf_content = f.read()
                
                pdf_file = DatasetFile.objects.create(
                    dataset=dataset,
                    filename=f"arxiv_manuscript_{arxiv_submission.submission_id}.pdf",
                    file_path="arxiv/",
                    file_type='documentation',
                    file_format='pdf',
                    size_bytes=len(pdf_content),
                    description="arXiv submission PDF",
                    local_file=ContentFile(pdf_content, name=f"arxiv_manuscript_{arxiv_submission.submission_id}.pdf")
                )
                
            except Exception as e:
                logger.error(f"Failed to add arXiv PDF to dataset: {e}")
        
        # Add arXiv metadata
        arxiv_metadata = {
            'submission_id': str(arxiv_submission.submission_id),
            'arxiv_id': arxiv_submission.arxiv_id,
            'title': arxiv_submission.title,
            'authors': arxiv_submission.authors,
            'abstract': arxiv_submission.abstract,
            'primary_category': arxiv_submission.primary_category.code,
            'secondary_categories': [cat.code for cat in arxiv_submission.secondary_categories.all()],
            'comments': arxiv_submission.comments,
            'journal_reference': arxiv_submission.journal_reference,
            'doi': arxiv_submission.doi,
            'submission_type': arxiv_submission.submission_type,
            'status': arxiv_submission.status,
            'version': arxiv_submission.version,
            'submitted_at': arxiv_submission.submitted_at.isoformat() if arxiv_submission.submitted_at else None,
            'published_at': arxiv_submission.published_at.isoformat() if arxiv_submission.published_at else None,
        }
        
        metadata_content = json.dumps(arxiv_metadata, indent=2).encode('utf-8')
        metadata_file = DatasetFile.objects.create(
            dataset=dataset,
            filename="arxiv_metadata.json",
            file_path="metadata/",
            file_type='metadata',
            file_format='json',
            size_bytes=len(metadata_content),
            description="arXiv submission metadata",
            local_file=ContentFile(metadata_content, name="arxiv_metadata.json")
        )
        
        # Update dataset stats
        self._update_dataset_stats(dataset)
    
    def _add_manuscript_metadata_to_dataset(self, dataset: Dataset):
        """Add manuscript metadata to dataset"""
        
        metadata = {
            'manuscript_id': str(self.manuscript.id),
            'title': self.manuscript.title,
            'slug': self.manuscript.slug,
            'abstract': self.manuscript.abstract,
            'keywords': self.manuscript.keywords,
            'owner': self.manuscript.owner.get_full_name() or self.manuscript.owner.username,
            'collaborators': [
                c.get_full_name() or c.username 
                for c in self.manuscript.collaborators.all()
            ],
            'status': self.manuscript.status,
            'target_journal': self.manuscript.target_journal,
            'submission_deadline': self.manuscript.submission_deadline.isoformat() if self.manuscript.submission_deadline else None,
            'version': self.manuscript.version,
            'is_public': self.manuscript.is_public,
            'word_counts': {
                'abstract': self.manuscript.word_count_abstract,
                'introduction': self.manuscript.word_count_introduction,
                'methods': self.manuscript.word_count_methods,
                'results': self.manuscript.word_count_results,
                'discussion': self.manuscript.word_count_discussion,
                'total': self.manuscript.word_count_total,
            },
            'citation_count': self.manuscript.citation_count,
            'created_at': self.manuscript.created_at.isoformat(),
            'updated_at': self.manuscript.updated_at.isoformat(),
            'last_compiled': self.manuscript.last_compiled.isoformat() if self.manuscript.last_compiled else None,
        }
        
        metadata_content = json.dumps(metadata, indent=2).encode('utf-8')
        metadata_file = DatasetFile.objects.create(
            dataset=dataset,
            filename="manuscript_metadata.json",
            file_path="metadata/",
            file_type='metadata',
            file_format='json',
            size_bytes=len(metadata_content),
            description="Manuscript metadata and information",
            local_file=ContentFile(metadata_content, name="manuscript_metadata.json")
        )
    
    def _generate_replication_readme(self) -> str:
        """Generate README for replication dataset"""
        
        readme = f"# Replication Materials\n\n"
        readme += f"## Manuscript Information\n\n"
        readme += f"**Title:** {self.manuscript.title}\n"
        readme += f"**Authors:** {self.manuscript.owner.get_full_name() or self.manuscript.owner.username}"
        
        collaborators = self.manuscript.collaborators.all()
        if collaborators:
            collab_names = [c.get_full_name() or c.username for c in collaborators]
            readme += f", {', '.join(collab_names)}"
        
        readme += f"\n**Status:** {self.manuscript.get_status_display()}\n"
        
        if self.manuscript.target_journal:
            readme += f"**Target Journal:** {self.manuscript.target_journal}\n"
        
        readme += f"\n## Abstract\n\n{self.manuscript.abstract}\n\n"
        
        readme += f"## Repository Contents\n\n"
        readme += f"This repository contains all materials needed to reproduce the results presented in the manuscript:\n\n"
        readme += f"### Directory Structure\n\n"
        readme += f"```\n"
        readme += f"├── manuscript/          # Manuscript files (PDF, LaTeX)\n"
        readme += f"├── replication/         # Replication materials\n"
        readme += f"│   ├── code_outputs/    # Code execution metadata\n"
        readme += f"│   └── analysis/        # Analysis results\n"
        readme += f"├── metadata/            # Dataset and manuscript metadata\n"
        readme += f"└── README.md           # This file\n"
        readme += f"```\n\n"
        
        readme += f"### Requirements\n\n"
        readme += f"To reproduce the results, you will need:\n\n"
        readme += f"- Python 3.8 or higher\n"
        readme += f"- Required packages (see requirements files in code directories)\n"
        readme += f"- LaTeX distribution for document compilation\n\n"
        
        readme += f"### Usage\n\n"
        readme += f"1. Download all files from this repository\n"
        readme += f"2. Install required dependencies\n"
        readme += f"3. Run analysis scripts in the order specified\n"
        readme += f"4. Compare outputs with published results\n\n"
        
        readme += f"### Citation\n\n"
        readme += f"If you use these materials, please cite the original manuscript:\n\n"
        readme += f"```\n"
        readme += f"[Citation will be added upon publication]\n"
        readme += f"```\n\n"
        
        readme += f"### Contact\n\n"
        readme += f"For questions about these replication materials, please contact:\n"
        readme += f"{self.manuscript.owner.get_full_name() or self.manuscript.owner.username}\n"
        
        if hasattr(self.manuscript.owner, 'email'):
            readme += f"Email: {self.manuscript.owner.email}\n"
        
        readme += f"\n### License\n\n"
        readme += f"These materials are made available under the Creative Commons Attribution 4.0 License (CC-BY-4.0).\n"
        
        return readme
    
    def _update_dataset_stats(self, dataset: Dataset):
        """Update dataset file count and total size"""
        
        files = dataset.files.all()
        dataset.file_count = files.count()
        dataset.total_size_bytes = sum(f.size_bytes for f in files)
        
        # Update file formats list
        formats = list(set(f.file_format for f in files if f.file_format))
        dataset.file_formats = formats
        
        dataset.save()


# Utility functions for manuscript-repository integration
def auto_create_supplementary_dataset(manuscript: Manuscript) -> Optional[Dataset]:
    """Automatically create a supplementary dataset when manuscript is submitted"""
    
    # Check if user has auto-sync enabled
    default_connection = RepositoryConnection.objects.filter(
        user=manuscript.owner,
        is_default=True,
        auto_sync_enabled=True,
        status='active'
    ).first()
    
    if not default_connection:
        logger.info(f"No auto-sync repository connection for user {manuscript.owner.username}")
        return None
    
    try:
        integrator = ManuscriptRepositoryIntegrator(manuscript, default_connection)
        dataset = integrator.create_supplementary_dataset(auto_upload=False)  # Don't auto-upload, let user review first
        
        if dataset:
            logger.info(f"Auto-created supplementary dataset {dataset.id} for manuscript {manuscript.slug}")
        
        return dataset
        
    except Exception as e:
        logger.error(f"Failed to auto-create supplementary dataset: {e}")
        return None