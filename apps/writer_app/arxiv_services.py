"""
arXiv Integration Services for SciTeX Writer

This module provides services for integrating with arXiv submission system,
including account verification, manuscript formatting, and submission workflow.
"""

import os
import shutil
import tempfile
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from django.utils.text import slugify

from .models import (
    ArxivAccount, ArxivApiResponse, ArxivCategory, ArxivSubmission,
    ArxivSubmissionHistory, ArxivValidationResult, Manuscript
)


class ArxivAPIException(Exception):
    """Custom exception for arXiv API errors."""
    pass


class ArxivAccountService:
    """Service for managing arXiv account verification and authentication."""
    
    def __init__(self):
        self.base_url = getattr(settings, 'ARXIV_API_BASE_URL', 'https://arxiv.org/api')
        self.submission_url = getattr(settings, 'ARXIV_SUBMISSION_URL', 'https://arxiv.org/submit')
    
    def verify_account(self, arxiv_account: ArxivAccount) -> bool:
        """
        Verify arXiv account credentials by attempting authentication.
        
        Args:
            arxiv_account: ArxivAccount instance to verify
            
        Returns:
            bool: True if verification successful, False otherwise
        """
        try:
            # In a real implementation, this would use arXiv's authentication API
            # For now, we'll simulate the verification process
            
            # Create verification token
            verification_token = self._generate_verification_token(arxiv_account)
            
            # Update account with verification status
            arxiv_account.verification_token = verification_token
            arxiv_account.is_verified = True
            arxiv_account.verified_at = timezone.now()
            arxiv_account.save()
            
            return True
            
        except Exception as e:
            # Log the error and return False
            print(f"Account verification failed: {str(e)}")
            return False
    
    def _generate_verification_token(self, arxiv_account: ArxivAccount) -> str:
        """Generate a verification token for the account."""
        import hashlib
        import uuid
        
        data = f"{arxiv_account.arxiv_username}{arxiv_account.arxiv_email}{uuid.uuid4()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def check_submission_limits(self, arxiv_account: ArxivAccount) -> Dict[str, Union[bool, int]]:
        """
        Check if user can submit based on daily limits and account status.
        
        Args:
            arxiv_account: ArxivAccount to check
            
        Returns:
            Dict with limit information
        """
        return {
            'can_submit': arxiv_account.can_submit_today() and arxiv_account.is_active,
            'submissions_today': arxiv_account.submissions_today,
            'daily_limit': arxiv_account.daily_submission_limit,
            'remaining': max(0, arxiv_account.daily_submission_limit - arxiv_account.submissions_today),
            'is_suspended': arxiv_account.suspended_until and arxiv_account.suspended_until > timezone.now(),
            'suspension_reason': arxiv_account.suspension_reason if arxiv_account.suspended_until else None
        }


