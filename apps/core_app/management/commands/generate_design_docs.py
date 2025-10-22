"""
Generate component documentation from CSS files with @annotations.

This management command parses CSS files in static/css/common/ and static/css/components/
directories, extracts @annotation metadata, and generates a components.json file for
the programmatic design system.

Usage:
    python manage.py generate_design_docs
    python manage.py generate_design_docs --verbose
    python manage.py generate_design_docs --output path/to/output.json
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import json
import re
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Generate component documentation from CSS files with @annotations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='apps/dev_app/data/components.json',
            help='Output JSON file path (default: apps/dev_app/data/components.json)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Print detailed parsing information'
        )

    def handle(self, *args, **options):
        css_dirs = [
            'static/css/common/',
            'static/css/components/',
        ]

        components = []
        total_files = 0
        parsed_files = 0

        for css_dir in css_dirs:
            if not os.path.exists(css_dir):
                if options['verbose']:
                    self.stdout.write(
                        self.style.WARNING(f"Directory not found: {css_dir}")
                    )
                continue

            for css_file in Path(css_dir).glob('*.css'):
                total_files += 1

                if options['verbose']:
                    self.stdout.write(f"\nParsing: {css_file}")

                component = self.parse_css_file(css_file, options['verbose'])

                if component:
                    components.append(component)
                    parsed_files += 1

                    if options['verbose']:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  ✓ Extracted: {component['name']} "
                                f"({len(component.get('variants', []))} variants, "
                                f"{len(component.get('examples', []))} examples)"
                            )
                        )
                else:
                    if options['verbose']:
                        self.stdout.write(
                            self.style.WARNING("  ⚠ No @component annotation found")
                        )

        # Create output directory if it doesn't exist
        output_path = Path(options['output'])
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to JSON
        output_data = {
            'components': components,
            'metadata': {
                'total_components': len(components),
                'generated_at': self._get_timestamp(),
                'source_directories': css_dirs,
            }
        }

        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)

        # Summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Generated documentation for {parsed_files}/{total_files} CSS files"
            )
        )
        self.stdout.write(f"  Components found: {len(components)}")
        self.stdout.write(f"  Output file: {output_path}")
        self.stdout.write("="*60 + "\n")

    def parse_css_file(self, filepath, verbose=False):
        """Parse a single CSS file and extract @annotation metadata"""

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract the first multi-line comment block
        comment_pattern = r'/\*\s*\n(.*?)\*/'
        match = re.search(comment_pattern, content, re.DOTALL)

        if not match:
            return None

        comment = match.group(1)

        # Check if this is an @annotated component
        if '@component' not in comment:
            return None

        component = {
            'id': self._extract_annotation(comment, 'component', filepath.stem),
            'name': self._extract_annotation(comment, 'component', filepath.stem.title().replace('-', ' ')),
            'description': self._extract_annotation(comment, 'description', ''),
            'category': self._extract_annotation(comment, 'category', 'Other Components'),
            'css_file': f'/static/css/{filepath.relative_to("static/css")}',
            'darkmode': self._extract_darkmode(comment),
            'variants': self._extract_variants(comment, verbose),
            'states': self._extract_states(comment, verbose),
            'examples': self._extract_examples(comment, verbose),
        }

        return component

    def _extract_annotation(self, text, key, default=''):
        """Extract single-line @key value from comment"""
        pattern = rf'@{key}\s+(.+?)(?:\n|$)'
        match = re.search(pattern, text)
        return match.group(1).strip() if match else default

    def _extract_darkmode(self, text):
        """Extract @darkmode value and return boolean status.

        Only accepts 'true' or 'false' values to enforce clean binary dark mode system.
        No 'partial' dark mode - components either fully support both modes or don't.
        """
        pattern = r'@darkmode\s+(true|false)'
        match = re.search(pattern, text, re.IGNORECASE)

        if not match:
            return False

        value = match.group(1).lower()
        return value == 'true'

    def _extract_variants(self, text, verbose=False):
        """Extract @variant annotations"""
        variants = []
        pattern = r'@variant\s+([^\s-]+)\s+-\s+(.+?)(?:\n|$)'

        for match in re.finditer(pattern, text):
            variant = {
                'class_name': match.group(1).strip(),
                'description': match.group(2).strip(),
            }
            variants.append(variant)

            if verbose:
                print(f"    Found variant: {variant['class_name']}")

        return variants

    def _extract_states(self, text, verbose=False):
        """Extract @state annotations"""
        states = []
        pattern = r'@state\s+([^\s-]+)\s+-\s+(.+?)(?:\n|$)'

        for match in re.finditer(pattern, text):
            state = {
                'name': match.group(1).strip(),
                'description': match.group(2).strip(),
            }
            states.append(state)

            if verbose:
                print(f"    Found state: {state['name']}")

        return states

    def _extract_examples(self, text, verbose=False):
        """Extract @example code blocks"""
        examples = []

        # Use a more precise pattern that matches @example at the start of a comment line
        # This avoids splitting on @ symbols within the HTML content (like email addresses)
        example_pattern = r'\n\s*\*\s*@example(?:\s|$)'

        # Known annotation keywords that mark the end of an example
        annotation_keywords = ['component', 'description', 'category', 'file', 'darkmode',
                               'variant', 'state', 'example']

        # Find all @example positions
        example_matches = list(re.finditer(example_pattern, text))

        if not example_matches:
            return examples

        for i, match in enumerate(example_matches):
            start_pos = match.end()  # Start after the @example line

            # Find the end of this example
            if i + 1 < len(example_matches):
                # End at the next @example
                end_pos = example_matches[i + 1].start()
            else:
                # Look for next annotation keyword at start of line
                pattern = r'\n\s*\*\s*@(' + '|'.join(annotation_keywords) + r')(?:\s|$)'
                next_annotation = re.search(pattern, text[start_pos:])
                if next_annotation:
                    end_pos = start_pos + next_annotation.start()
                else:
                    # Find end of comment block
                    comment_end = text.find('*/', start_pos)
                    end_pos = comment_end if comment_end != -1 else len(text)

            example_block = text[start_pos:end_pos]

            # Clean up the example:
            # 1. Remove leading asterisks and spaces from each line
            # 2. Dedent the code
            lines = []
            for line in example_block.split('\n'):
                # Remove leading whitespace and asterisk
                cleaned = re.sub(r'^\s*\*\s?', '', line)
                # Stop if we hit comment end
                if '*/' in cleaned:
                    break
                if cleaned.strip():  # Only add non-empty lines
                    lines.append(cleaned)

            if lines:
                # Find minimum indentation
                min_indent = min(len(line) - len(line.lstrip()) for line in lines if line.strip())
                # Remove that indentation from all lines
                dedented = '\n'.join(line[min_indent:] if len(line) > min_indent else line for line in lines)

                example_html = dedented.strip()
                if example_html:
                    examples.append(example_html)

                    if verbose:
                        print(f"    Found example ({len(example_html)} chars)")

        return examples

    def _get_timestamp(self):
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
