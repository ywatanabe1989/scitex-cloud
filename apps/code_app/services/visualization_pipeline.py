#!/usr/bin/env python3
"""
Data Visualization Pipeline for SciTeX-Code
Integrates with Viz Module for publication-ready figure generation.
"""

import json
import uuid
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

from ..models import CodeExecutionJob

logger = logging.getLogger(__name__)


class VisualizationGenerator:
    """Generates publication-ready visualizations from data."""
    
    def __init__(self, user: User):
        self.user = user
        self.output_dir = Path(settings.MEDIA_ROOT) / 'visualizations' / str(user.id)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set publication-ready defaults
        self._setup_matplotlib_style()
    
    def _setup_matplotlib_style(self):
        """Configure matplotlib for publication-ready plots."""
        plt.rcParams.update({
            'figure.figsize': (10, 6),
            'figure.dpi': 300,
            'savefig.dpi': 300,
            'savefig.bbox': 'tight',
            'savefig.pad_inches': 0.1,
            'font.family': 'serif',
            'font.serif': ['Times', 'Times New Roman', 'DejaVu Serif'],
            'font.size': 12,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'axes.linewidth': 1.2,
            'axes.spines.top': False,
            'axes.spines.right': False,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
            'legend.frameon': False,
            'grid.alpha': 0.3,
            'lines.linewidth': 2,
            'lines.markersize': 8
        })
        
        # Set color palette
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                 '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)
    
    def generate_plot(self, plot_type: str, data: Dict[str, Any], 
                     options: Dict[str, Any] = None) -> Tuple[bool, Dict[str, Any]]:
        """Generate a plot based on type and data."""
        options = options or {}
        
        try:
            if plot_type == 'line':
                return self._generate_line_plot(data, options)
            elif plot_type == 'scatter':
                return self._generate_scatter_plot(data, options)
            elif plot_type == 'bar':
                return self._generate_bar_plot(data, options)
            elif plot_type == 'histogram':
                return self._generate_histogram(data, options)
            elif plot_type == 'boxplot':
                return self._generate_boxplot(data, options)
            elif plot_type == 'heatmap':
                return self._generate_heatmap(data, options)
            elif plot_type == 'violin':
                return self._generate_violin_plot(data, options)
            elif plot_type == 'pair':
                return self._generate_pair_plot(data, options)
            else:
                return False, {'error': f'Unsupported plot type: {plot_type}'}
                
        except Exception as e:
            logger.error(f"Error generating {plot_type} plot: {e}")
            return False, {'error': str(e)}
    
    def _generate_line_plot(self, data: Dict[str, Any], options: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Generate a line plot."""
        fig, ax = plt.subplots(figsize=options.get('figsize', (10, 6)))
        
        x_data = data.get('x', [])
        y_data = data.get('y', [])
        
        if not x_data or not y_data:
            return False, {'error': 'x and y data are required for line plot'}
        
        # Multiple series support
        if isinstance(y_data[0], list):
            for i, y_series in enumerate(y_data):
                label = data.get('labels', [f'Series {i+1}'])[i] if i < len(data.get('labels', [])) else f'Series {i+1}'
                ax.plot(x_data, y_series, label=label, linewidth=options.get('linewidth', 2))
            ax.legend()
        else:
            ax.plot(x_data, y_data, linewidth=options.get('linewidth', 2))
        
        ax.set_xlabel(options.get('xlabel', 'X'))
        ax.set_ylabel(options.get('ylabel', 'Y'))
        ax.set_title(options.get('title', 'Line Plot'))
        
        if options.get('grid', True):
            ax.grid(True, alpha=0.3)
        
        filename = self._save_figure(fig, 'line_plot')
        plt.close(fig)
        
        return True, {
            'filename': filename,
            'plot_type': 'line',
            'data_points': len(x_data)
        }
    
    def _generate_scatter_plot(self, data: Dict[str, Any], options: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Generate a scatter plot."""
        fig, ax = plt.subplots(figsize=options.get('figsize', (10, 6)))
        
        x_data = data.get('x', [])
        y_data = data.get('y', [])
        
        if not x_data or not y_data:
            return False, {'error': 'x and y data are required for scatter plot'}
        
        # Color and size support
        c = data.get('color', None)
        s = data.get('size', options.get('markersize', 50))
        
        scatter = ax.scatter(x_data, y_data, c=c, s=s, alpha=options.get('alpha', 0.7))
        
        # Add colorbar if color data provided
        if c is not None:
            plt.colorbar(scatter, ax=ax, label=options.get('color_label', 'Color'))
        
        ax.set_xlabel(options.get('xlabel', 'X'))
        ax.set_ylabel(options.get('ylabel', 'Y'))
        ax.set_title(options.get('title', 'Scatter Plot'))
        
        if options.get('grid', True):
            ax.grid(True, alpha=0.3)
        
        filename = self._save_figure(fig, 'scatter_plot')
        plt.close(fig)
        
        return True, {
            'filename': filename,
            'plot_type': 'scatter',
            'data_points': len(x_data)
        }
    
    def _generate_bar_plot(self, data: Dict[str, Any], options: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Generate a bar plot."""
        fig, ax = plt.subplots(figsize=options.get('figsize', (10, 6)))
        
        categories = data.get('categories', [])
        values = data.get('values', [])
        
        if not categories or not values:
            return False, {'error': 'categories and values are required for bar plot'}
        
        bars = ax.bar(categories, values, color=options.get('color', None))
        
        ax.set_xlabel(options.get('xlabel', 'Categories'))
        ax.set_ylabel(options.get('ylabel', 'Values'))
        ax.set_title(options.get('title', 'Bar Plot'))
        
        # Rotate labels if too many categories
        if len(categories) > 10:
            plt.xticks(rotation=45, ha='right')
        
        # Add value labels on bars if requested
        if options.get('show_values', False):
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}', ha='center', va='bottom')
        
        filename = self._save_figure(fig, 'bar_plot')
        plt.close(fig)
        
        return True, {
            'filename': filename,
            'plot_type': 'bar',
            'categories': len(categories)
        }
    
    def _generate_histogram(self, data: Dict[str, Any], options: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Generate a histogram."""
        fig, ax = plt.subplots(figsize=options.get('figsize', (10, 6)))
        
        values = data.get('values', [])
        
        if not values:
            return False, {'error': 'values are required for histogram'}
        
        bins = options.get('bins', 'auto')
        alpha = options.get('alpha', 0.7)
        
        n, bins, patches = ax.hist(values, bins=bins, alpha=alpha, edgecolor='black')
        
        ax.set_xlabel(options.get('xlabel', 'Values'))
        ax.set_ylabel(options.get('ylabel', 'Frequency'))
        ax.set_title(options.get('title', 'Histogram'))
        
        # Add statistics
        if options.get('show_stats', True):
            mean_val = np.mean(values)
            std_val = np.std(values)
            ax.axvline(mean_val, color='red', linestyle='--', label=f'Mean: {mean_val:.2f}')
            ax.legend()
        
        filename = self._save_figure(fig, 'histogram')
        plt.close(fig)
        
        return True, {
            'filename': filename,
            'plot_type': 'histogram',
            'data_points': len(values),
            'bins_count': len(bins) - 1
        }
    
    def _generate_boxplot(self, data: Dict[str, Any], options: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Generate a boxplot."""
        fig, ax = plt.subplots(figsize=options.get('figsize', (10, 6)))
        
        values = data.get('values', [])
        labels = data.get('labels', None)
        
        if not values:
            return False, {'error': 'values are required for boxplot'}
        
        bp = ax.boxplot(values, labels=labels, patch_artist=True)
        
        # Color the boxes
        colors = plt.cm.Set3(np.linspace(0, 1, len(values)))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
        
        ax.set_ylabel(options.get('ylabel', 'Values'))
        ax.set_title(options.get('title', 'Box Plot'))
        
        if options.get('grid', True):
            ax.grid(True, alpha=0.3)
        
        filename = self._save_figure(fig, 'boxplot')
        plt.close(fig)
        
        return True, {
            'filename': filename,
            'plot_type': 'boxplot',
            'groups': len(values)
        }
    
    def _generate_heatmap(self, data: Dict[str, Any], options: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Generate a heatmap."""
        fig, ax = plt.subplots(figsize=options.get('figsize', (10, 8)))
        
        matrix = data.get('matrix', [])
        
        if not matrix:
            return False, {'error': 'matrix data is required for heatmap'}
        
        # Convert to numpy array if needed
        if isinstance(matrix, list):
            matrix = np.array(matrix)
        
        cmap = options.get('cmap', 'viridis')
        annot = options.get('annotate', True)
        
        sns.heatmap(matrix, annot=annot, cmap=cmap, ax=ax,
                   xticklabels=data.get('x_labels', True),
                   yticklabels=data.get('y_labels', True))
        
        ax.set_title(options.get('title', 'Heatmap'))
        
        filename = self._save_figure(fig, 'heatmap')
        plt.close(fig)
        
        return True, {
            'filename': filename,
            'plot_type': 'heatmap',
            'shape': matrix.shape
        }
    
    def _generate_violin_plot(self, data: Dict[str, Any], options: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Generate a violin plot."""
        fig, ax = plt.subplots(figsize=options.get('figsize', (10, 6)))
        
        values = data.get('values', [])
        labels = data.get('labels', None)
        
        if not values:
            return False, {'error': 'values are required for violin plot'}
        
        vp = ax.violinplot(values, showmeans=True, showmedians=True)
        
        if labels:
            ax.set_xticks(range(1, len(labels) + 1))
            ax.set_xticklabels(labels)
        
        ax.set_ylabel(options.get('ylabel', 'Values'))
        ax.set_title(options.get('title', 'Violin Plot'))
        
        if options.get('grid', True):
            ax.grid(True, alpha=0.3)
        
        filename = self._save_figure(fig, 'violin_plot')
        plt.close(fig)
        
        return True, {
            'filename': filename,
            'plot_type': 'violin',
            'groups': len(values)
        }
    
    def _generate_pair_plot(self, data: Dict[str, Any], options: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Generate a pair plot."""
        try:
            # Create DataFrame from data
            df_data = data.get('dataframe', {})
            if not df_data:
                return False, {'error': 'dataframe data is required for pair plot'}
            
            df = pd.DataFrame(df_data)
            
            # Create pair plot
            g = sns.pairplot(df, hue=options.get('hue', None), 
                           diag_kind=options.get('diag_kind', 'hist'))
            
            g.fig.suptitle(options.get('title', 'Pair Plot'), y=1.02)
            
            filename = self._save_figure(g.fig, 'pair_plot')
            plt.close(g.fig)
            
            return True, {
                'filename': filename,
                'plot_type': 'pair',
                'variables': len(df.columns)
            }
            
        except Exception as e:
            return False, {'error': f'Error creating pair plot: {e}'}
    
    def _save_figure(self, fig, plot_type: str) -> str:
        """Save figure to file and return filename."""
        filename = f"{plot_type}_{uuid.uuid4().hex[:8]}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        
        fig.savefig(filepath, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        
        logger.info(f"Saved visualization: {filepath}")
        return filename
    
    def generate_publication_figure(self, plot_configs: List[Dict[str, Any]], 
                                   layout: str = 'single') -> Tuple[bool, Dict[str, Any]]:
        """Generate publication-ready multi-panel figure."""
        try:
            if layout == 'single':
                # Single plot
                if len(plot_configs) != 1:
                    return False, {'error': 'Single layout requires exactly one plot config'}
                
                return self.generate_plot(
                    plot_configs[0]['type'],
                    plot_configs[0]['data'],
                    plot_configs[0].get('options', {})
                )
            
            elif layout == 'horizontal':
                # Horizontal subplot layout
                fig, axes = plt.subplots(1, len(plot_configs), 
                                       figsize=(5 * len(plot_configs), 5))
                if len(plot_configs) == 1:
                    axes = [axes]
                
                filenames = []
                for i, config in enumerate(plot_configs):
                    plt.sca(axes[i])
                    success, result = self._generate_subplot(config, axes[i])
                    if not success:
                        plt.close(fig)
                        return False, result
                
                plt.tight_layout()
                filename = self._save_figure(fig, 'multi_horizontal')
                plt.close(fig)
                
                return True, {
                    'filename': filename,
                    'plot_type': 'multi_horizontal',
                    'subplot_count': len(plot_configs)
                }
            
            elif layout == 'vertical':
                # Vertical subplot layout
                fig, axes = plt.subplots(len(plot_configs), 1, 
                                       figsize=(8, 4 * len(plot_configs)))
                if len(plot_configs) == 1:
                    axes = [axes]
                
                for i, config in enumerate(plot_configs):
                    plt.sca(axes[i])
                    success, result = self._generate_subplot(config, axes[i])
                    if not success:
                        plt.close(fig)
                        return False, result
                
                plt.tight_layout()
                filename = self._save_figure(fig, 'multi_vertical')
                plt.close(fig)
                
                return True, {
                    'filename': filename,
                    'plot_type': 'multi_vertical',
                    'subplot_count': len(plot_configs)
                }
            
            else:
                return False, {'error': f'Unsupported layout: {layout}'}
                
        except Exception as e:
            logger.error(f"Error generating publication figure: {e}")
            return False, {'error': str(e)}
    
    def _generate_subplot(self, config: Dict[str, Any], ax) -> Tuple[bool, Dict[str, Any]]:
        """Generate a subplot on the given axes."""
        plot_type = config['type']
        data = config['data']
        options = config.get('options', {})
        
        try:
            # Simple subplot generation - can be expanded
            if plot_type == 'line':
                x_data = data.get('x', [])
                y_data = data.get('y', [])
                ax.plot(x_data, y_data)
                ax.set_xlabel(options.get('xlabel', 'X'))
                ax.set_ylabel(options.get('ylabel', 'Y'))
                ax.set_title(options.get('title', ''))
                
            elif plot_type == 'scatter':
                x_data = data.get('x', [])
                y_data = data.get('y', [])
                ax.scatter(x_data, y_data)
                ax.set_xlabel(options.get('xlabel', 'X'))
                ax.set_ylabel(options.get('ylabel', 'Y'))
                ax.set_title(options.get('title', ''))
                
            elif plot_type == 'bar':
                categories = data.get('categories', [])
                values = data.get('values', [])
                ax.bar(categories, values)
                ax.set_xlabel(options.get('xlabel', 'Categories'))
                ax.set_ylabel(options.get('ylabel', 'Values'))
                ax.set_title(options.get('title', ''))
                
            else:
                return False, {'error': f'Subplot type {plot_type} not supported'}
            
            if options.get('grid', True):
                ax.grid(True, alpha=0.3)
            
            return True, {'success': True}
            
        except Exception as e:
            return False, {'error': str(e)}


class VisualizationPipeline:
    """Orchestrates data visualization workflows."""
    
    def __init__(self, user: User):
        self.user = user
        self.generator = VisualizationGenerator(user)
    
    def process_data_and_visualize(self, data_source: str, 
                                 visualization_specs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process data and generate visualizations."""
        try:
            # Load data (simplified - could support multiple formats)
            if data_source.endswith('.csv'):
                df = pd.read_csv(data_source)
            elif data_source.endswith('.json'):
                with open(data_source) as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
            else:
                return {'error': 'Unsupported data format'}
            
            results = []
            
            for spec in visualization_specs:
                plot_type = spec['type']
                
                # Extract data based on specification
                if plot_type in ['line', 'scatter']:
                    x_col = spec.get('x_column')
                    y_col = spec.get('y_column')
                    
                    if x_col not in df.columns or y_col not in df.columns:
                        results.append({'error': f'Columns {x_col}, {y_col} not found'})
                        continue
                    
                    plot_data = {
                        'x': df[x_col].tolist(),
                        'y': df[y_col].tolist()
                    }
                    
                elif plot_type == 'histogram':
                    col = spec.get('column')
                    if col not in df.columns:
                        results.append({'error': f'Column {col} not found'})
                        continue
                    
                    plot_data = {'values': df[col].tolist()}
                    
                elif plot_type == 'heatmap':
                    # Correlation heatmap
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    correlation_matrix = df[numeric_cols].corr()
                    
                    plot_data = {
                        'matrix': correlation_matrix.values,
                        'x_labels': correlation_matrix.columns.tolist(),
                        'y_labels': correlation_matrix.index.tolist()
                    }
                
                else:
                    results.append({'error': f'Unsupported plot type: {plot_type}'})
                    continue
                
                # Generate visualization
                success, result = self.generator.generate_plot(
                    plot_type, plot_data, spec.get('options', {})
                )
                
                results.append(result)
            
            return {
                'success': True,
                'visualizations': results,
                'data_shape': df.shape,
                'data_columns': df.columns.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error in visualization pipeline: {e}")
            return {'error': str(e)}
    
    def create_research_report(self, title: str, sections: List[Dict[str, Any]]) -> str:
        """Create a research report with embedded visualizations."""
        from datetime import datetime
        
        report_content = f"""
# {title}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Author: {self.user.get_full_name() or self.user.username}

---

"""
        
        for section in sections:
            section_title = section.get('title', 'Untitled Section')
            section_text = section.get('text', '')
            visualizations = section.get('visualizations', [])
            
            report_content += f"## {section_title}\n\n"
            
            if section_text:
                report_content += f"{section_text}\n\n"
            
            for viz in visualizations:
                if viz.get('filename'):
                    report_content += f"![{viz.get('plot_type', 'Visualization')}](visualizations/{self.user.id}/{viz['filename']})\n\n"
                    if viz.get('caption'):
                        report_content += f"*Figure: {viz['caption']}*\n\n"
        
        # Save report
        report_dir = Path(settings.MEDIA_ROOT) / 'reports' / str(self.user.id)
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_filename = f"report_{uuid.uuid4().hex[:8]}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = report_dir / report_filename
        
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        return str(report_path)