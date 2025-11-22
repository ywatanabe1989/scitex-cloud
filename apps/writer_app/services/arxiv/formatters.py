"""
arXiv Manuscript Formatting Utilities

This module provides specialized formatters for converting SciTeX manuscripts
to arXiv-compatible formats, including LaTeX cleanup, bibliography processing,
and PDF generation with arXiv requirements.
"""

import re
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple


from ...models import ArxivSubmission, Citation, Manuscript


class ArxivLatexFormatter:
    """Format LaTeX content for arXiv submission compliance."""

    def __init__(self):
        self.arxiv_class_options = {
            "article": r"\documentclass[12pt]{article}",
            "revtex": r"\documentclass[12pt,prd,aps]{revtex4-2}",  # For physics papers
            "neurips": r"\documentclass[final]{neurips_2023}",  # For ML papers
        }

        # arXiv-approved packages
        self.approved_packages = {
            "amsmath",
            "amsfonts",
            "amssymb",
            "amsthm",
            "graphicx",
            "cite",
            "natbib",
            "biblatex",
            "hyperref",
            "url",
            "geometry",
            "fancyhdr",
            "array",
            "booktabs",
            "longtable",
            "multirow",
            "algorithm",
            "algorithmic",
            "algorithm2e",
            "listings",
            "xcolor",
            "tikz",
            "pgfplots",
            "subcaption",
            "caption",
            "float",
        }

        # Packages to remove or replace
        self.problematic_packages = {
            "pstricks": None,  # Not supported on arXiv
            "xy": "xymatrix",  # Replace with xymatrix
            "pdfpages": None,  # Not allowed
            "epstopdf": None,  # Automatic conversion
        }

    def format_for_arxiv(
        self, manuscript: Manuscript, document_class: str = "article"
    ) -> str:
        """
        Format manuscript LaTeX for arXiv submission.

        Args:
            manuscript: Manuscript to format
            document_class: LaTeX document class to use

        Returns:
            Formatted LaTeX content
        """
        if manuscript.is_modular:
            return self._format_modular_manuscript(manuscript, document_class)
        else:
            return self._format_standard_manuscript(manuscript, document_class)

    def _format_modular_manuscript(
        self, manuscript: Manuscript, document_class: str
    ) -> str:
        """Format modular manuscript structure for arXiv."""
        # Get paper path
        paper_path = manuscript.get_project_paper_path()
        if not paper_path:
            raise ValueError("Cannot access modular manuscript files")

        # Read main.tex and sections
        main_tex_path = paper_path / "manuscript" / "main.tex"
        if main_tex_path.exists():
            with open(main_tex_path, "r", encoding="utf-8") as f:
                main_content = f.read()
        else:
            main_content = self._generate_default_main_tex(manuscript, document_class)

        # Process and combine sections
        sections_content = self._compile_sections(paper_path / "manuscript" / "src")

        # Replace \\input commands with actual content
        latex_content = self._replace_input_commands(main_content, sections_content)

        # Clean and validate LaTeX
        return self._clean_latex_for_arxiv(latex_content)

    def _format_standard_manuscript(
        self, manuscript: Manuscript, document_class: str
    ) -> str:
        """Format standard (non-modular) manuscript for arXiv."""
        # Generate complete LaTeX document
        latex_content = self._generate_complete_latex(manuscript, document_class)

        # Clean and validate LaTeX
        return self._clean_latex_for_arxiv(latex_content)

    def _generate_default_main_tex(
        self, manuscript: Manuscript, document_class: str
    ) -> str:
        """Generate default main.tex structure."""
        template = self.arxiv_class_options.get(
            document_class, self.arxiv_class_options["article"]
        )

        return f"""{template}

% Essential packages for arXiv
\\usepackage[utf8]{{inputenc}}
\\usepackage[english]{{babel}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{cite}}
\\usepackage{{url}}
\\usepackage[margin=1in]{{geometry}}

% Manuscript metadata
\\title{{{manuscript.title}}}
\\author{{{self._format_authors(manuscript)}}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle

\\begin{{abstract}}
{manuscript.abstract or "Abstract content."}
\\end{{abstract}}

% Keywords
{self._format_keywords(manuscript)}

% Main content sections
\\input{{src/introduction}}
\\input{{src/methods}}
\\input{{src/results}}
\\input{{src/discussion}}
\\input{{src/conclusion}}

% Bibliography
\\bibliographystyle{{plain}}
\\bibliography{{references}}

\\end{{document}}
"""

    def _compile_sections(self, src_path: Path) -> Dict[str, str]:
        """Compile content from individual section files."""
        sections = {}

        section_files = [
            "abstract.tex",
            "introduction.tex",
            "methods.tex",
            "results.tex",
            "discussion.tex",
            "conclusion.tex",
        ]

        for section_file in section_files:
            file_path = src_path / section_file
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        sections[section_file] = self._clean_section_content(content)
                except Exception as e:
                    sections[section_file] = f"% Error reading {section_file}: {str(e)}"
            else:
                sections[section_file] = f"% Section {section_file} not found"

        return sections

    def _replace_input_commands(
        self, main_content: str, sections: Dict[str, str]
    ) -> str:
        """Replace \\input commands with actual section content."""
        # Pattern to match \\input{src/filename} or \\input{filename}
        input_pattern = r"\\input\{(?:src/)?([^}]+)\}"

        def replace_input(match):
            filename = match.group(1)
            if not filename.endswith(".tex"):
                filename += ".tex"

            return sections.get(filename, f"% Content for {filename} not found")

        return re.sub(input_pattern, replace_input, main_content)

    def _generate_complete_latex(
        self, manuscript: Manuscript, document_class: str
    ) -> str:
        """Generate complete LaTeX document from manuscript data."""
        template = self.arxiv_class_options.get(
            document_class, self.arxiv_class_options["article"]
        )

        # Build complete document
        latex_parts = [
            template,
            "",
            "% Essential packages for arXiv",
            "\\usepackage[utf8]{inputenc}",
            "\\usepackage[english]{babel}",
            "\\usepackage{amsmath}",
            "\\usepackage{amsfonts}",
            "\\usepackage{amssymb}",
            "\\usepackage{graphicx}",
            "\\usepackage{cite}",
            "\\usepackage{url}",
            "\\usepackage[margin=1in]{geometry}",
            "",
            "% Manuscript metadata",
            f"\\title{{{manuscript.title}}}",
            f"\\author{{{self._format_authors(manuscript)}}}",
            "\\date{\\today}",
            "",
            "\\begin{document}",
            "",
            "\\maketitle",
            "",
            "\\begin{abstract}",
            manuscript.abstract or "Abstract content.",
            "\\end{abstract}",
            "",
            self._format_keywords(manuscript),
            "",
            manuscript.content or "% Main content here",
            "",
            self._format_figures(manuscript),
            "",
            self._format_tables(manuscript),
            "",
            "% Bibliography",
            "\\bibliographystyle{plain}",
            "\\bibliography{references}",
            "",
            "\\end{document}",
        ]

        return "\n".join(latex_parts)

    def _clean_latex_for_arxiv(self, latex_content: str) -> str:
        """Clean LaTeX content for arXiv compliance."""
        # Remove problematic packages
        latex_content = self._remove_problematic_packages(latex_content)

        # Fix common issues
        latex_content = self._fix_common_latex_issues(latex_content)

        # Validate package usage
        latex_content = self._validate_packages(latex_content)

        # Clean up formatting
        latex_content = self._clean_formatting(latex_content)

        return latex_content

    def _remove_problematic_packages(self, content: str) -> str:
        """Remove or replace packages not supported by arXiv."""
        for problematic, replacement in self.problematic_packages.items():
            pattern = rf"\\usepackage(?:\[[^\]]*\])?\{{{problematic}\}}"
            if replacement:
                replacement_line = f"\\usepackage{{{replacement}}}"
                content = re.sub(pattern, replacement_line, content)
            else:
                content = re.sub(
                    pattern, f"% Removed unsupported package: {problematic}", content
                )

        return content

    def _fix_common_latex_issues(self, content: str) -> str:
        """Fix common LaTeX issues for arXiv."""
        # Fix figure paths (remove absolute paths)
        content = re.sub(
            r"\\includegraphics\{[^}]*[/\\]([^/\\}]+)\}",
            r"\\includegraphics{\1}",
            content,
        )

        # Ensure UTF-8 encoding
        if (
            "\\usepackage[utf8]{inputenc}" not in content
            and "\\documentclass" in content
        ):
            content = content.replace(
                "\\documentclass", "\\usepackage[utf8]{inputenc}\n\\documentclass"
            )

        # Fix citation commands
        content = re.sub(r"\\cite\s*\{([^}]+)\}", r"\\cite{\1}", content)

        # Remove excessive whitespace
        content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)

        return content

    def _validate_packages(self, content: str) -> str:
        """Validate that only approved packages are used."""
        # Find all package imports
        package_pattern = r"\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}"
        packages = re.findall(package_pattern, content)

        warnings = []
        for package in packages:
            if package not in self.approved_packages:
                warnings.append(
                    f"Warning: Package '{package}' may not be supported by arXiv"
                )

        if warnings:
            warning_comment = (
                "% arXiv Package Warnings:\n% " + "\n% ".join(warnings) + "\n\n"
            )
            content = warning_comment + content

        return content

    def _clean_formatting(self, content: str) -> str:
        """Clean up LaTeX formatting."""
        # Remove extra spaces around braces
        content = re.sub(r"\s*\{\s*", "{", content)
        content = re.sub(r"\s*\}\s*", "}", content)

        # Fix line breaks
        content = re.sub(r"(?<!\\)\\\\(?!\s*\n)", "\\\\\n", content)

        # Clean up comments
        content = re.sub(r"%\s*$", "%", content, flags=re.MULTILINE)

        return content

    def _clean_section_content(self, content: str) -> str:
        """Clean individual section content."""
        # Remove section commands if they exist (will be added by main document)
        content = re.sub(r"^\\section\*?\{[^}]+\}\s*", "", content, flags=re.MULTILINE)

        # Clean up whitespace
        content = content.strip()

        return content

    def _format_authors(self, manuscript: Manuscript) -> str:
        """Format author list for LaTeX."""
        authors = []

        # Primary author
        primary_author = manuscript.owner
        authors.append(primary_author.get_full_name() or primary_author.username)

        # Collaborators
        for collaborator in manuscript.collaborators.all():
            authors.append(collaborator.get_full_name() or collaborator.username)

        return " \\and ".join(authors)

    def _format_keywords(self, manuscript: Manuscript) -> str:
        """Format keywords section."""
        if manuscript.keywords:
            return f"\\textbf{{Keywords:}} {manuscript.keywords}"
        return "% Keywords: Add relevant keywords here"

    def _format_figures(self, manuscript: Manuscript) -> str:
        """Format figures for LaTeX."""
        if not manuscript.figures.exists():
            return "% No figures"

        figures_latex = []
        for figure in manuscript.figures.all():
            figure_latex = f"""\\begin{{figure}}[{figure.position}]
\\centering
\\includegraphics[width={figure.width}\\textwidth]{{figures/{figure.file.name.split("/")[-1]}}}
\\caption{{{figure.caption}}}
\\label{{fig:{figure.label}}}
\\end{{figure}}"""
            figures_latex.append(figure_latex)

        return "\n\n".join(figures_latex)

    def _format_tables(self, manuscript: Manuscript) -> str:
        """Format tables for LaTeX."""
        if not manuscript.tables.exists():
            return "% No tables"

        tables_latex = []
        for table in manuscript.tables.all():
            table_latex = f"""\\begin{{table}}[{table.position}]
\\centering
\\caption{{{table.caption}}}
\\label{{tab:{table.label}}}
{table.content}
\\end{{table}}"""
            tables_latex.append(table_latex)

        return "\n\n".join(tables_latex)


