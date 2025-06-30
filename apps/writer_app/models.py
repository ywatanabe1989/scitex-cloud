from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
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
        'project_app.Project', 
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
        """Create modular LaTeX structure in project/paper/ directory using SciTeX-Writer template."""
        paper_path = self.get_project_paper_path()
        if not paper_path:
            return False
        
        # Try to copy from SciTeX-Writer template first
        if self._copy_from_scitex_writer_template(paper_path):
            return True
            
        # Fallback: Create directory structure following SciTeX-Writer pattern
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
    
    def _copy_from_scitex_writer_template(self, paper_path):
        """Copy structure from local SciTeX-Writer template if available."""
        from django.conf import settings
        import shutil
        from pathlib import Path
        
        try:
            template_path = Path(settings.SCITEX_WRITER_TEMPLATE_PATH)
            if not template_path.exists():
                print(f"SciTeX-Writer template not found at {template_path}")
                return False
            
            # Create paper directory
            paper_path.mkdir(parents=True, exist_ok=True)
            
            # Copy key directories from SciTeX-Writer template
            template_dirs = {
                'manuscript': 'manuscript',
                'revision': 'revision', 
                'scripts': 'scripts',
                'supplementary': 'supplementary'
            }
            
            for src_dir, dst_dir in template_dirs.items():
                src_path = template_path / src_dir
                dst_path = paper_path / dst_dir
                
                if src_path.exists():
                    if dst_path.exists():
                        shutil.rmtree(dst_path)
                    shutil.copytree(src_path, dst_path)
                    print(f"Copied {src_dir} to {dst_path}")
            
            # Copy essential files
            essential_files = [
                'README.md'
            ]
            
            for file_path in essential_files:
                src_file = template_path / file_path
                dst_file = paper_path / file_path
                
                if src_file.exists():
                    dst_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, dst_file)
                    print(f"Copied {file_path}")
            
            # Create a compile.sh script in paper root
            compile_script = paper_path / 'compile.sh'
            compile_script.write_text(f'''#!/bin/bash
# SciTeX-Writer compilation script
# Generated for project: {self.project.name if self.project else self.title}

cd manuscript
if [ -f ../scripts/compile-manuscript.sh ]; then
    bash ../scripts/compile-manuscript.sh
else
    pdflatex main.tex
fi
''')
            compile_script.chmod(0o755)
            
            # Create references directory and bib file if not exists
            references_dir = paper_path / 'references'
            references_dir.mkdir(exist_ok=True)
            
            bib_file = references_dir / 'references.bib'
            if not bib_file.exists():
                bib_file.write_text(f'''% Bibliography for {self.title}
% Generated by SciTeX Cloud

@article{{example2024,
    title={{Example Paper Title}},
    author={{Author, First}},
    journal={{Example Journal}},
    year={{2024}},
    volume={{1}},
    pages={{1--10}}
}}
''')
            
            print(f"Successfully copied SciTeX-Writer template to {paper_path}")
            return True
            
        except Exception as e:
            print(f"Error copying SciTeX-Writer template: {e}")
            return False
    
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


class CollaborativeSession(models.Model):
    """Track collaborative editing sessions for real-time collaboration."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    manuscript = models.ForeignKey(Manuscript, on_delete=models.CASCADE, related_name='collaborative_sessions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='writing_sessions')
    
    # Session details
    session_id = models.CharField(max_length=100)  # WebSocket session identifier
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Collaboration features
    locked_sections = models.JSONField(default=list, blank=True)  # List of section IDs locked by this user
    cursor_position = models.JSONField(default=dict, blank=True)  # Current cursor position
    
    # Statistics
    characters_typed = models.IntegerField(default=0)
    operations_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_activity']
        unique_together = ['manuscript', 'user', 'session_id']
    
    def __str__(self):
        return f"{self.user.username} - {self.manuscript.title[:30]} ({self.session_id[:8]})"
    
    @property
    def session_duration(self):
        """Calculate session duration."""
        end_time = self.ended_at or timezone.now()
        return end_time - self.started_at
    
    def is_session_active(self):
        """Check if session is still active (within 5 minutes of last activity)."""
        if not self.is_active:
            return False
        return timezone.now() - self.last_activity < timedelta(minutes=5)


class DocumentChange(models.Model):
    """Track individual document changes for version control and operational transforms."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    manuscript = models.ForeignKey(Manuscript, on_delete=models.CASCADE, related_name='document_changes')
    section = models.ForeignKey(ManuscriptSection, on_delete=models.CASCADE, related_name='changes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_changes')
    session = models.ForeignKey(CollaborativeSession, on_delete=models.CASCADE, related_name='changes')
    
    # Change details
    change_type = models.CharField(max_length=20, choices=[
        ('insert', 'Text Insertion'),
        ('delete', 'Text Deletion'),
        ('replace', 'Text Replacement'),
        ('format', 'Formatting Change'),
    ])
    
    # Operation details for operational transforms
    operation_data = models.JSONField()  # Contains position, text, length, etc.
    
    # Content tracking
    content_before = models.TextField(blank=True)  # Content before change
    content_after = models.TextField(blank=True)   # Content after change
    
    # Version control
    version_number = models.IntegerField(default=1)
    parent_change = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Operational transform state
    transform_applied = models.BooleanField(default=False)
    conflict_resolved = models.BooleanField(default=False)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_change_type_display()} by {self.user.username} - {self.section.title}"