class ArxivCategoryService:
    """Service for managing arXiv categories and subject classification."""
    
    def __init__(self):
        self.categories_url = "https://arxiv.org/category_taxonomy"
    
    def populate_categories(self) -> int:
        """
        Populate the database with current arXiv categories.
        
        Returns:
            int: Number of categories created/updated
        """
        # This would fetch from arXiv's category API in a real implementation
        # For now, we'll create some common categories
        categories_data = [
            # Computer Science
            {'code': 'cs.AI', 'name': 'Artificial Intelligence', 'description': 'Covers all areas of AI'},
            {'code': 'cs.CL', 'name': 'Computation and Language', 'description': 'Natural language processing, computational linguistics'},
            {'code': 'cs.CV', 'name': 'Computer Vision and Pattern Recognition', 'description': 'Image processing, computer vision'},
            {'code': 'cs.LG', 'name': 'Machine Learning', 'description': 'Machine learning research'},
            {'code': 'cs.NI', 'name': 'Networking and Internet Architecture', 'description': 'Network protocols, internet architecture'},
            {'code': 'cs.SE', 'name': 'Software Engineering', 'description': 'Software development, engineering practices'},
            
            # Mathematics
            {'code': 'math.ST', 'name': 'Statistics Theory', 'description': 'Mathematical statistics'},
            {'code': 'math.PR', 'name': 'Probability', 'description': 'Probability theory'},
            {'code': 'math.NA', 'name': 'Numerical Analysis', 'description': 'Numerical methods and analysis'},
            
            # Physics
            {'code': 'physics.comp-ph', 'name': 'Computational Physics', 'description': 'Computational methods in physics'},
            {'code': 'physics.data-an', 'name': 'Data Analysis, Statistics and Probability', 'description': 'Data analysis in physics'},
            
            # Quantitative Biology
            {'code': 'q-bio.BM', 'name': 'Biomolecules', 'description': 'Molecular biology, biochemistry'},
            {'code': 'q-bio.GN', 'name': 'Genomics', 'description': 'Genomics and bioinformatics'},
            
            # Statistics
            {'code': 'stat.AP', 'name': 'Applications', 'description': 'Applied statistics'},
            {'code': 'stat.ML', 'name': 'Machine Learning', 'description': 'Statistical machine learning'},
        ]
        
        created_count = 0
        for cat_data in categories_data:
            category, created = ArxivCategory.objects.get_or_create(
                code=cat_data['code'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description']
                }
            )
            if created:
                created_count += 1
        
        return created_count
    
    def get_categories_by_field(self, field: str) -> List[ArxivCategory]:
        """
        Get categories by field (e.g., 'cs', 'math', 'physics').
        
        Args:
            field: Field prefix (e.g., 'cs', 'math')
            
        Returns:
            List of ArxivCategory objects
        """
        return ArxivCategory.objects.filter(
            code__startswith=f"{field}.",
            is_active=True
        ).order_by('code')
    
    def suggest_categories(self, manuscript: Manuscript, max_suggestions: int = 5) -> List[ArxivCategory]:
        """
        Suggest categories based on manuscript content.
        
        Args:
            manuscript: Manuscript to analyze
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List of suggested ArxivCategory objects
        """
        # Simple keyword-based suggestion system
        content = f"{manuscript.title} {manuscript.abstract}".lower()
        
        category_keywords = {
            'cs.AI': ['artificial intelligence', 'ai', 'machine learning', 'deep learning', 'neural network'],
            'cs.CL': ['natural language', 'nlp', 'language model', 'text processing', 'linguistics'],
            'cs.CV': ['computer vision', 'image processing', 'object detection', 'recognition'],
            'cs.LG': ['machine learning', 'learning algorithm', 'classification', 'regression'],
            'stat.ML': ['statistical learning', 'bayesian', 'statistics', 'probabilistic'],
            'math.ST': ['statistics', 'statistical theory', 'hypothesis testing'],
            'q-bio.GN': ['genomics', 'bioinformatics', 'dna', 'rna', 'genome'],
        }
        
        suggestions = []
        for code, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content)
            if score > 0:
                try:
                    category = ArxivCategory.objects.get(code=code)
                    suggestions.append((category, score))
                except ArxivCategory.DoesNotExist:
                    continue
        
        # Sort by score and return top suggestions
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [cat for cat, score in suggestions[:max_suggestions]]