class ArxivBibliographyFormatter:
    """Format bibliography for arXiv submission."""

    def __init__(self):
        self.biblatex_to_bibtex_map = {
            "journaltitle": "journal",
            "location": "address",
            "date": "year",
        }

    def format_bibliography(self, manuscript: Manuscript) -> str:
        """
        Generate arXiv-compatible bibliography file.

        Args:
            manuscript: Manuscript with citations

        Returns:
            BibTeX content string
        """
        citations = manuscript.citations.all()
        if not citations:
            return self._get_default_bibliography()

        bib_entries = []
        bib_entries.append("% Bibliography for arXiv submission")
        bib_entries.append("% Generated from SciTeX Writer")
        bib_entries.append("")

        for citation in citations:
            formatted_entry = self._format_citation_entry(citation)
            bib_entries.append(formatted_entry)
            bib_entries.append("")

        return "\n".join(bib_entries)

    def _format_citation_entry(self, citation: Citation) -> str:
        """Format individual citation entry for BibTeX."""
        if citation.bibtex_entry:
            # Clean existing BibTeX entry
            return self._clean_bibtex_entry(citation.bibtex_entry)
        else:
            # Generate BibTeX entry from citation fields
            return self._generate_bibtex_entry(citation)

    def _clean_bibtex_entry(self, bibtex_entry: str) -> str:
        """Clean BibTeX entry for arXiv compatibility."""
        # Convert biblatex fields to bibtex
        for biblatex_field, bibtex_field in self.biblatex_to_bibtex_map.items():
            bibtex_entry = re.sub(
                rf"\b{biblatex_field}\s*=", f"{bibtex_field} =", bibtex_entry
            )

        # Remove unsupported fields
        unsupported_fields = ["url", "urldate", "file", "abstract"]
        for field in unsupported_fields:
            bibtex_entry = re.sub(
                rf"\s*{field}\s*=\s*\{{[^}}]*\}},?\s*",
                "",
                bibtex_entry,
                flags=re.IGNORECASE,
            )

        # Clean up formatting
        bibtex_entry = re.sub(r",\s*}", "\n}", bibtex_entry)

        return bibtex_entry

    def _generate_bibtex_entry(self, citation: Citation) -> str:
        """Generate BibTeX entry from citation fields."""
        entry_type = citation.entry_type
        key = citation.citation_key

        fields = []
        fields.append(f"title = {{{citation.title}}}")
        fields.append(f"author = {{{citation.authors}}}")
        fields.append(f"year = {{{citation.year}}}")

        if citation.journal:
            fields.append(f"journal = {{{citation.journal}}}")
        if citation.volume:
            fields.append(f"volume = {{{citation.volume}}}")
        if citation.number:
            fields.append(f"number = {{{citation.number}}}")
        if citation.pages:
            fields.append(f"pages = {{{citation.pages}}}")
        if citation.doi:
            fields.append(f"doi = {{{citation.doi}}}")

        fields_str = ",\n  ".join(fields)

        return f"""@{entry_type}{{{key},
  {fields_str}
}}"""

    def _get_default_bibliography(self) -> str:
        """Get default bibliography template."""
        return """% Bibliography for arXiv submission
% Add your citations here in BibTeX format

% Example entry:
% @article{example2023,
%   title={Example Article Title},
%   author={Author, First and Second, Author},
%   journal={Journal Name},
%   volume={1},
%   number={1},
%   pages={1--10},
%   year={2023}
% }
"""


