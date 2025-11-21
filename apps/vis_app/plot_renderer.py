#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend Plot Renderer
Uses matplotlib/scitex.plt to render scientific plots from JSON specifications.
"""

import io
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path

# Unit conversion constants
MM_PER_INCH = 25.4
PT_PER_INCH = 72


def mm_to_inch(mm: float) -> float:
    """Convert millimeters to inches."""
    return mm / MM_PER_INCH


def mm_to_pt(mm: float) -> float:
    """Convert millimeters to points."""
    return mm * PT_PER_INCH / MM_PER_INCH


def pt_to_mm(pt: float) -> float:
    """Convert points to millimeters."""
    return pt * MM_PER_INCH / PT_PER_INCH


def apply_nature_style(fig, ax, style):
    """
    Apply Nature journal style specifications with scientific plotting defaults.

    Args:
        fig: Matplotlib figure
        ax: Matplotlib axis
        style: Style dictionary with parameters in mm/pt
    """
    # Convert mm to pt
    tick_length_pt = mm_to_pt(style.get('tick_length_mm', 0.8))
    tick_width_pt = mm_to_pt(style.get('tick_thickness_mm', 0.2))
    axis_width_pt = mm_to_pt(style.get('axis_thickness_mm', 0.2))
    trace_width_pt = mm_to_pt(style.get('trace_thickness_mm', 0.12))

    # Font sizes
    axis_font_size = style.get('axis_font_size_pt', 8)
    tick_font_size = style.get('tick_font_size_pt', 7)
    title_font_size = style.get('title_font_size_pt', 8)

    # Apply to rcParams
    plt.rcParams.update({
        'font.family': 'Arial',
        'font.size': tick_font_size,
        'axes.linewidth': axis_width_pt,
        'axes.labelsize': axis_font_size,
        'axes.titlesize': title_font_size,
        'xtick.major.size': tick_length_pt,
        'ytick.major.size': tick_length_pt,
        'xtick.major.width': tick_width_pt,
        'ytick.major.width': tick_width_pt,
        'xtick.labelsize': tick_font_size,
        'ytick.labelsize': tick_font_size,
        'lines.linewidth': trace_width_pt,
        'savefig.transparent': True,  # Transparent background by default
        'figure.facecolor': 'none',   # No figure background
        'axes.facecolor': 'none',     # No axes background
    })

    # Hide top and right spines (scientific plot style)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    return fig, ax


def render_line_plot(ax, df, plot_spec, style):
    """Render a line plot."""
    x_col = plot_spec.get('x_column', 'x')
    y_col = plot_spec.get('y_column', 'y')
    color = plot_spec.get('color', 'blue')

    x = df[x_col] if x_col in df.columns else range(len(df))
    y = df[y_col] if y_col in df.columns else df.iloc[:, 0]

    # Convert line width from mm to pt
    linewidth = mm_to_pt(style.get('trace_thickness_mm', 0.12))

    ax.plot(x, y, color=color, linewidth=linewidth)

    if plot_spec.get('xlabel'):
        ax.set_xlabel(plot_spec['xlabel'])
    if plot_spec.get('ylabel'):
        ax.set_ylabel(plot_spec['ylabel'])
    if plot_spec.get('title'):
        ax.set_title(plot_spec['title'])

    return ax


def render_scatter_plot(ax, df, plot_spec, style):
    """Render a scatter plot."""
    x_col = plot_spec.get('x_column', 'x')
    y_col = plot_spec.get('y_column', 'y')
    color = plot_spec.get('color', 'blue')

    x = df[x_col] if x_col in df.columns else range(len(df))
    y = df[y_col] if y_col in df.columns else df.iloc[:, 0]

    # Marker size in mm to pt
    marker_size_mm = style.get('dot_size_mm', 0.8)
    marker_size_pt = mm_to_pt(marker_size_mm)

    ax.scatter(x, y, color=color, s=marker_size_pt**2)

    if plot_spec.get('xlabel'):
        ax.set_xlabel(plot_spec['xlabel'])
    if plot_spec.get('ylabel'):
        ax.set_ylabel(plot_spec['ylabel'])
    if plot_spec.get('title'):
        ax.set_title(plot_spec['title'])

    return ax


def render_bar_plot(ax, df, plot_spec, style):
    """Render a bar plot."""
    x_col = plot_spec.get('x_column', 'x')
    y_col = plot_spec.get('y_column', 'y')
    color = plot_spec.get('color', 'blue')

    x = df[x_col] if x_col in df.columns else range(len(df))
    y = df[y_col] if y_col in df.columns else df.iloc[:, 0]

    # Bar width
    width = plot_spec.get('bar_width', 0.8)

    ax.bar(x, y, color=color, width=width)

    if plot_spec.get('xlabel'):
        ax.set_xlabel(plot_spec['xlabel'])
    if plot_spec.get('ylabel'):
        ax.set_ylabel(plot_spec['ylabel'])
    if plot_spec.get('title'):
        ax.set_title(plot_spec['title'])

    return ax


def render_barh_plot(ax, df, plot_spec, style):
    """Render a horizontal bar plot."""
    x_col = plot_spec.get('x_column', 'x')
    y_col = plot_spec.get('y_column', 'y')
    color = plot_spec.get('color', 'blue')

    x = df[x_col] if x_col in df.columns else range(len(df))
    y = df[y_col] if y_col in df.columns else df.iloc[:, 0]

    width = plot_spec.get('bar_width', 0.8)
    ax.barh(x, y, color=color, height=width)

    if plot_spec.get('xlabel'):
        ax.set_xlabel(plot_spec['xlabel'])
    if plot_spec.get('ylabel'):
        ax.set_ylabel(plot_spec['ylabel'])
    if plot_spec.get('title'):
        ax.set_title(plot_spec['title'])

    return ax


def render_errorbar_plot(ax, df, plot_spec, style):
    """Render an error bar plot."""
    x_col = plot_spec.get('x_column', 'x')
    y_col = plot_spec.get('y_column', 'y')
    yerr_col = plot_spec.get('yerr_column', 'yerr')
    color = plot_spec.get('color', 'blue')

    x = df[x_col] if x_col in df.columns else range(len(df))
    y = df[y_col] if y_col in df.columns else df.iloc[:, 0]
    yerr = df[yerr_col] if yerr_col in df.columns else None

    linewidth = mm_to_pt(style.get('trace_thickness_mm', 0.12))

    ax.errorbar(x, y, yerr=yerr, color=color, linewidth=linewidth,
                capsize=3, capthick=linewidth)

    if plot_spec.get('xlabel'):
        ax.set_xlabel(plot_spec['xlabel'])
    if plot_spec.get('ylabel'):
        ax.set_ylabel(plot_spec['ylabel'])
    if plot_spec.get('title'):
        ax.set_title(plot_spec['title'])

    return ax


def render_fill_between_plot(ax, df, plot_spec, style):
    """Render a fill_between plot for confidence intervals."""
    x_col = plot_spec.get('x_column', 'x')
    y_col = plot_spec.get('y_column', 'y')
    y_lower_col = plot_spec.get('y_lower_column', 'y_lower')
    y_upper_col = plot_spec.get('y_upper_column', 'y_upper')
    color = plot_spec.get('color', 'blue')

    x = df[x_col] if x_col in df.columns else range(len(df))
    y = df[y_col] if y_col in df.columns else df.iloc[:, 0]

    # Draw center line
    linewidth = mm_to_pt(style.get('trace_thickness_mm', 0.12))
    ax.plot(x, y, color=color, linewidth=linewidth)

    # Fill confidence interval if available
    if y_lower_col in df.columns and y_upper_col in df.columns:
        y_lower = df[y_lower_col]
        y_upper = df[y_upper_col]
        ax.fill_between(x, y_lower, y_upper, color=color, alpha=0.2)

    if plot_spec.get('xlabel'):
        ax.set_xlabel(plot_spec['xlabel'])
    if plot_spec.get('ylabel'):
        ax.set_ylabel(plot_spec['ylabel'])
    if plot_spec.get('title'):
        ax.set_title(plot_spec['title'])

    return ax


def render_hist_plot(ax, df, plot_spec, style):
    """Render a histogram."""
    data_col = plot_spec.get('data_column', 'value')
    color = plot_spec.get('color', 'blue')
    bins = plot_spec.get('bins', 20)

    data = df[data_col] if data_col in df.columns else df.iloc[:, 0]

    ax.hist(data, bins=bins, color=color, alpha=0.7, edgecolor='black')

    if plot_spec.get('xlabel'):
        ax.set_xlabel(plot_spec['xlabel'])
    if plot_spec.get('ylabel'):
        ax.set_ylabel(plot_spec['ylabel'])
    if plot_spec.get('title'):
        ax.set_title(plot_spec['title'])

    return ax


def render_boxplot_plot(ax, df, plot_spec, style):
    """Render a box plot."""
    # Support both single column or grouped data
    value_col = plot_spec.get('value_column', 'value')
    group_col = plot_spec.get('group_column', None)

    if group_col and group_col in df.columns:
        # Grouped boxplot
        groups = df[group_col].unique()
        data = [df[df[group_col] == g][value_col].values for g in groups]
        bp = ax.boxplot(data, labels=groups)
    else:
        # Single boxplot
        data = df[value_col] if value_col in df.columns else df.iloc[:, 0]
        bp = ax.boxplot([data])

    if plot_spec.get('xlabel'):
        ax.set_xlabel(plot_spec['xlabel'])
    if plot_spec.get('ylabel'):
        ax.set_ylabel(plot_spec['ylabel'])
    if plot_spec.get('title'):
        ax.set_title(plot_spec['title'])

    return ax


def render_violin_plot(ax, df, plot_spec, style):
    """Render a violin plot."""
    value_col = plot_spec.get('value_column', 'value')
    group_col = plot_spec.get('group_column', None)

    if group_col and group_col in df.columns:
        # Grouped violin plot
        groups = df[group_col].unique()
        data = [df[df[group_col] == g][value_col].values for g in groups]
        vp = ax.violinplot(data, positions=range(len(groups)), showmeans=True)
        ax.set_xticks(range(len(groups)))
        ax.set_xticklabels(groups)
    else:
        # Single violin plot
        data = df[value_col] if value_col in df.columns else df.iloc[:, 0]
        vp = ax.violinplot([data], showmeans=True)

    if plot_spec.get('xlabel'):
        ax.set_xlabel(plot_spec['xlabel'])
    if plot_spec.get('ylabel'):
        ax.set_ylabel(plot_spec['ylabel'])
    if plot_spec.get('title'):
        ax.set_title(plot_spec['title'])

    return ax


def render_raster_plot(ax, df, plot_spec, style):
    """Render a raster plot (event plot)."""
    # Expect data in format: time_col, trial_col
    time_col = plot_spec.get('time_column', 'time')
    trial_col = plot_spec.get('trial_column', 'trial')
    color = plot_spec.get('color', 'black')

    if time_col in df.columns and trial_col in df.columns:
        # Group by trial
        trials = df[trial_col].unique()
        positions = []
        for trial in sorted(trials):
            trial_times = df[df[trial_col] == trial][time_col].values
            positions.append(trial_times)

        ax.eventplot(positions, colors=color, linewidths=0.5)
    else:
        # Fall back to simple eventplot
        times = df[time_col] if time_col in df.columns else df.iloc[:, 0]
        ax.eventplot([times], colors=color)

    if plot_spec.get('xlabel'):
        ax.set_xlabel(plot_spec['xlabel'])
    if plot_spec.get('ylabel'):
        ax.set_ylabel(plot_spec['ylabel'])
    if plot_spec.get('title'):
        ax.set_title(plot_spec['title'])

    return ax


def render_single_plot(fig, panel_spec, style_spec):
    """
    Render a single plot on a specific axes within a figure.

    Args:
        fig: Matplotlib figure
        panel_spec: Panel specification with position and plot details
        style_spec: Style specifications

    Returns:
        ax: The created axes
    """
    # Get panel position in mm
    x_mm = panel_spec.get('x_mm', 0)
    y_mm = panel_spec.get('y_mm', 0)
    width_mm = panel_spec.get('width_mm', 35)
    height_mm = panel_spec.get('height_mm', 24.5)

    # Get figure dimensions
    fig_width_inch, fig_height_inch = fig.get_size_inches()

    # Convert mm to normalized figure coordinates (0-1)
    # Note: matplotlib origin is bottom-left
    x_norm = mm_to_inch(x_mm) / fig_width_inch
    y_norm = mm_to_inch(y_mm) / fig_height_inch
    width_norm = mm_to_inch(width_mm) / fig_width_inch
    height_norm = mm_to_inch(height_mm) / fig_height_inch

    # Create axes at specified position
    ax = fig.add_axes([x_norm, y_norm, width_norm, height_norm])

    # Apply style (but don't apply to figure again)
    tick_length_pt = mm_to_pt(style_spec.get('tick_length_mm', 0.8))
    tick_width_pt = mm_to_pt(style_spec.get('tick_thickness_mm', 0.2))
    axis_width_pt = mm_to_pt(style_spec.get('axis_thickness_mm', 0.2))

    ax.tick_params(
        axis='both',
        which='both',
        length=tick_length_pt,
        width=tick_width_pt,
    )

    # Set spine width and hide top/right spines (scientific style)
    for spine_name, spine in ax.spines.items():
        spine.set_linewidth(axis_width_pt)
        if spine_name in ['top', 'right']:
            spine.set_visible(False)

    # Get plot specification
    plot_spec = panel_spec.get('plot', {})

    # Load data from CSV or inline data array
    csv_path = plot_spec.get('csv_path')
    inline_data = plot_spec.get('data')

    if inline_data:
        # Convert inline data array to DataFrame
        # Supports [[x1, y1], [x2, y2], ...] format
        df = pd.DataFrame(inline_data, columns=['x', 'y'])
    elif csv_path and os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        raise ValueError(f"No data provided. Specify either 'data' (inline array) or 'csv_path' (file path)")

    # Render plot based on kind
    plot_kind = plot_spec.get('kind', 'line')

    # Priority 10 plot types + existing
    if plot_kind == 'line':
        ax = render_line_plot(ax, df, plot_spec, style_spec)
    elif plot_kind == 'scatter':
        ax = render_scatter_plot(ax, df, plot_spec, style_spec)
    elif plot_kind == 'bar':
        ax = render_bar_plot(ax, df, plot_spec, style_spec)
    elif plot_kind == 'barh':
        ax = render_barh_plot(ax, df, plot_spec, style_spec)
    elif plot_kind == 'errorbar':
        ax = render_errorbar_plot(ax, df, plot_spec, style_spec)
    elif plot_kind == 'fill_between':
        ax = render_fill_between_plot(ax, df, plot_spec, style_spec)
    elif plot_kind == 'hist':
        ax = render_hist_plot(ax, df, plot_spec, style_spec)
    elif plot_kind == 'boxplot':
        ax = render_boxplot_plot(ax, df, plot_spec, style_spec)
    elif plot_kind == 'violin':
        ax = render_violin_plot(ax, df, plot_spec, style_spec)
    elif plot_kind == 'raster':
        ax = render_raster_plot(ax, df, plot_spec, style_spec)
    else:
        raise ValueError(f"Unsupported plot kind: {plot_kind}. Supported types: line, scatter, bar, barh, errorbar, fill_between, hist, boxplot, violin, raster")

    # Add panel ID label if provided
    panel_id = panel_spec.get('id')
    if panel_id:
        # Place label at top-left corner
        ax.text(
            -0.15, 1.05, panel_id,
            transform=ax.transAxes,
            fontsize=style_spec.get('title_font_size_pt', 8),
            fontweight='bold',
            va='bottom'
        )

    return ax


def render_multipanel_from_spec(spec):
    """
    Render a multi-panel figure from JSON specification.

    Args:
        spec: Dictionary containing:
            - figure: {width_mm, height_mm, dpi}
            - style: {tick_length_mm, tick_thickness_mm, ...}
            - panels: [{id, x_mm, y_mm, width_mm, height_mm, plot: {...}}, ...]

    Returns:
        BytesIO buffer containing SVG data
    """
    # Extract specifications
    figure_spec = spec.get('figure', {})
    style_spec = spec.get('style', {})
    panels_spec = spec.get('panels', [])

    if not panels_spec:
        raise ValueError("No panels specified for multi-panel figure")

    # Figure dimensions
    width_mm = figure_spec.get('width_mm', 89)
    height_mm = figure_spec.get('height_mm', 60)
    dpi = figure_spec.get('dpi', 300)

    # Convert to inches for matplotlib
    width_inch = mm_to_inch(width_mm)
    height_inch = mm_to_inch(height_mm)

    # Create empty figure
    fig = plt.figure(figsize=(width_inch, height_inch), dpi=dpi)

    # Apply global style to rcParams
    tick_length_pt = mm_to_pt(style_spec.get('tick_length_mm', 0.8))
    tick_width_pt = mm_to_pt(style_spec.get('tick_thickness_mm', 0.2))
    axis_width_pt = mm_to_pt(style_spec.get('axis_thickness_mm', 0.2))
    trace_width_pt = mm_to_pt(style_spec.get('trace_thickness_mm', 0.12))
    axis_font_size = style_spec.get('axis_font_size_pt', 8)
    tick_font_size = style_spec.get('tick_font_size_pt', 7)
    title_font_size = style_spec.get('title_font_size_pt', 8)

    plt.rcParams.update({
        'font.family': 'Arial',
        'font.size': tick_font_size,
        'axes.linewidth': axis_width_pt,
        'axes.labelsize': axis_font_size,
        'axes.titlesize': title_font_size,
        'xtick.major.size': tick_length_pt,
        'ytick.major.size': tick_length_pt,
        'xtick.major.width': tick_width_pt,
        'ytick.major.width': tick_width_pt,
        'xtick.labelsize': tick_font_size,
        'ytick.labelsize': tick_font_size,
        'lines.linewidth': trace_width_pt,
    })

    # Render each panel
    for panel_spec in panels_spec:
        render_single_plot(fig, panel_spec, style_spec)

    # Save to buffer as SVG with transparent background
    buf = io.BytesIO()
    fig.savefig(buf, format='svg', bbox_inches='tight', dpi=dpi, transparent=True)
    plt.close(fig)

    buf.seek(0)
    return buf


def render_plot_from_spec(spec):
    """
    Main renderer function that creates a plot from JSON specification.
    Supports both single plot and multi-panel layouts.

    Args:
        spec: Dictionary containing either:
            Single plot:
                - figure: {width_mm, height_mm, dpi}
                - style: {tick_length_mm, tick_thickness_mm, ...}
                - plot: {kind, csv_path, x_column, y_column, ...}
            Multi-panel:
                - figure: {width_mm, height_mm, dpi}
                - style: {tick_length_mm, tick_thickness_mm, ...}
                - panels: [{id, x_mm, y_mm, width_mm, height_mm, plot: {...}}, ...]

    Returns:
        BytesIO buffer containing SVG data
    """
    # Check if multi-panel or single plot
    if 'panels' in spec:
        return render_multipanel_from_spec(spec)

    # Single plot rendering (original logic)
    # Extract specifications
    figure_spec = spec.get('figure', {})
    style_spec = spec.get('style', {})
    plot_spec = spec.get('plot', {})

    # Figure dimensions
    width_mm = figure_spec.get('width_mm', 35)
    height_mm = figure_spec.get('height_mm', 24.5)
    dpi = figure_spec.get('dpi', 300)

    # Convert to inches for matplotlib
    width_inch = mm_to_inch(width_mm)
    height_inch = mm_to_inch(height_mm)

    # Create figure
    fig, ax = plt.subplots(figsize=(width_inch, height_inch), dpi=dpi)

    # Apply Nature style
    fig, ax = apply_nature_style(fig, ax, style_spec)

    # Load data from CSV or inline data array
    csv_path = plot_spec.get('csv_path')
    inline_data = plot_spec.get('data')

    if inline_data:
        # Convert inline data array to DataFrame
        # Supports [[x1, y1], [x2, y2], ...] format
        df = pd.DataFrame(inline_data, columns=['x', 'y'])
    elif csv_path and os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        raise ValueError(f"No data provided. Specify either 'data' (inline array) or 'csv_path' (file path)")

    # Render plot based on kind
    plot_kind = plot_spec.get('kind', 'line')

    # Priority 10 plot types + existing
    if plot_kind == 'line':
        ax = render_line_plot(ax, df, plot_spec, style_spec)
    elif plot_kind == 'scatter':
        ax = render_scatter_plot(ax, df, plot_spec, style_spec)
    elif plot_kind == 'bar':
        ax = render_bar_plot(ax, df, plot_spec, style_spec)
    elif plot_kind == 'barh':
        ax = render_barh_plot(ax, df, plot_spec, style_spec)
    elif plot_kind == 'errorbar':
        ax = render_errorbar_plot(ax, df, plot_spec, style_spec)
    elif plot_kind == 'fill_between':
        ax = render_fill_between_plot(ax, df, plot_spec, style_spec)
    elif plot_kind == 'hist':
        ax = render_hist_plot(ax, df, plot_spec, style_spec)
    elif plot_kind == 'boxplot':
        ax = render_boxplot_plot(ax, df, plot_spec, style_spec)
    elif plot_kind == 'violin':
        ax = render_violin_plot(ax, df, plot_spec, style_spec)
    elif plot_kind == 'raster':
        ax = render_raster_plot(ax, df, plot_spec, style_spec)
    else:
        raise ValueError(f"Unsupported plot kind: {plot_kind}. Supported types: line, scatter, bar, barh, errorbar, fill_between, hist, boxplot, violin, raster")

    # Adjust layout
    fig.tight_layout()

    # Save to buffer as SVG with transparent background
    buf = io.BytesIO()
    fig.savefig(buf, format='svg', bbox_inches='tight', dpi=dpi, transparent=True)
    plt.close(fig)

    buf.seek(0)
    return buf


# EOF