class ArxivValidationService:
    """Service for validating manuscripts before arXiv submission."""
    
    def __init__(self):
        self.max_file_size_mb = 50  # arXiv's file size limit
        self.max_title_length = 256
        self.max_abstract_length = 1920
    
    def validate_submission(self, submission: ArxivSubmission) -> ArxivValidationResult:
        """
        Comprehensive validation of arXiv submission.
        
        Args:
            submission: ArxivSubmission to validate
            
        Returns:
            ArxivValidationResult object
        """
        # Create or get validation result
        validation, created = ArxivValidationResult.objects.get_or_create(
            submission=submission,
            defaults={'status': 'pending'}
        )
        
        validation.validation_started = timezone.now()
        validation.save()
        
        # Run validation checks
        self._validate_metadata(validation, submission)
        self._validate_latex_compilation(validation, submission)
        self._validate_pdf_generation(validation, submission)
        self._validate_file_formats(validation, submission)
        self._validate_categories(validation, submission)
        
        # Calculate overall score and status
        self._calculate_overall_validation(validation)
        
        validation.validation_completed = timezone.now()
        validation.save()
        
        return validation
    
    def _validate_metadata(self, validation: ArxivValidationResult, submission: ArxivSubmission):
        """Validate submission metadata (title, abstract, authors)."""
        errors = []
        warnings = []
        
        # Title validation
        if len(submission.title) > self.max_title_length:
            errors.append(f"Title exceeds maximum length of {self.max_title_length} characters")
            validation.title_length_check = False
        else:
            validation.title_length_check = True
        
        # Abstract validation
        if len(submission.abstract) > self.max_abstract_length:
            errors.append(f"Abstract exceeds maximum length of {self.max_abstract_length} characters")
            validation.abstract_length_check = False
        else:
            validation.abstract_length_check = True
        
        # Author format validation
        if not submission.authors.strip():
            errors.append("Authors field is required")
            validation.author_format_check = False
        else:
            validation.author_format_check = True
        
        # Set validation status
        if errors:
            validation.metadata_validation = 'failed'
            validation.error_messages.extend(errors)
        elif warnings:
            validation.metadata_validation = 'warning'
            validation.warning_messages.extend(warnings)
        else:
            validation.metadata_validation = 'passed'
        
        validation.save()
    
    def _validate_latex_compilation(self, validation: ArxivValidationResult, submission: ArxivSubmission):
        """Validate LaTeX compilation."""
        if not submission.latex_source:
            validation.latex_compilation = 'failed'
            validation.error_messages.append("LaTeX source file is required")
            validation.save()
            return
        
        try:
            # In a real implementation, this would compile the LaTeX
            # For now, we'll simulate successful compilation
            validation.latex_compilation = 'passed'
            validation.latex_log = "LaTeX compilation successful"
        except Exception as e:
            validation.latex_compilation = 'failed'
            validation.error_messages.append(f"LaTeX compilation failed: {str(e)}")
        
        validation.save()
    
    def _validate_pdf_generation(self, validation: ArxivValidationResult, submission: ArxivSubmission):
        """Validate PDF generation."""
        if not submission.pdf_file:
            validation.pdf_generation = 'failed'
            validation.error_messages.append("PDF file is required")
        else:
            validation.pdf_generation = 'passed'
        
        validation.save()
    
    def _validate_file_formats(self, validation: ArxivValidationResult, submission: ArxivSubmission):
        """Validate file formats and sizes."""
        total_size = 0
        unsupported_files = []
        
        # Check main files
        if submission.latex_source:
            total_size += submission.latex_source.size / (1024 * 1024)  # Convert to MB
        
        if submission.pdf_file:
            total_size += submission.pdf_file.size / (1024 * 1024)
        
        validation.total_file_size = total_size
        validation.max_file_size_exceeded = total_size > self.max_file_size_mb
        validation.unsupported_files = unsupported_files
        
        if validation.max_file_size_exceeded:
            validation.file_format_check = 'failed'
            validation.error_messages.append(f"Total file size ({total_size:.1f}MB) exceeds limit of {self.max_file_size_mb}MB")
        else:
            validation.file_format_check = 'passed'
        
        validation.save()
    
    def _validate_categories(self, validation: ArxivValidationResult, submission: ArxivSubmission):
        """Validate category selection."""
        if not submission.primary_category:
            validation.category_validation = 'failed'
            validation.error_messages.append("Primary category is required")
        else:
            validation.category_validation = 'passed'
        
        validation.save()
    
    def _calculate_overall_validation(self, validation: ArxivValidationResult):
        """Calculate overall validation score and status."""
        checks = [
            validation.latex_compilation,
            validation.pdf_generation,
            validation.metadata_validation,
            validation.category_validation,
            validation.file_format_check,
        ]
        
        passed_count = sum(1 for check in checks if check == 'passed')
        failed_count = sum(1 for check in checks if check == 'failed')
        warning_count = sum(1 for check in checks if check == 'warning')
        
        # Calculate score (0-100)
        validation.overall_score = (passed_count / len(checks)) * 100
        
        # Determine overall status
        if failed_count > 0:
            validation.status = 'failed'
        elif warning_count > 0:
            validation.status = 'warning'
        else:
            validation.status = 'passed'
        
        validation.save()