class ManuscriptVersion(models.Model):
    """Track manuscript versions with comprehensive change history and branching."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    manuscript = models.ForeignKey(Manuscript, on_delete=models.CASCADE, related_name='versions')
    
    # Version identification
    version_number = models.CharField(max_length=20)  # e.g., "1.0", "1.1", "2.0-beta"
    version_tag = models.CharField(max_length=100, blank=True)  # e.g., "Initial Draft", "Reviewer Comments Addressed"
    branch_name = models.CharField(max_length=50, default='main')  # Git-style branching
    
    # Version metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_versions')
    created_at = models.DateTimeField(auto_now_add=True)
    commit_message = models.TextField(blank=True)
    
    # Content snapshot
    manuscript_data = models.JSONField()  # Complete manuscript state at this version
    section_contents = models.JSONField()  # Section-by-section content
    
    # Version relationships
    parent_version = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_versions')
    is_major_version = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    
    # Statistics
    total_changes = models.IntegerField(default=0)
    word_count_delta = models.IntegerField(default=0)
    lines_added = models.IntegerField(default=0)
    lines_removed = models.IntegerField(default=0)
    
    # File attachments
    version_file = models.FileField(upload_to='manuscript_versions/', blank=True, null=True)
    diff_file = models.FileField(upload_to='manuscript_diffs/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['manuscript', 'version_number', 'branch_name']
    
    def __str__(self):
        return f"{self.manuscript.title} - v{self.version_number} ({self.branch_name})"
    
    def get_version_summary(self):
        """Get a summary of changes in this version."""
        return {
            'version': self.version_number,
            'branch': self.branch_name,
            'tag': self.version_tag,
            'author': self.created_by.username,
            'date': self.created_at,
            'message': self.commit_message,
            'changes': self.total_changes,
            'word_delta': self.word_count_delta,
            'lines_added': self.lines_added,
            'lines_removed': self.lines_removed
        }


class ManuscriptBranch(models.Model):
    """Manage manuscript branches for parallel development."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    manuscript = models.ForeignKey(Manuscript, on_delete=models.CASCADE, related_name='branches')
    
    # Branch identification
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    
    # Branch metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_branches')
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Branch relationships
    parent_branch = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_branches')
    base_version = models.ForeignKey(ManuscriptVersion, on_delete=models.SET_NULL, null=True, related_name='branched_from')
    
    # Branch status
    is_active = models.BooleanField(default=True)
    is_merged = models.BooleanField(default=False)
    merged_at = models.DateTimeField(null=True, blank=True)
    merged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='merged_branches')
    
    # Statistics
    total_commits = models.IntegerField(default=0)
    contributors = models.ManyToManyField(User, related_name='contributed_branches', blank=True)
    
    class Meta:
        ordering = ['-last_updated']
        unique_together = ['manuscript', 'name']
    
    def __str__(self):
        return f"{self.manuscript.title} - {self.name} branch"
    
    def get_latest_version(self):
        """Get the latest version in this branch."""
        return self.manuscript.versions.filter(branch_name=self.name).first()
    
    def get_commits_ahead_behind(self, target_branch='main'):
        """Calculate commits ahead/behind target branch."""
        # Implementation for branch comparison
        target_versions = self.manuscript.versions.filter(branch_name=target_branch).count()
        current_versions = self.manuscript.versions.filter(branch_name=self.name).count()
        return {
            'ahead': max(0, current_versions - target_versions),
            'behind': max(0, target_versions - current_versions)
        }