class ArxivFilePackager:
    """Package files for arXiv submission."""

    def __init__(self):
        self.max_file_size = 50 * 1024 * 1024  # 50MB limit
        self.allowed_extensions = {
            ".tex",
            ".bib",
            ".bbl",
            ".cls",
            ".sty",
            ".eps",
            ".ps",
            ".pdf",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
        }

    def package_submission(self, submission: ArxivSubmission, work_dir: Path) -> Path:
        """
        Package all files for arXiv submission.

        Args:
            submission: ArxivSubmission to package
            work_dir: Working directory containing files

        Returns:
            Path to created submission package (zip file)
        """
        package_path = work_dir / f"arxiv_submission_{submission.submission_id}.zip"

        with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Add main LaTeX file
            if (work_dir / "main.tex").exists():
                zipf.write(work_dir / "main.tex", "main.tex")

            # Add bibliography
            if (work_dir / "references.bib").exists():
                zipf.write(work_dir / "references.bib", "references.bib")

            # Add figures
            figures_dir = work_dir / "figures"
            if figures_dir.exists():
                for figure_file in figures_dir.iterdir():
                    if (
                        figure_file.is_file()
                        and figure_file.suffix.lower() in self.allowed_extensions
                    ):
                        zipf.write(figure_file, f"figures/{figure_file.name}")

            # Add any additional files
            for file_path in work_dir.iterdir():
                if (
                    file_path.is_file()
                    and file_path.suffix.lower() in self.allowed_extensions
                    and file_path.name not in ["main.tex", "references.bib"]
                ):
                    zipf.write(file_path, file_path.name)

        # Check file size
        if package_path.stat().st_size > self.max_file_size:
            raise ValueError(
                f"Submission package exceeds {self.max_file_size / (1024 * 1024):.1f}MB limit"
            )

        return package_path

    def validate_file_types(self, work_dir: Path) -> Tuple[List[str], List[str]]:
        """
        Validate file types in submission.

        Args:
            work_dir: Directory to validate

        Returns:
            Tuple of (valid_files, invalid_files)
        """
        valid_files = []
        invalid_files = []

        for file_path in work_dir.rglob("*"):
            if file_path.is_file():
                if file_path.suffix.lower() in self.allowed_extensions:
                    valid_files.append(str(file_path.relative_to(work_dir)))
                else:
                    invalid_files.append(str(file_path.relative_to(work_dir)))

        return valid_files, invalid_files


