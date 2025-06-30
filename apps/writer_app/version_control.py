"""
Version Control System for SciTeX Writer
Advanced diff generation, branching, and merge capabilities for manuscript management.
"""
import difflib
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from django.utils import timezone
from django.contrib.auth.models import User
from .models import (
    Manuscript, ManuscriptVersion, ManuscriptBranch, 
    DiffResult, MergeRequest, ManuscriptSection
)


class DiffEngine:
    """Advanced diff generation for manuscript content."""
    
    def __init__(self):
        self.word_pattern = re.compile(r'\b\w+\b|[^\w\s]')
        self.sentence_pattern = re.compile(r'[.!?]+')
        
    def generate_unified_diff(self, text1: str, text2: str, 
                           context_lines: int = 3) -> Dict[str, Any]:
        """Generate unified diff between two text versions."""
        lines1 = text1.splitlines(keepends=True)
        lines2 = text2.splitlines(keepends=True)
        
        diff = list(difflib.unified_diff(
            lines1, lines2,
            fromfile='Version A',
            tofile='Version B',
            n=context_lines
        ))
        
        # Parse diff into structured format
        changes = []
        current_hunk = None
        
        for line in diff:
            if line.startswith('@@'):
                if current_hunk:
                    changes.append(current_hunk)
                current_hunk = {
                    'header': line.strip(),
                    'lines': []
                }
            elif current_hunk and (line.startswith(' ') or line.startswith('+') or line.startswith('-')):
                change_type = 'context' if line.startswith(' ') else ('addition' if line.startswith('+') else 'deletion')
                current_hunk['lines'].append({
                    'type': change_type,
                    'content': line[1:],
                    'line_number': len(current_hunk['lines']) + 1
                })
        
        if current_hunk:
            changes.append(current_hunk)
        
        return {
            'type': 'unified',
            'changes': changes,
            'raw_diff': ''.join(diff),
            'stats': self._calculate_diff_stats(diff)
        }
    
    def generate_side_by_side_diff(self, text1: str, text2: str) -> Dict[str, Any]:
        """Generate side-by-side diff visualization."""
        lines1 = text1.splitlines()
        lines2 = text2.splitlines()
        
        # Use difflib.HtmlDiff for side-by-side comparison
        html_diff = difflib.HtmlDiff(wrapcolumn=80)
        html_content = html_diff.make_table(
            lines1, lines2,
            fromdesc='Previous Version',
            todesc='Current Version',
            context=True,
            numlines=3
        )
        
        # Parse changes for structured data
        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        changes = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                continue
            elif tag == 'replace':
                changes.append({
                    'type': 'replace',
                    'old_start': i1 + 1,
                    'old_end': i2,
                    'new_start': j1 + 1,
                    'new_end': j2,
                    'old_lines': lines1[i1:i2],
                    'new_lines': lines2[j1:j2]
                })
            elif tag == 'delete':
                changes.append({
                    'type': 'delete',
                    'old_start': i1 + 1,
                    'old_end': i2,
                    'lines': lines1[i1:i2]
                })
            elif tag == 'insert':
                changes.append({
                    'type': 'insert',
                    'new_start': j1 + 1,
                    'new_end': j2,
                    'lines': lines2[j1:j2]
                })
        
        return {
            'type': 'side_by_side',
            'html': html_content,
            'changes': changes,
            'stats': self._calculate_change_stats(changes)
        }
    
    def generate_word_level_diff(self, text1: str, text2: str) -> Dict[str, Any]:
        """Generate word-level diff for precise change tracking."""
        words1 = self.word_pattern.findall(text1)
        words2 = self.word_pattern.findall(text2)
        
        matcher = difflib.SequenceMatcher(None, words1, words2)
        changes = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                changes.append({
                    'type': 'equal',
                    'words': words1[i1:i2]
                })
            elif tag == 'replace':
                changes.append({
                    'type': 'replace',
                    'old_words': words1[i1:i2],
                    'new_words': words2[j1:j2]
                })
            elif tag == 'delete':
                changes.append({
                    'type': 'delete',
                    'words': words1[i1:i2]
                })
            elif tag == 'insert':
                changes.append({
                    'type': 'insert',
                    'words': words2[j1:j2]
                })
        
        return {
            'type': 'word_level',
            'changes': changes,
            'stats': {
                'words_added': sum(len(c.get('words', c.get('new_words', []))) 
                                 for c in changes if c['type'] in ['insert', 'replace']),
                'words_removed': sum(len(c.get('words', c.get('old_words', []))) 
                                   for c in changes if c['type'] in ['delete', 'replace']),
                'words_unchanged': sum(len(c['words']) for c in changes if c['type'] == 'equal')
            }
        }
    
    def generate_semantic_diff(self, text1: str, text2: str) -> Dict[str, Any]:
        """Generate semantic diff focusing on meaningful changes."""
        # Split into sentences for semantic analysis
        sentences1 = self.sentence_pattern.split(text1)
        sentences2 = self.sentence_pattern.split(text2)
        
        # Clean empty sentences
        sentences1 = [s.strip() for s in sentences1 if s.strip()]
        sentences2 = [s.strip() for s in sentences2 if s.strip()]
        
        matcher = difflib.SequenceMatcher(None, sentences1, sentences2)
        semantic_changes = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                continue
            
            change = {
                'type': tag,
                'severity': self._assess_change_severity(
                    sentences1[i1:i2] if tag in ['delete', 'replace'] else [],
                    sentences2[j1:j2] if tag in ['insert', 'replace'] else []
                )
            }
            
            if tag == 'replace':
                change.update({
                    'old_sentences': sentences1[i1:i2],
                    'new_sentences': sentences2[j1:j2],
                    'description': self._describe_change(sentences1[i1:i2], sentences2[j1:j2])
                })
            elif tag == 'delete':
                change.update({
                    'sentences': sentences1[i1:i2],
                    'description': f"Removed {len(sentences1[i1:i2])} sentence(s)"
                })
            elif tag == 'insert':
                change.update({
                    'sentences': sentences2[j1:j2],
                    'description': f"Added {len(sentences2[j1:j2])} sentence(s)"
                })
            
            semantic_changes.append(change)
        
        return {
            'type': 'semantic',
            'changes': semantic_changes,
            'stats': {
                'major_changes': len([c for c in semantic_changes if c['severity'] == 'major']),
                'minor_changes': len([c for c in semantic_changes if c['severity'] == 'minor']),
                'total_changes': len(semantic_changes)
            }
        }
    
    def _calculate_diff_stats(self, diff_lines: List[str]) -> Dict[str, int]:
        """Calculate statistics from unified diff."""
        additions = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
        deletions = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
        
        return {
            'additions': additions,
            'deletions': deletions,
            'changes': additions + deletions
        }
    
    def _calculate_change_stats(self, changes: List[Dict]) -> Dict[str, int]:
        """Calculate statistics from structured changes."""
        additions = sum(len(c.get('lines', c.get('new_lines', []))) 
                       for c in changes if c['type'] in ['insert', 'replace'])
        deletions = sum(len(c.get('lines', c.get('old_lines', []))) 
                       for c in changes if c['type'] in ['delete', 'replace'])
        
        return {
            'additions': additions,
            'deletions': deletions,
            'changes': len(changes)
        }
    
    def _assess_change_severity(self, old_sentences: List[str], 
                              new_sentences: List[str]) -> str:
        """Assess the severity of semantic changes."""
        # Simple heuristic: length difference and word overlap
        old_text = ' '.join(old_sentences)
        new_text = ' '.join(new_sentences)
        
        length_ratio = abs(len(new_text) - len(old_text)) / max(len(old_text), len(new_text), 1)
        
        if length_ratio > 0.5:
            return 'major'
        elif length_ratio > 0.2:
            return 'moderate'
        else:
            return 'minor'
    
    def _describe_change(self, old_sentences: List[str], 
                        new_sentences: List[str]) -> str:
        """Generate human-readable description of changes."""
        if not old_sentences:
            return f"Added {len(new_sentences)} new sentence(s)"
        elif not new_sentences:
            return f"Removed {len(old_sentences)} sentence(s)"
        else:
            return f"Modified {len(old_sentences)} sentence(s) to {len(new_sentences)} sentence(s)"