class ArxivFormattingService:
    """Service for formatting manuscripts for arXiv submission."""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / 'arxiv_formatting'
        self.temp_dir.mkdir(exist_ok=True)
    
    def format_manuscript_for_arxiv(self, manuscript: Manuscript) -> Tuple[Path, Path]:
        """
        Format manuscript for arXiv submission.
        
        Args:
            manuscript: Manuscript to format
            
        Returns:
            Tuple of (latex_file_path, pdf_file_path)
        """
        # Create temporary working directory
        work_dir = self.temp_dir / f"manuscript_{manuscript.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
        work_dir.mkdir(exist_ok=True)
        
        try:
            # Generate arXiv-compatible LaTeX
            latex_content = self._generate_arxiv_latex(manuscript)
            latex_file = work_dir / "main.tex"
            
            with open(latex_file, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            # Copy figures and other assets
            self._copy_manuscript_assets(manuscript, work_dir)
            
            # Generate bibliography if needed
            bib_file = self._generate_bibliography(manuscript, work_dir)
            
            # Compile to PDF
            pdf_file = self._compile_latex_to_pdf(latex_file, work_dir)
            
            return latex_file, pdf_file
            
        except Exception as e:
            # Clean up on error
            shutil.rmtree(work_dir, ignore_errors=True)
            raise ArxivAPIException(f"Failed to format manuscript: {str(e)}")
    
    def _generate_arxiv_latex(self, manuscript: Manuscript) -> str:
        """Generate arXiv-compatible LaTeX content."""
        # Basic arXiv template
        latex_template = r"""\documentclass[12pt]{{article}}

% arXiv recommended packages
\usepackage[utf8]{{inputenc}}
\usepackage[english]{{babel}}
\usepackage{{amsmath}}
\usepackage{{amsfonts}}
\usepackage{{amssymb}}
\usepackage{{graphicx}}
\usepackage{{cite}}
\usepackage{{url}}
\usepackage[margin=1in]{{geometry}}

% Metadata
\title{{{title}}}
\author{{{authors}}}
\date{{\today}}

\begin{{document}}

\maketitle

\begin{{abstract}}
{abstract}
\end{{abstract}}

% Keywords
\textbf{{Keywords:}} {keywords}

{content}

% Bibliography
\bibliographystyle{{plain}}
\bibliography{{references}}

\end{{document}}
"""
        
        # Prepare content
        if manuscript.is_modular:
            content = self._compile_modular_content(manuscript)
        else:
            content = manuscript.content
        
        # Format authors
        authors = self._format_authors(manuscript)
        
        # Generate LaTeX
        return latex_template.format(
            title=manuscript.title,
            authors=authors,
            abstract=manuscript.abstract or "Abstract content here.",
            keywords=manuscript.keywords or "keyword1, keyword2, keyword3",
            content=content
        )
    
    def _compile_modular_content(self, manuscript: Manuscript) -> str:
        """Compile content from modular manuscript sections."""
        content = ""
        
        # Get paper path
        paper_path = manuscript.get_project_paper_path()
        if not paper_path:
            return "% Content could not be loaded"
        
        # Section files mapping
        section_files = [
            ('manuscript/src/introduction.tex', 'Introduction'),
            ('manuscript/src/methods.tex', 'Methods'),
            ('manuscript/src/results.tex', 'Results'),
            ('manuscript/src/discussion.tex', 'Discussion'),
            ('manuscript/src/conclusion.tex', 'Conclusion'),
        ]
        
        for file_path, section_name in section_files:
            full_path = paper_path / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        section_content = f.read()
                        # Remove section commands if they exist
                        if not section_content.strip().startswith('\\section'):
                            content += f"\\section{{{section_name}}}\n"
                        content += section_content + "\n\n"
                except Exception:
                    content += f"% Error loading {section_name} section\n\n"
        
        return content
    
    def _format_authors(self, manuscript: Manuscript) -> str:
        """Format author list for arXiv."""
        authors = [manuscript.owner.get_full_name() or manuscript.owner.username]
        
        if manuscript.collaborators.exists():
            collaborator_names = [
                c.get_full_name() or c.username 
                for c in manuscript.collaborators.all()
            ]
            authors.extend(collaborator_names)
        
        return " \\and ".join(authors)
    
    def _copy_manuscript_assets(self, manuscript: Manuscript, work_dir: Path):
        """Copy figures and other assets to working directory."""
        if not manuscript.is_modular:
            return
        
        paper_path = manuscript.get_project_paper_path()
        if not paper_path:
            return
        
        # Copy figures
        figures_src = paper_path / 'manuscript' / 'src' / 'figures'
        if figures_src.exists():
            figures_dst = work_dir / 'figures'
            figures_dst.mkdir(exist_ok=True)
            
            for figure_file in figures_src.glob('*'):
                if figure_file.is_file():
                    shutil.copy2(figure_file, figures_dst)
    
    def _generate_bibliography(self, manuscript: Manuscript, work_dir: Path) -> Optional[Path]:
        """Generate bibliography file from manuscript citations."""
        bib_file = work_dir / "references.bib"
        
        # Get citations from manuscript
        citations = manuscript.citations.all()
        if not citations:
            # Try to copy from modular structure
            if manuscript.is_modular:
                paper_path = manuscript.get_project_paper_path()
                if paper_path:
                    ref_file = paper_path / 'references' / 'references.bib'
                    if ref_file.exists():
                        shutil.copy2(ref_file, bib_file)
                        return bib_file
            return None
        
        # Generate BibTeX content
        bib_content = "% Bibliography for arXiv submission\n\n"
        for citation in citations:
            bib_content += citation.bibtex_entry + "\n\n"
        
        with open(bib_file, 'w', encoding='utf-8') as f:
            f.write(bib_content)
        
        return bib_file
    
    def _compile_latex_to_pdf(self, latex_file: Path, work_dir: Path) -> Path:
        """Compile LaTeX to PDF."""
        import subprocess
        
        pdf_file = work_dir / "main.pdf"
        
        try:
            # Change to working directory
            original_cwd = os.getcwd()
            os.chdir(work_dir)
            
            # Run pdflatex
            subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', latex_file.name],
                check=True,
                capture_output=True
            )
            
            # Run bibtex if bibliography exists
            if (work_dir / "references.bib").exists():
                subprocess.run(
                    ['bibtex', latex_file.stem],
                    check=False,  # Don't fail if no citations
                    capture_output=True
                )
                
                # Run pdflatex twice more for references
                subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', latex_file.name],
                    check=True,
                    capture_output=True
                )
                subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', latex_file.name],
                    check=True,
                    capture_output=True
                )
            
            return pdf_file
            
        except subprocess.CalledProcessError as e:
            raise ArxivAPIException(f"LaTeX compilation failed: {e}")
        except FileNotFoundError:
            raise ArxivAPIException("pdflatex not found. Please install LaTeX.")
        finally:
            os.chdir(original_cwd)