class ArxivComplianceChecker:
    """Check manuscript compliance with arXiv requirements."""

    def __init__(self):
        self.required_sections = ["title", "abstract", "introduction"]
        self.max_title_length = 256
        self.max_abstract_length = 1920
        self.min_abstract_length = 100

    def check_compliance(
        self, manuscript: Manuscript, latex_content: str
    ) -> Dict[str, any]:
        """
        Check manuscript compliance with arXiv requirements.

        Args:
            manuscript: Manuscript to check
            latex_content: LaTeX content

        Returns:
            Dictionary with compliance results
        """
        compliance_results = {
            "is_compliant": True,
            "errors": [],
            "warnings": [],
            "checks": {},
        }

        # Check title
        title_check = self._check_title(manuscript.title)
        compliance_results["checks"]["title"] = title_check
        if not title_check["passed"]:
            compliance_results["errors"].extend(title_check["errors"])
            compliance_results["is_compliant"] = False

        # Check abstract
        abstract_check = self._check_abstract(manuscript.abstract)
        compliance_results["checks"]["abstract"] = abstract_check
        if not abstract_check["passed"]:
            compliance_results["errors"].extend(abstract_check["errors"])
            compliance_results["is_compliant"] = False

        # Check LaTeX structure
        latex_check = self._check_latex_structure(latex_content)
        compliance_results["checks"]["latex"] = latex_check
        if not latex_check["passed"]:
            compliance_results["errors"].extend(latex_check["errors"])
            compliance_results["is_compliant"] = False

        # Check categories
        category_check = self._check_categories(manuscript)
        compliance_results["checks"]["categories"] = category_check
        if not category_check["passed"]:
            compliance_results["errors"].extend(category_check["errors"])
            compliance_results["is_compliant"] = False

        return compliance_results

    def _check_title(self, title: str) -> Dict:
        """Check title compliance."""
        errors = []
        warnings = []

        if not title or not title.strip():
            errors.append("Title is required")
        elif len(title) > self.max_title_length:
            errors.append(
                f"Title exceeds maximum length of {self.max_title_length} characters"
            )

        if title and len(title) < 10:
            warnings.append("Title is very short")

        return {"passed": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _check_abstract(self, abstract: str) -> Dict:
        """Check abstract compliance."""
        errors = []
        warnings = []

        if not abstract or not abstract.strip():
            errors.append("Abstract is required")
        else:
            if len(abstract) > self.max_abstract_length:
                errors.append(
                    f"Abstract exceeds maximum length of {self.max_abstract_length} characters"
                )
            elif len(abstract) < self.min_abstract_length:
                warnings.append(
                    f"Abstract is shorter than recommended minimum of {self.min_abstract_length} characters"
                )

        return {"passed": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _check_latex_structure(self, latex_content: str) -> Dict:
        """Check LaTeX structure compliance."""
        errors = []
        warnings = []

        # Check for document class
        if not re.search(r"\\documentclass", latex_content):
            errors.append("Missing \\documentclass declaration")

        # Check for document environment
        if not re.search(r"\\begin\{document\}", latex_content):
            errors.append("Missing \\begin{document}")
        if not re.search(r"\\end\{document\}", latex_content):
            errors.append("Missing \\end{document}")

        # Check for title and author
        if not re.search(r"\\title\{", latex_content):
            warnings.append("Missing \\title command")
        if not re.search(r"\\author\{", latex_content):
            warnings.append("Missing \\author command")

        return {"passed": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _check_categories(self, manuscript: Manuscript) -> Dict:
        """Check category requirements."""
        errors = []
        warnings = []

        # This would check if the manuscript has arXiv submissions with categories
        # For now, just return a basic check
        if (
            not hasattr(manuscript, "arxiv_submissions")
            or not manuscript.arxiv_submissions.exists()
        ):
            warnings.append("No arXiv category selected")

        return {"passed": len(errors) == 0, "errors": errors, "warnings": warnings}