class DiffResult(models.Model):
    """Store computed diffs between manuscript versions."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    manuscript = models.ForeignKey(Manuscript, on_delete=models.CASCADE, related_name='diffs')
    
    # Diff identification
    from_version = models.ForeignKey(ManuscriptVersion, on_delete=models.CASCADE, related_name='diffs_from')
    to_version = models.ForeignKey(ManuscriptVersion, on_delete=models.CASCADE, related_name='diffs_to')
    
    # Diff data
    diff_type = models.CharField(max_length=20, choices=[
        ('unified', 'Unified Diff'),
        ('side_by_side', 'Side by Side'),
        ('word_level', 'Word Level'),
        ('semantic', 'Semantic Diff'),
    ], default='unified')
    
    diff_data = models.JSONField()  # Structured diff information
    diff_html = models.TextField(blank=True)  # Pre-rendered HTML diff
    diff_stats = models.JSONField(default=dict)  # Statistics about the diff
    
    # Caching
    computed_at = models.DateTimeField(auto_now_add=True)
    is_cached = models.BooleanField(default=True)
    cache_expires = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-computed_at']
        unique_together = ['from_version', 'to_version', 'diff_type']
    
    def __str__(self):
        return f"Diff: {self.from_version.version_number} → {self.to_version.version_number}"
    
    def is_valid_cache(self):
        """Check if cached diff is still valid."""
        if not self.is_cached:
            return False
        if self.cache_expires and timezone.now() > self.cache_expires:
            return False
        return True


class MergeRequest(models.Model):
    """Manage merge requests between manuscript branches."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    manuscript = models.ForeignKey(Manuscript, on_delete=models.CASCADE, related_name='merge_requests')
    
    # Merge identification
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Branch information
    source_branch = models.ForeignKey(ManuscriptBranch, on_delete=models.CASCADE, related_name='merge_requests_from')
    target_branch = models.ForeignKey(ManuscriptBranch, on_delete=models.CASCADE, related_name='merge_requests_to')
    source_version = models.ForeignKey(ManuscriptVersion, on_delete=models.CASCADE, related_name='merge_requests_from_version')
    target_version = models.ForeignKey(ManuscriptVersion, on_delete=models.CASCADE, related_name='merge_requests_to_version')
    
    # Request metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_merge_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Review process
    status = models.CharField(max_length=20, choices=[
        ('open', 'Open'),
        ('review', 'In Review'),
        ('approved', 'Approved'),
        ('merged', 'Merged'),
        ('closed', 'Closed'),
        ('draft', 'Draft'),
    ], default='open')
    
    reviewers = models.ManyToManyField(User, related_name='merge_requests_to_review', blank=True)
    approved_by = models.ManyToManyField(User, related_name='approved_merge_requests', blank=True)
    
    # Merge information
    merged_at = models.DateTimeField(null=True, blank=True)
    merged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='merged_requests')
    merge_commit = models.ForeignKey(ManuscriptVersion, on_delete=models.SET_NULL, null=True, blank=True, related_name='merge_commit_for')
    
    # Conflict resolution
    has_conflicts = models.BooleanField(default=False)
    conflict_data = models.JSONField(default=dict)
    auto_mergeable = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"MR: {self.source_branch.name} → {self.target_branch.name}"
    
    def can_auto_merge(self):
        """Check if merge request can be automatically merged."""
        return self.auto_mergeable and not self.has_conflicts and self.status == 'approved'


