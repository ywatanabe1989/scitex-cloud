from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import os
from pathlib import Path


class DocumentTemplate(models.Model):
    """Templates for different journals and document types."""
    TEMPLATE_TYPES = [
        ('article', 'Journal Article'),
        ('conference', 'Conference Paper'),
        ('thesis', 'Thesis/Dissertation'),
        ('report', 'Technical Report'),
        ('book', 'Book/Chapter'),
        ('preprint', 'Preprint'),
        ('custom', 'Custom Template'),
    ]
    
    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    journal_name = models.CharField(max_length=200, blank=True)
    
    # Template files
    latex_template = models.TextField()
    style_file = models.TextField(blank=True)  # .sty content
    bibliography_style = models.CharField(max_length=50, default='plain')
    
    # Metadata
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='doc_templates/', blank=True, null=True)
    is_public = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='doc_templates')
    
    # Usage tracking
    usage_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class Manuscript(models.Model):
    """Main document model for scientific manuscripts."""
    DOCUMENT_STATUS = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('revision', 'In Revision'),
        ('submitted', 'Submitted'),
        ('accepted', 'Accepted'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
    ]
    
    # Basic information
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, unique=True)
    abstract = models.TextField(blank=True)
    keywords = models.CharField(max_length=500, blank=True)
    
    # Project linking
    project = models.ForeignKey(
        'core_app.Project', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='writer_manuscripts'
    )
    
    # Ownership and collaboration
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='manuscripts')
    collaborators = models.ManyToManyField(User, related_name='shared_manuscripts', blank=True)
    
    # Template and content
    template = models.ForeignKey(DocumentTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()  # LaTeX content
    compiled_pdf = models.FileField(upload_to='manuscripts/pdfs/', blank=True, null=True)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=DOCUMENT_STATUS, default='draft')
    target_journal = models.CharField(max_length=200, blank=True)
    submission_deadline = models.DateField(null=True, blank=True)
    
    # Version control
    version = models.IntegerField(default=1)
    is_public = models.BooleanField(default=False)
    
    # AI assistance tracking
    ai_suggestions_count = models.IntegerField(default=0)
    last_ai_assist = models.DateTimeField(null=True, blank=True)
    
    # Modular manuscript structure
    is_modular = models.BooleanField(default=False)
    paper_directory = models.CharField(max_length=500, blank=True)  # Relative path to paper directory
    
    # Word count tracking
    word_count_abstract = models.IntegerField(default=0)
    word_count_introduction = models.IntegerField(default=0)
    word_count_methods = models.IntegerField(default=0)
    word_count_results = models.IntegerField(default=0)
    word_count_discussion = models.IntegerField(default=0)
    word_count_total = models.IntegerField(default=0)
    citation_count = models.IntegerField(default=0)
    unique_citation_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_compiled = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-updated_at']
        permissions = [
            ("can_compile_manuscript", "Can compile manuscript"),
            ("can_share_manuscript", "Can share manuscript"),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return f"/writer/manuscript/{self.slug}/"
    
    def get_project_paper_path(self):
        """Get the paper directory path within the project."""
        if self.project and hasattr(self.project, 'data_location'):
            from apps.core_app.directory_manager import get_user_directory_manager
            manager = get_user_directory_manager(self.owner)
            project_path = manager.get_project_path(self.project)
            return project_path / 'paper' if project_path else None
        return None
    
    def create_modular_structure(self):
        """Create modular LaTeX structure in project/paper/ directory."""
        paper_path = self.get_project_paper_path()
        if not paper_path:
            return False
            
        # Create directory structure following SciTeX-Writer pattern
        directories = [
            'manuscript/src',
            'manuscript/src/figures',
            'manuscript/src/tables', 
            'manuscript/logs',
            'revision/src',
            'revision/logs',
            'references',
            'scripts/python',
            'scripts/shell'
        ]
        
        for dir_path in directories:
            (paper_path / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create main.tex in manuscript/
        main_tex_content = r'''\documentclass[12pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath}
\usepackage{graphicx}
\usepackage[margin=1in]{geometry}
\usepackage{cite}

\title{''' + self.title + r'''}
\author{''' + (self.owner.get_full_name() or self.owner.username) + r'''}
\date{\today}

\begin{document}

\maketitle

\input{src/abstract}
\input{src/introduction}
\input{src/methods}
\input{src/results}
\input{src/discussion}
\input{src/conclusion}

\bibliographystyle{plain}
\bibliography{../references/references}

\end{document}'''
        
        with open(paper_path / 'manuscript' / 'main.tex', 'w') as f:
            f.write(main_tex_content)
        
        # Create section files
        sections = {
            'abstract.tex': '% Abstract\n\\begin{abstract}\nYour abstract here...\n\\end{abstract}\n',
            'introduction.tex': '% Introduction\n\\section{Introduction}\nYour introduction here...\n',
            'methods.tex': '% Methods\n\\section{Methods}\nYour methods here...\n',
            'results.tex': '% Results\n\\section{Results}\nYour results here...\n',
            'discussion.tex': '% Discussion\n\\section{Discussion}\nYour discussion here...\n',
            'conclusion.tex': '% Conclusion\n\\section{Conclusion}\nYour conclusion here...\n'
        }
        
        for filename, content in sections.items():
            with open(paper_path / 'manuscript' / 'src' / filename, 'w') as f:
                f.write(content)
        
        # Create compile.sh script following SciTeX-Writer pattern
        compile_script = '''#!/bin/bash
# LaTeX compilation script for SciTeX Writer
# Based on SciTeX-Writer repository structure

set -e
set -o pipefail

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_DIR="$THIS_DIR/logs"
LOG_FILE="$LOG_DIR/compilation.log"

# Create log directory
mkdir -p "$LOG_DIR"
touch "$LOG_FILE"

echo_info() {
    echo "[INFO] $1" | tee -a "$LOG_FILE"
}

echo_success() {
    echo "[SUCCESS] $1" | tee -a "$LOG_FILE"
}

echo_error() {
    echo "[ERROR] $1" | tee -a "$LOG_FILE"
}

main() {
    echo_info "Starting SciTeX Writer compilation..."
    
    # Navigate to manuscript directory using absolute path
    MANUSCRIPT_DIR="$THIS_DIR/manuscript"
    if [ ! -d "$MANUSCRIPT_DIR" ]; then
        echo_error "Manuscript directory not found: $MANUSCRIPT_DIR"
        return 1
    fi
    cd "$MANUSCRIPT_DIR"
    
    # Clean previous compilation files
    echo_info "Cleaning previous compilation files..."
    rm -f *.aux *.log *.out *.toc *.bbl *.blg *.pdf *.fls *.fdb_latexmk
    
    # Create compiled.tex by gathering all components
    echo_info "Gathering LaTeX components..."
    cp main.tex compiled.tex
    
    # First pass: pdflatex
    echo_info "Running pdflatex (first pass)..."
    pdflatex -interaction=nonstopmode compiled.tex >> "$LOG_FILE" 2>&1 || {
        echo_error "pdflatex first pass failed"
        return 1
    }
    
    # Check if bibliography exists and has citations to process
    if [ -f "../references/references.bib" ] && grep -q "\\\\\\\\citation" compiled.aux 2>/dev/null; then
        echo_info "Processing bibliography..."
        bibtex compiled >> "$LOG_FILE" 2>&1 || {
            echo_error "bibtex failed"
            return 1
        }
    else
        echo_info "No citations found, skipping bibliography processing"
    fi
    
    # Second pass: pdflatex
    echo_info "Running pdflatex (second pass)..."
    pdflatex -interaction=nonstopmode compiled.tex >> "$LOG_FILE" 2>&1 || {
        echo_error "pdflatex second pass failed"
        return 1
    }
    
    # Third pass: pdflatex (to resolve all references)
    echo_info "Running pdflatex (third pass)..."
    pdflatex -interaction=nonstopmode compiled.tex >> "$LOG_FILE" 2>&1 || {
        echo_error "pdflatex third pass failed"
        return 1
    }
    
    # Rename final output
    if [ -f "compiled.pdf" ]; then
        mv compiled.pdf main.pdf
        echo_success "Compilation completed: main.pdf"
        echo_success "Log file: $LOG_FILE"
    else
        echo_error "PDF generation failed"
        return 1
    fi
    
    # Word count
    if command -v texcount >/dev/null 2>&1; then
        echo_info "Counting words..."
        texcount -inc -brief main.tex 2>/dev/null | tee -a "$LOG_FILE" || true
    fi
    
    return 0
}

# Execute main function and log output
main "$@" 2>&1 | tee -a "$LOG_FILE"
exit_code=${PIPESTATUS[0]}

if [ $exit_code -eq 0 ]; then
    echo_success "SciTeX Writer compilation completed successfully"
else
    echo_error "SciTeX Writer compilation failed with exit code $exit_code"
fi

exit $exit_code
'''
        
        compile_path = paper_path / 'compile.sh'
        with open(compile_path, 'w') as f:
            f.write(compile_script)
        
        # Make compile.sh executable
        compile_path.chmod(0o755)
        
        # Create configuration file
        config_content = '''# SciTeX Writer Configuration
# Based on SciTeX-Writer repository

# Paths
BASE_TEX="base.tex"
COMPILED_TEX="compiled.tex"
LOG_DIR="logs"
GLOBAL_LOG_FILE="$LOG_DIR/compilation.log"

# LaTeX settings
LATEX_ENGINE="pdflatex"
BIBTEX_ENGINE="bibtex"

# Output settings
OUTPUT_PDF="main.pdf"
WORD_COUNT_ENABLED=true

echo_info() {
    echo "[INFO] $1"
}

echo_success() {
    echo "[SUCCESS] $1" 
}

echo_warn() {
    echo "[WARN] $1"
}

echo_error() {
    echo "[ERROR] $1"
}
'''
        
        with open(paper_path / 'config.src', 'w') as f:
            f.write(config_content)
            
        # Create empty references.bib with proper structure
        bib_content = '''% Bibliography entries for SciTeX Writer
% Based on SciTeX-Writer repository structure
% Add your citations here following BibTeX format

% Example entry:
% @article{example2023,
%   title={Example Article Title},
%   author={Author, First and Second, Author},
%   journal={Journal Name},
%   volume={1},
%   number={1},
%   pages={1--10},
%   year={2023},
%   publisher={Publisher}
% }
'''
        
        with open(paper_path / 'references' / 'references.bib', 'w') as f:
            f.write(bib_content)
            
        # Create README for the paper directory
        readme_content = f'''# {self.title} - SciTeX Writer

This manuscript directory follows the SciTeX-Writer repository structure for modular scientific writing.

## Directory Structure

```
paper/
├── manuscript/
│   ├── src/               # Editable LaTeX components
│   │   ├── abstract.tex   # Abstract section
│   │   ├── introduction.tex
│   │   ├── methods.tex
│   │   ├── results.tex
│   │   ├── discussion.tex
│   │   ├── conclusion.tex
│   │   ├── figures/       # Figure files and captions
│   │   └── tables/        # Table files and captions
│   ├── main.tex           # Main LaTeX document
│   └── logs/              # Compilation logs
├── revision/
│   ├── src/               # Revision documents
│   └── logs/              # Revision logs
├── references/
│   └── references.bib     # Bibliography entries
├── scripts/               # Utility scripts
│   ├── python/
│   └── shell/
├── compile.sh             # Compilation script
├── config.src             # Configuration file
└── README.md              # This file
```

## Usage

### Text-Based Editing (Recommended)
Use the SciTeX Writer web interface to edit sections using plain text. The system automatically handles LaTeX formatting.

### LaTeX Editing (Advanced)
Edit files directly in `manuscript/src/` for advanced LaTeX control.

### Compilation
```bash
./compile.sh
```

### Word Counting
Word counts are automatically tracked for each section and displayed in the web interface.

### Citations
Add citations to `references/references.bib` and reference them in your text using `\\cite{{citation_key}}`.

## Integration with SciTeX-Writer Repository

This structure is compatible with the SciTeX-Writer repository at:
https://github.com/ywatanabe1989/SciTeX-Writer

For advanced features and local development, you can sync with the external repository.
'''
        
        with open(paper_path / 'README.md', 'w') as f:
            f.write(readme_content)
        
        self.is_modular = True
        self.paper_directory = 'paper'
        self.save()
        
        return True
    
    def update_word_counts(self):
        """Update word counts for each section."""
        if not self.is_modular:
            # Count words in the main content for non-modular manuscripts
            words = len(self.content.split())
            self.word_count_total = words
        else:
            # Count words in each modular section file
            paper_path = self.get_project_paper_path()
            if paper_path:
                section_files = {
                    'word_count_abstract': 'manuscript/src/abstract.tex',
                    'word_count_introduction': 'manuscript/src/introduction.tex',
                    'word_count_methods': 'manuscript/src/methods.tex',
                    'word_count_results': 'manuscript/src/results.tex',
                    'word_count_discussion': 'manuscript/src/discussion.tex'
                }
                
                total_words = 0
                for field_name, file_path in section_files.items():
                    full_path = paper_path / file_path
                    if full_path.exists():
                        with open(full_path, 'r') as f:
                            content = f.read()
                            # Remove LaTeX commands for word counting
                            import re
                            text_only = re.sub(r'\\[a-zA-Z*]+(?:\[[^\]]*\])?(?:\{[^}]*\})?', '', content)
                            text_only = re.sub(r'[{}%]', '', text_only)
                            words = len(text_only.split())
                            setattr(self, field_name, words)
                            total_words += words
                
                self.word_count_total = total_words
        
        self.save()
        return self.word_count_total
    
    def generate_latex(self):
        """Generate LaTeX content for the manuscript."""
        # Start with template if available
        if self.template:
            latex = self.template.latex_template
        else:
            # Basic default template
            latex = r"""\documentclass[12pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{hyperref}
\usepackage[margin=1in]{geometry}

\title{{{title}}}
\author{{{authors}}}
\date{{\today}}

\begin{{document}}

\maketitle

"""
        
        # Add abstract if exists
        if self.abstract:
            latex += r"\begin{abstract}" + "\n"
            latex += self.abstract + "\n"
            latex += r"\end{abstract}" + "\n\n"
        
        # Add sections
        for section in self.sections.all():
            if section.section_type == 'references':
                latex += r"\bibliographystyle{plain}" + "\n"
                latex += r"\bibliography{references}" + "\n"
            else:
                latex += f"\\section{{{section.title}}}\n"
                latex += section.content + "\n\n"
        
        # Add figures
        for figure in self.figures.all():
            latex += r"\begin{figure}[" + figure.position + "]\n"
            latex += r"\centering" + "\n"
            latex += f"\\includegraphics[width={figure.width}\\textwidth]{{{figure.file.name}}}\n"
            latex += f"\\caption{{{figure.caption}}}\n"
            latex += f"\\label{{fig:{figure.label}}}\n"
            latex += r"\end{figure}" + "\n\n"
        
        # Add tables
        for table in self.tables.all():
            latex += r"\begin{table}[" + table.position + "]\n"
            latex += r"\centering" + "\n"
            latex += f"\\caption{{{table.caption}}}\n"
            latex += f"\\label{{tab:{table.label}}}\n"
            latex += table.content + "\n"
            latex += r"\end{table}" + "\n\n"
        
        # End document
        latex += r"\end{document}"
        
        # Replace placeholders
        authors = ", ".join([self.owner.get_full_name() or self.owner.username])
        if self.collaborators.exists():
            collab_names = [c.get_full_name() or c.username for c in self.collaborators.all()]
            authors += ", " + ", ".join(collab_names)
        
        latex = latex.replace("{title}", self.title)
        latex = latex.replace("{authors}", authors)
        
        return latex


class ManuscriptSection(models.Model):
    """Sections within a manuscript."""
    SECTION_TYPES = [
        ('abstract', 'Abstract'),
        ('introduction', 'Introduction'),
        ('methods', 'Methods'),
        ('results', 'Results'),
        ('discussion', 'Discussion'),
        ('conclusion', 'Conclusion'),
        ('references', 'References'),
        ('appendix', 'Appendix'),
        ('custom', 'Custom Section'),
    ]
    
    manuscript = models.ForeignKey(Manuscript, on_delete=models.CASCADE, related_name='sections')
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.IntegerField(default=0)
    
    # AI assistance
    ai_enhanced = models.BooleanField(default=False)
    improvement_suggestions = models.JSONField(default=list)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['manuscript', 'order']
    
    def __str__(self):
        return f"{self.manuscript.title} - {self.title}"


class Figure(models.Model):
    """Figures and images in manuscripts."""
    manuscript = models.ForeignKey(Manuscript, on_delete=models.CASCADE, related_name='figures')
    
    # Figure details
    label = models.CharField(max_length=100)  # LaTeX label
    caption = models.TextField()
    file = models.ImageField(upload_to='manuscripts/figures/')
    
    # Positioning
    position = models.CharField(max_length=10, default='htbp')  # LaTeX positioning
    width = models.FloatField(default=1.0)  # Fraction of textwidth
    
    # Enhanced figure
    enhanced_file = models.ImageField(upload_to='manuscripts/figures/enhanced/', blank=True, null=True)
    ai_caption = models.TextField(blank=True)
    
    # Order and references
    order = models.IntegerField(default=0)
    referenced_in_sections = models.ManyToManyField(ManuscriptSection, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Figure {self.order}: {self.label}"


class Table(models.Model):
    """Tables in manuscripts."""
    manuscript = models.ForeignKey(Manuscript, on_delete=models.CASCADE, related_name='tables')
    
    # Table details
    label = models.CharField(max_length=100)
    caption = models.TextField()
    content = models.TextField()  # LaTeX table content
    
    # Data source
    data_file = models.FileField(upload_to='manuscripts/tables/', blank=True, null=True)
    
    # Positioning
    position = models.CharField(max_length=10, default='htbp')
    
    # Order and references
    order = models.IntegerField(default=0)
    referenced_in_sections = models.ManyToManyField(ManuscriptSection, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Table {self.order}: {self.label}"


class Citation(models.Model):
    """Bibliography entries and citations."""
    ENTRY_TYPES = [
        ('article', 'Journal Article'),
        ('book', 'Book'),
        ('inproceedings', 'Conference Paper'),
        ('techreport', 'Technical Report'),
        ('phdthesis', 'PhD Thesis'),
        ('misc', 'Miscellaneous'),
    ]
    
    # Citation key and manuscript
    citation_key = models.CharField(max_length=100)
    manuscript = models.ForeignKey(Manuscript, on_delete=models.CASCADE, related_name='citations')
    
    # Bibliographic information
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES)
    authors = models.TextField()
    title = models.CharField(max_length=500)
    year = models.IntegerField()
    
    # Additional fields
    journal = models.CharField(max_length=200, blank=True)
    volume = models.CharField(max_length=20, blank=True)
    number = models.CharField(max_length=20, blank=True)
    pages = models.CharField(max_length=50, blank=True)
    doi = models.CharField(max_length=100, blank=True)
    url = models.URLField(blank=True)
    
    # BibTeX entry
    bibtex_entry = models.TextField()
    
    # Usage tracking
    cited_in_sections = models.ManyToManyField(ManuscriptSection, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['manuscript', 'citation_key']
        ordering = ['authors', 'year']
    
    def __str__(self):
        return f"[{self.citation_key}] {self.authors[:50]}... ({self.year})"


class CompilationJob(models.Model):
    """Track LaTeX compilation jobs."""
    JOB_STATUS = [
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    COMPILATION_TYPES = [
        ('full', 'Full Compilation'),
        ('draft', 'Draft Mode'),
        ('quick', 'Quick Preview'),
    ]
    
    manuscript = models.ForeignKey(Manuscript, on_delete=models.CASCADE, related_name='compilation_jobs')
    job_id = models.UUIDField(default=uuid.uuid4, unique=True)
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='compilation_jobs')
    
    # Compilation details
    compilation_type = models.CharField(max_length=20, choices=COMPILATION_TYPES, default='full')
    
    # Status and results
    status = models.CharField(max_length=20, choices=JOB_STATUS, default='queued')
    output_pdf = models.FileField(upload_to='compilations/', blank=True, null=True)
    output_path = models.CharField(max_length=500, blank=True)  # Temporary path for downloads
    log_file = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    error_log = models.TextField(blank=True)  # Detailed error logs
    
    # Metrics
    compilation_time = models.FloatField(null=True, blank=True)  # in seconds
    page_count = models.IntegerField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Compilation {self.job_id} - {self.status}"


class AIAssistanceLog(models.Model):
    """Track AI assistance usage."""
    ASSISTANCE_TYPES = [
        ('content', 'Content Generation'),
        ('revision', 'Text Revision'),
        ('citation', 'Citation Suggestion'),
        ('figure', 'Figure Enhancement'),
        ('grammar', 'Grammar Check'),
        ('style', 'Style Improvement'),
        ('generate_section', 'Section Generation'),
    ]
    
    manuscript = models.ForeignKey(Manuscript, on_delete=models.CASCADE, related_name='ai_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Assistance details
    assistance_type = models.CharField(max_length=20, choices=ASSISTANCE_TYPES)
    section = models.ForeignKey(ManuscriptSection, on_delete=models.SET_NULL, null=True, blank=True)
    section_type = models.CharField(max_length=50, blank=True)  # Type of section being generated
    
    # Content
    prompt = models.TextField(blank=True)  # User's prompt/request
    original_text = models.TextField(blank=True)
    suggested_text = models.TextField(blank=True)
    generated_text = models.TextField(blank=True)  # AI-generated content
    accepted = models.BooleanField(default=False)
    
    # Section-specific generation
    target_section = models.CharField(max_length=50, blank=True)  # Which section is being worked on
    word_count_target = models.IntegerField(null=True, blank=True)  # Target word count for generation
    
    # Metrics
    tokens_used = models.IntegerField(default=0)
    response_time = models.FloatField(null=True, blank=True)  # in seconds
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_assistance_type_display()} - {self.manuscript.title[:50]}"