class ArxivSubmissionService:
    """Service for managing arXiv submissions and status tracking."""
    
    def __init__(self):
        self.account_service = ArxivAccountService()
        self.validation_service = ArxivValidationService()
        self.formatting_service = ArxivFormattingService()
    
    def create_submission(self, manuscript: Manuscript, user, submission_data: Dict) -> ArxivSubmission:
        """
        Create a new arXiv submission.
        
        Args:
            manuscript: Manuscript to submit
            user: User creating the submission
            submission_data: Submission metadata
            
        Returns:
            ArxivSubmission object
        """
        # Get or verify arXiv account
        try:
            arxiv_account = user.arxiv_account
            if not arxiv_account.is_verified:
                raise ArxivAPIException("arXiv account not verified")
        except ArxivAccount.DoesNotExist:
            raise ArxivAPIException("No arXiv account configured")
        
        # Check submission limits
        limits = self.account_service.check_submission_limits(arxiv_account)
        if not limits['can_submit']:
            raise ArxivAPIException("Daily submission limit exceeded or account suspended")
        
        # Create submission
        submission = ArxivSubmission.objects.create(
            manuscript=manuscript,
            user=user,
            arxiv_account=arxiv_account,
            title=submission_data.get('title', manuscript.title),
            abstract=submission_data.get('abstract', manuscript.abstract),
            authors=submission_data.get('authors', ''),
            primary_category_id=submission_data['primary_category_id'],
            comments=submission_data.get('comments', ''),
            journal_reference=submission_data.get('journal_reference', ''),
            doi=submission_data.get('doi', ''),
        )
        
        # Add secondary categories
        if 'secondary_categories' in submission_data:
            submission.secondary_categories.set(submission_data['secondary_categories'])
        
        # Create history entry
        ArxivSubmissionHistory.objects.create(
            submission=submission,
            new_status='draft',
            change_reason='Submission created',
            changed_by=user,
            is_automatic=False
        )
        
        return submission
    
    def validate_submission(self, submission: ArxivSubmission) -> ArxivValidationResult:
        """Validate submission for arXiv requirements."""
        return self.validation_service.validate_submission(submission)
    
    def prepare_submission_files(self, submission: ArxivSubmission) -> Tuple[str, str]:
        """
        Prepare LaTeX and PDF files for submission.
        
        Args:
            submission: ArxivSubmission to prepare
            
        Returns:
            Tuple of (latex_file_path, pdf_file_path) in storage
        """
        # Format manuscript
        latex_file, pdf_file = self.formatting_service.format_manuscript_for_arxiv(
            submission.manuscript
        )
        
        # Save files to storage
        latex_name = f"arxiv_{submission.submission_id}_latex.tex"
        pdf_name = f"arxiv_{submission.submission_id}.pdf"
        
        with open(latex_file, 'rb') as f:
            latex_content = ContentFile(f.read(), name=latex_name)
            submission.latex_source = latex_content
        
        with open(pdf_file, 'rb') as f:
            pdf_content = ContentFile(f.read(), name=pdf_name)
            submission.pdf_file = pdf_content
        
        submission.save()
        
        # Clean up temporary files
        shutil.rmtree(latex_file.parent, ignore_errors=True)
        
        return submission.latex_source.path, submission.pdf_file.path
    
    def submit_to_arxiv(self, submission: ArxivSubmission) -> bool:
        """
        Submit to arXiv (simulated - would use real arXiv API).
        
        Args:
            submission: ArxivSubmission to submit
            
        Returns:
            bool: True if submission successful
        """
        try:
            # Update status
            submission.status = 'submitted'
            submission.submitted_at = timezone.now()
            submission.save()
            
            # Increment daily submission count
            submission.arxiv_account.increment_daily_submissions()
            
            # Create history entry
            ArxivSubmissionHistory.objects.create(
                submission=submission,
                previous_status='draft',
                new_status='submitted',
                change_reason='Submitted to arXiv',
                arxiv_response={'message': 'Submission successful', 'timestamp': timezone.now().isoformat()},
                is_automatic=True
            )
            
            # In a real implementation, this would:
            # 1. Package files according to arXiv requirements
            # 2. Make API call to arXiv submission system
            # 3. Handle response and update submission status
            # 4. Store arXiv-assigned submission ID
            
            # Simulate successful submission
            submission.arxiv_id = f"2312.{str(submission.id).zfill(5)}"
            submission.arxiv_url = f"https://arxiv.org/abs/{submission.arxiv_id}"
            submission.save()
            
            return True
            
        except Exception as e:
            # Update status to indicate failure
            submission.status = 'draft'
            submission.save()
            
            # Create error history entry
            ArxivSubmissionHistory.objects.create(
                submission=submission,
                previous_status='draft',
                new_status='draft',
                change_reason='Submission failed',
                error_details=str(e),
                is_automatic=True
            )
            
            raise ArxivAPIException(f"Submission failed: {str(e)}")
    
    def check_submission_status(self, submission: ArxivSubmission) -> Dict:
        """
        Check submission status from arXiv (simulated).
        
        Args:
            submission: ArxivSubmission to check
            
        Returns:
            Dict with status information
        """
        if not submission.arxiv_id:
            return {'status': submission.status, 'message': 'Not yet submitted to arXiv'}
        
        # In a real implementation, this would query arXiv API
        # For now, simulate status progression
        
        # Simulate status progression based on time elapsed
        time_since_submission = timezone.now() - submission.submitted_at if submission.submitted_at else timedelta(0)
        
        if time_since_submission < timedelta(hours=1):
            new_status = 'submitted'
        elif time_since_submission < timedelta(hours=24):
            new_status = 'under_review'
        elif time_since_submission < timedelta(days=3):
            new_status = 'approved'
        else:
            new_status = 'published'
            if not submission.published_at:
                submission.published_at = timezone.now()
        
        # Update status if changed
        if new_status != submission.status:
            old_status = submission.status
            submission.status = new_status
            submission.last_status_check = timezone.now()
            submission.save()
            
            # Create history entry
            ArxivSubmissionHistory.objects.create(
                submission=submission,
                previous_status=old_status,
                new_status=new_status,
                change_reason='Status updated from arXiv',
                arxiv_response={'status': new_status, 'timestamp': timezone.now().isoformat()},
                is_automatic=True
            )
        
        return {
            'status': submission.status,
            'arxiv_id': submission.arxiv_id,
            'arxiv_url': submission.arxiv_url,
            'message': submission.get_status_display_with_details(),
            'last_checked': submission.last_status_check
        }
    
    def withdraw_submission(self, submission: ArxivSubmission, reason: str) -> bool:
        """
        Withdraw a submission from arXiv.
        
        Args:
            submission: ArxivSubmission to withdraw
            reason: Reason for withdrawal
            
        Returns:
            bool: True if withdrawal successful
        """
        if not submission.can_be_withdrawn():
            raise ArxivAPIException("Submission cannot be withdrawn in current status")
        
        try:
            # Update status
            old_status = submission.status
            submission.status = 'withdrawn'
            submission.save()
            
            # Create history entry
            ArxivSubmissionHistory.objects.create(
                submission=submission,
                previous_status=old_status,
                new_status='withdrawn',
                change_reason=f'Withdrawn by user: {reason}',
                changed_by=submission.user,
                is_automatic=False
            )
            
            return True
            
        except Exception as e:
            raise ArxivAPIException(f"Withdrawal failed: {str(e)}")
    
    def replace_submission(self, original_submission: ArxivSubmission, new_manuscript: Manuscript, replacement_data: Dict) -> ArxivSubmission:
        """
        Create a replacement submission for an existing arXiv paper.
        
        Args:
            original_submission: Original ArxivSubmission to replace
            new_manuscript: New manuscript for replacement
            replacement_data: Replacement metadata
            
        Returns:
            New ArxivSubmission object
        """
        if not original_submission.can_be_replaced():
            raise ArxivAPIException("Original submission cannot be replaced")
        
        # Create replacement submission
        replacement = ArxivSubmission.objects.create(
            manuscript=new_manuscript,
            user=original_submission.user,
            arxiv_account=original_submission.arxiv_account,
            submission_type='replacement',
            replaces_submission=original_submission,
            title=replacement_data.get('title', new_manuscript.title),
            abstract=replacement_data.get('abstract', new_manuscript.abstract),
            authors=replacement_data.get('authors', original_submission.authors),
            primary_category=original_submission.primary_category,
            comments=replacement_data.get('comments', ''),
            journal_reference=replacement_data.get('journal_reference', ''),
            doi=replacement_data.get('doi', ''),
            version=original_submission.version + 1,
        )
        
        # Copy secondary categories
        replacement.secondary_categories.set(original_submission.secondary_categories.all())
        
        # Create history entry
        ArxivSubmissionHistory.objects.create(
            submission=replacement,
            new_status='draft',
            change_reason=f'Replacement created for {original_submission.arxiv_id}',
            changed_by=original_submission.user,
            is_automatic=False
        )
        
        return replacement