# arXiv Integration Models
class ArxivAccount(models.Model):
    """Store arXiv account credentials and verification status."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='arxiv_account')
    
    # Account credentials
    arxiv_username = models.CharField(max_length=200)
    arxiv_password = models.CharField(max_length=500)  # Will be encrypted
    arxiv_email = models.EmailField()
    
    # Verification status
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=255, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Account metadata
    orcid_id = models.CharField(max_length=50, blank=True)
    affiliation = models.CharField(max_length=500, blank=True)
    
    # Submission limits and status
    daily_submission_limit = models.IntegerField(default=5)
    submissions_today = models.IntegerField(default=0)
    last_submission_date = models.DateField(null=True, blank=True)
    
    # Account status
    is_active = models.BooleanField(default=True)
    suspension_reason = models.TextField(blank=True)
    suspended_until = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"arXiv Account: {self.arxiv_username} ({'Verified' if self.is_verified else 'Unverified'})"
    
    def can_submit_today(self):
        """Check if user can submit today based on daily limits."""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.last_submission_date != today:
            self.submissions_today = 0
            self.last_submission_date = today
            self.save()
        
        return self.submissions_today < self.daily_submission_limit
    
    def increment_daily_submissions(self):
        """Increment daily submission count."""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.last_submission_date != today:
            self.submissions_today = 0
            self.last_submission_date = today
        
        self.submissions_today += 1
        self.save()


class ArxivCategory(models.Model):
    """arXiv subject categories."""
    code = models.CharField(max_length=20, unique=True)  # e.g., 'cs.AI', 'physics.gen-ph'
    name = models.CharField(max_length=200)
    description = models.TextField()
    parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Category metadata
    is_active = models.BooleanField(default=True)
    submission_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['code']
        verbose_name_plural = 'arXiv Categories'
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ArxivSubmission(models.Model):
    """Track arXiv submission records."""
    SUBMISSION_STATUS = [
        ('draft', 'Draft'),
        ('validating', 'Validating'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
        ('replaced', 'Replaced'),
    ]
    
    SUBMISSION_TYPE = [
        ('new', 'New Submission'),
        ('replacement', 'Replacement'),
        ('withdrawal', 'Withdrawal'),
        ('cross_list', 'Cross-list'),
    ]
    
    # Core relationships
    manuscript = models.ForeignKey(Manuscript, on_delete=models.CASCADE, related_name='arxiv_submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='arxiv_submissions')
    arxiv_account = models.ForeignKey(ArxivAccount, on_delete=models.CASCADE, related_name='submissions')
    
    # Submission identification
    submission_id = models.UUIDField(default=uuid.uuid4, unique=True)
    arxiv_id = models.CharField(max_length=50, blank=True)  # e.g., '2312.12345'
    arxiv_url = models.URLField(blank=True)
    
    # Submission metadata
    submission_type = models.CharField(max_length=20, choices=SUBMISSION_TYPE, default='new')
    status = models.CharField(max_length=20, choices=SUBMISSION_STATUS, default='draft')
    
    # Categories
    primary_category = models.ForeignKey(ArxivCategory, on_delete=models.PROTECT, related_name='primary_submissions')
    secondary_categories = models.ManyToManyField(ArxivCategory, blank=True, related_name='secondary_submissions')
    
    # Manuscript details for submission
    title = models.CharField(max_length=500)
    abstract = models.TextField()
    authors = models.TextField()  # Formatted author list
    
    # Files
    latex_source = models.FileField(upload_to='arxiv_submissions/latex/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='arxiv_submissions/pdfs/', blank=True, null=True)
    supplementary_files = models.JSONField(default=list)  # List of additional file paths
    
    # Submission comments and journal reference
    comments = models.TextField(blank=True)  # e.g., "28 pages, 15 figures"
    journal_reference = models.CharField(max_length=500, blank=True)
    doi = models.CharField(max_length=100, blank=True)
    
    # arXiv specific fields
    arxiv_comments = models.TextField(blank=True)  # Comments from arXiv moderators
    moderation_reason = models.TextField(blank=True)  # Reason for rejection/hold
    
    # Version management
    version = models.IntegerField(default=1)
    replaces_submission = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replacements')
    
    # Status tracking
    submitted_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    last_status_check = models.DateTimeField(null=True, blank=True)
    
    # Administrative
    admin_notes = models.TextField(blank=True)
    is_test_submission = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['manuscript', 'version']
    
    def __str__(self):
        arxiv_display = f" ({self.arxiv_id})" if self.arxiv_id else ""
        return f"arXiv Submission: {self.title[:50]}...{arxiv_display}"
    
    def get_status_display_with_details(self):
        """Get detailed status display."""
        status_map = {
            'draft': 'Draft - Not yet submitted',
            'validating': 'Validating - Checking submission requirements',
            'submitted': 'Submitted - Awaiting arXiv processing',
            'under_review': 'Under Review - Being reviewed by arXiv moderators',
            'approved': 'Approved - Will be published in next announcement',
            'published': f'Published - Available at {self.arxiv_url}' if self.arxiv_url else 'Published',
            'rejected': f'Rejected - {self.moderation_reason}' if self.moderation_reason else 'Rejected',
            'withdrawn': 'Withdrawn - Submission withdrawn by author',
            'replaced': 'Replaced - Superseded by newer version',
        }
        return status_map.get(self.status, self.get_status_display())
    
    def can_be_replaced(self):
        """Check if submission can be replaced with a new version."""
        return self.status in ['published', 'approved'] and not self.replacements.exists()
    
    def can_be_withdrawn(self):
        """Check if submission can be withdrawn."""
        return self.status in ['submitted', 'under_review', 'approved', 'published']


class ArxivSubmissionHistory(models.Model):
    """Track status changes and updates for arXiv submissions."""
    submission = models.ForeignKey(ArxivSubmission, on_delete=models.CASCADE, related_name='history')
    
    # Status change details
    previous_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    change_reason = models.TextField(blank=True)
    
    # External data
    arxiv_response = models.JSONField(default=dict)  # Full response from arXiv API
    error_details = models.TextField(blank=True)
    
    # User action
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_automatic = models.BooleanField(default=True)  # True for API updates, False for manual changes
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'arXiv Submission Histories'
    
    def __str__(self):
        return f"{self.submission.title[:30]}... - {self.previous_status} → {self.new_status}"


class ArxivValidationResult(models.Model):
    """Store validation results for arXiv submissions."""
    VALIDATION_STATUS = [
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('warning', 'Warning'),
    ]
    
    submission = models.OneToOneField(ArxivSubmission, on_delete=models.CASCADE, related_name='validation')
    
    # Overall validation status
    status = models.CharField(max_length=20, choices=VALIDATION_STATUS, default='pending')
    overall_score = models.FloatField(default=0.0)  # 0-100 validation score
    
    # Individual validation checks
    latex_compilation = models.CharField(max_length=20, choices=VALIDATION_STATUS, default='pending')
    pdf_generation = models.CharField(max_length=20, choices=VALIDATION_STATUS, default='pending')
    metadata_validation = models.CharField(max_length=20, choices=VALIDATION_STATUS, default='pending')
    category_validation = models.CharField(max_length=20, choices=VALIDATION_STATUS, default='pending')
    file_format_check = models.CharField(max_length=20, choices=VALIDATION_STATUS, default='pending')
    
    # Detailed results
    validation_details = models.JSONField(default=dict)
    error_messages = models.JSONField(default=list)
    warning_messages = models.JSONField(default=list)
    
    # LaTeX specific checks
    latex_log = models.TextField(blank=True)
    bibtex_issues = models.JSONField(default=list)
    missing_figures = models.JSONField(default=list)
    
    # arXiv specific requirements
    title_length_check = models.BooleanField(default=False)
    abstract_length_check = models.BooleanField(default=False)
    author_format_check = models.BooleanField(default=False)
    
    # File size and format checks
    total_file_size = models.FloatField(default=0.0)  # in MB
    max_file_size_exceeded = models.BooleanField(default=False)
    unsupported_files = models.JSONField(default=list)
    
    # Validation timestamps
    validation_started = models.DateTimeField(auto_now_add=True)
    validation_completed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-validation_started']
    
    def __str__(self):
        return f"Validation: {self.submission.title[:30]}... - {self.status}"
    
    def is_ready_for_submission(self):
        """Check if validation passed all required checks."""
        return (
            self.status == 'passed' and
            self.latex_compilation == 'passed' and
            self.pdf_generation == 'passed' and
            self.metadata_validation == 'passed' and
            not self.max_file_size_exceeded
        )
    
    def get_validation_summary(self):
        """Get a summary of validation results."""
        return {
            'status': self.status,
            'score': self.overall_score,
            'checks': {
                'latex': self.latex_compilation,
                'pdf': self.pdf_generation,
                'metadata': self.metadata_validation,
                'category': self.category_validation,
                'file_format': self.file_format_check,
            },
            'errors': len(self.error_messages),
            'warnings': len(self.warning_messages),
            'ready': self.is_ready_for_submission()
        }


class ArxivApiResponse(models.Model):
    """Log arXiv API responses for debugging and monitoring."""
    submission = models.ForeignKey(ArxivSubmission, on_delete=models.CASCADE, related_name='api_responses')
    
    # Request details
    api_endpoint = models.CharField(max_length=200)
    request_method = models.CharField(max_length=10)
    request_data = models.JSONField(default=dict)
    
    # Response details
    response_status = models.IntegerField()
    response_data = models.JSONField(default=dict)
    response_headers = models.JSONField(default=dict)
    
    # Timing
    request_time = models.DateTimeField()
    response_time = models.DateTimeField()
    duration_ms = models.IntegerField()  # Duration in milliseconds
    
    # Error tracking
    is_error = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"API Response: {self.api_endpoint} - {self.response_status}"