class VersionControlManager:
    """Manage manuscript versions, branches, and merges."""
    
    def __init__(self):
        self.diff_engine = DiffEngine()
    
    def create_version(self, manuscript: Manuscript, user: User, 
                      commit_message: str = "", version_tag: str = "",
                      branch_name: str = "main", is_major: bool = False) -> ManuscriptVersion:
        """Create a new version of the manuscript."""
        
        # Generate version number
        latest_version = manuscript.versions.filter(branch_name=branch_name).first()
        if latest_version:
            # Parse version number and increment
            version_parts = latest_version.version_number.split('.')
            if is_major:
                version_number = f"{int(version_parts[0]) + 1}.0"
            else:
                minor = int(version_parts[1]) if len(version_parts) > 1 else 0
                version_number = f"{version_parts[0]}.{minor + 1}"
        else:
            version_number = "1.0" if is_major else "0.1"
        
        # Collect current manuscript state
        sections = manuscript.sections.all()
        section_contents = {}
        total_word_count = 0
        
        for section in sections:
            section_contents[section.section_type] = {
                'title': section.title,
                'content': section.content,
                'word_count': len(section.content.split()),
                'order': section.order
            }
            total_word_count += len(section.content.split())
        
        manuscript_data = {
            'title': manuscript.title,
            'abstract': manuscript.abstract,
            'status': manuscript.status,
            'target_journal': manuscript.target_journal,
            'keywords': manuscript.keywords,
            'word_count_total': total_word_count,
            'created_at': manuscript.created_at.isoformat(),
            'updated_at': manuscript.updated_at.isoformat()
        }
        
        # Calculate changes from previous version
        changes_count = 0
        word_delta = 0
        lines_added = 0
        lines_removed = 0
        
        if latest_version:
            # Calculate diff statistics
            old_content = self._reconstruct_content(latest_version.section_contents)
            new_content = self._reconstruct_content(section_contents)
            
            diff_result = self.diff_engine.generate_unified_diff(old_content, new_content)
            changes_count = len(diff_result['changes'])
            word_delta = total_word_count - latest_version.manuscript_data.get('word_count_total', 0)
            lines_added = diff_result['stats']['additions']
            lines_removed = diff_result['stats']['deletions']
        
        # Create version
        version = ManuscriptVersion.objects.create(
            manuscript=manuscript,
            version_number=version_number,
            version_tag=version_tag,
            branch_name=branch_name,
            created_by=user,
            commit_message=commit_message,
            manuscript_data=manuscript_data,
            section_contents=section_contents,
            parent_version=latest_version,
            is_major_version=is_major,
            total_changes=changes_count,
            word_count_delta=word_delta,
            lines_added=lines_added,
            lines_removed=lines_removed
        )
        
        # Update manuscript version counter
        manuscript.version += 1
        manuscript.save()
        
        return version
    
    def create_branch(self, manuscript: Manuscript, branch_name: str, 
                     description: str, user: User, 
                     base_version: Optional[ManuscriptVersion] = None) -> ManuscriptBranch:
        """Create a new branch from base version."""
        
        if not base_version:
            base_version = manuscript.versions.filter(branch_name='main').first()
        
        branch = ManuscriptBranch.objects.create(
            manuscript=manuscript,
            name=branch_name,
            description=description,
            created_by=user,
            base_version=base_version
        )
        
        # Create initial version in new branch
        if base_version:
            self.create_version(
                manuscript=manuscript,
                user=user,
                commit_message=f"Created branch '{branch_name}' from {base_version.version_number}",
                branch_name=branch_name
            )
        
        return branch
    
    def generate_diff(self, from_version: ManuscriptVersion, 
                     to_version: ManuscriptVersion, 
                     diff_type: str = 'unified') -> DiffResult:
        """Generate diff between two versions."""
        
        # Check for cached diff
        cached_diff = DiffResult.objects.filter(
            from_version=from_version,
            to_version=to_version,
            diff_type=diff_type
        ).first()
        
        if cached_diff and cached_diff.is_valid_cache():
            return cached_diff
        
        # Generate new diff
        from_content = self._reconstruct_content(from_version.section_contents)
        to_content = self._reconstruct_content(to_version.section_contents)
        
        if diff_type == 'unified':
            diff_data = self.diff_engine.generate_unified_diff(from_content, to_content)
        elif diff_type == 'side_by_side':
            diff_data = self.diff_engine.generate_side_by_side_diff(from_content, to_content)
        elif diff_type == 'word_level':
            diff_data = self.diff_engine.generate_word_level_diff(from_content, to_content)
        elif diff_type == 'semantic':
            diff_data = self.diff_engine.generate_semantic_diff(from_content, to_content)
        else:
            raise ValueError(f"Unsupported diff type: {diff_type}")
        
        # Generate HTML representation
        diff_html = self._generate_diff_html(diff_data)
        
        # Cache the result
        cache_expires = timezone.now() + timedelta(hours=24)
        
        diff_result = DiffResult.objects.create(
            manuscript=from_version.manuscript,
            from_version=from_version,
            to_version=to_version,
            diff_type=diff_type,
            diff_data=diff_data,
            diff_html=diff_html,
            diff_stats=diff_data.get('stats', {}),
            cache_expires=cache_expires
        )
        
        return diff_result
    
    def create_merge_request(self, source_branch: ManuscriptBranch,
                           target_branch: ManuscriptBranch,
                           title: str, description: str, 
                           user: User) -> MergeRequest:
        """Create a merge request between branches."""
        
        source_version = source_branch.get_latest_version()
        target_version = target_branch.get_latest_version()
        
        if not source_version or not target_version:
            raise ValueError("Both branches must have at least one version")
        
        # Check for conflicts
        has_conflicts, conflict_data = self._check_merge_conflicts(source_version, target_version)
        
        merge_request = MergeRequest.objects.create(
            manuscript=source_branch.manuscript,
            title=title,
            description=description,
            source_branch=source_branch,
            target_branch=target_branch,
            source_version=source_version,
            target_version=target_version,
            created_by=user,
            has_conflicts=has_conflicts,
            conflict_data=conflict_data,
            auto_mergeable=not has_conflicts
        )
        
        return merge_request
    
    def merge_branches(self, merge_request: MergeRequest, 
                      user: User) -> ManuscriptVersion:
        """Merge source branch into target branch."""
        
        if not merge_request.can_auto_merge():
            raise ValueError("Merge request cannot be auto-merged due to conflicts")
        
        # Create merge commit
        merge_version = self.create_version(
            manuscript=merge_request.manuscript,
            user=user,
            commit_message=f"Merge '{merge_request.source_branch.name}' into '{merge_request.target_branch.name}'",
            branch_name=merge_request.target_branch.name,
            is_major=False
        )
        
        # Update merge request
        merge_request.status = 'merged'
        merge_request.merged_at = timezone.now()
        merge_request.merged_by = user
        merge_request.merge_commit = merge_version
        merge_request.save()
        
        # Update source branch
        merge_request.source_branch.is_merged = True
        merge_request.source_branch.merged_at = timezone.now()
        merge_request.source_branch.merged_by = user
        merge_request.source_branch.save()
        
        return merge_version
    
    def rollback_to_version(self, manuscript: Manuscript, 
                           target_version: ManuscriptVersion, 
                           user: User) -> ManuscriptVersion:
        """Rollback manuscript to a specific version."""
        
        # Create rollback version with target content
        rollback_version = ManuscriptVersion.objects.create(
            manuscript=manuscript,
            version_number=f"{target_version.version_number}-rollback",
            version_tag=f"Rollback to {target_version.version_number}",
            branch_name=target_version.branch_name,
            created_by=user,
            commit_message=f"Rollback to version {target_version.version_number}",
            manuscript_data=target_version.manuscript_data,
            section_contents=target_version.section_contents,
            parent_version=manuscript.versions.first()
        )
        
        # Update manuscript sections with rollback content
        for section_type, section_data in target_version.section_contents.items():
            section, created = manuscript.sections.get_or_create(
                section_type=section_type,
                defaults={
                    'title': section_data['title'],
                    'content': section_data['content'],
                    'order': section_data['order']
                }
            )
            if not created:
                section.title = section_data['title']
                section.content = section_data['content']
                section.order = section_data['order']
                section.save()
        
        return rollback_version
    
    def _reconstruct_content(self, section_contents: Dict) -> str:
        """Reconstruct full content from section contents."""
        content_parts = []
        
        # Sort sections by order
        sorted_sections = sorted(
            section_contents.items(),
            key=lambda x: x[1].get('order', 0)
        )
        
        for section_type, section_data in sorted_sections:
            content_parts.append(f"# {section_data['title']}\n")
            content_parts.append(section_data['content'])
            content_parts.append("\n\n")
        
        return ''.join(content_parts)
    
    def _generate_diff_html(self, diff_data: Dict) -> str:
        """Generate HTML representation of diff data."""
        if diff_data['type'] == 'side_by_side':
            return diff_data.get('html', '')
        
        # Generate simple HTML for other diff types
        html_parts = ['<div class="diff-container">']
        
        if diff_data['type'] == 'unified':
            for change in diff_data['changes']:
                html_parts.append('<div class="diff-hunk">')
                html_parts.append(f'<div class="diff-header">{change["header"]}</div>')
                
                for line in change['lines']:
                    css_class = f"diff-{line['type']}"
                    html_parts.append(f'<div class="{css_class}">{line["content"]}</div>')
                
                html_parts.append('</div>')
        
        elif diff_data['type'] == 'word_level':
            for change in diff_data['changes']:
                if change['type'] == 'equal':
                    html_parts.append(f'<span class="diff-equal">{" ".join(change["words"])}</span>')
                elif change['type'] == 'insert':
                    html_parts.append(f'<span class="diff-insert">{" ".join(change["words"])}</span>')
                elif change['type'] == 'delete':
                    html_parts.append(f'<span class="diff-delete">{" ".join(change["words"])}</span>')
                elif change['type'] == 'replace':
                    html_parts.append(f'<span class="diff-delete">{" ".join(change["old_words"])}</span>')
                    html_parts.append(f'<span class="diff-insert">{" ".join(change["new_words"])}</span>')
        
        html_parts.append('</div>')
        return ''.join(html_parts)
    
    def _check_merge_conflicts(self, source_version: ManuscriptVersion,
                             target_version: ManuscriptVersion) -> Tuple[bool, Dict]:
        """Check for merge conflicts between versions."""
        
        # Simple conflict detection based on section modifications
        conflicts = []
        source_sections = source_version.section_contents
        target_sections = target_version.section_contents
        
        for section_type in set(source_sections.keys()) | set(target_sections.keys()):
            source_content = source_sections.get(section_type, {}).get('content', '')
            target_content = target_sections.get(section_type, {}).get('content', '')
            
            if source_content != target_content:
                # Check if both branches modified the same section
                base_version = source_version.parent_version
                if base_version:
                    base_content = base_version.section_contents.get(section_type, {}).get('content', '')
                    
                    if (source_content != base_content and 
                        target_content != base_content and 
                        source_content != target_content):
                        conflicts.append({
                            'section': section_type,
                            'type': 'content_conflict',
                            'source_content': source_content,
                            'target_content': target_content,
                            'base_content': base_content
                        })
        
        return len(conflicts) > 0, {'conflicts': conflicts}