class ArxivIntegrationService:
    """Main service class for arXiv integration coordination."""
    
    def __init__(self):
        self.account_service = ArxivAccountService()
        self.category_service = ArxivCategoryService()
        self.submission_service = ArxivSubmissionService()
        self.validation_service = ArxivValidationService()
        self.formatting_service = ArxivFormattingService()
    
    def initialize_arxiv_integration(self):
        """Initialize arXiv integration by populating categories."""
        return self.category_service.populate_categories()
    
    def get_user_submission_status(self, user) -> Dict:
        """Get comprehensive submission status for a user."""
        try:
            arxiv_account = user.arxiv_account
            submissions = user.arxiv_submissions.all()
            
            return {
                'account': {
                    'is_verified': arxiv_account.is_verified,
                    'username': arxiv_account.arxiv_username,
                    'email': arxiv_account.arxiv_email,
                },
                'limits': self.account_service.check_submission_limits(arxiv_account),
                'submissions': {
                    'total': submissions.count(),
                    'draft': submissions.filter(status='draft').count(),
                    'submitted': submissions.filter(status='submitted').count(),
                    'published': submissions.filter(status='published').count(),
                },
                'recent_submissions': submissions[:5]
            }
        except ArxivAccount.DoesNotExist:
            return {
                'account': None,
                'limits': None,
                'submissions': None,
                'recent_submissions': []
            }