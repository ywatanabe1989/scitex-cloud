"""
LaTeX color mode handling for compilation.

Applies color themes to LaTeX content for different viewing modes.
"""


def apply_color_mode_to_latex(latex_content: str, color_mode: str) -> str:
    """Apply color mode to LaTeX content by injecting color commands.

    Args:
        latex_content: Original LaTeX content
        color_mode: 'light', 'dark', 'sepia', or 'paper'

    Returns:
        Modified LaTeX content with color commands
    """
    # Skip color injection for light mode (default LaTeX colors)
    if color_mode == "light":
        return latex_content

    # Define dark mode colors - Eye-friendly warm dark background with soft text
    # Following modern dark mode best practices (Material Design, GitHub, VS Code)
    # Background: #1c2128 (rgb 0.11, 0.129, 0.157) - darker warm gray with slight blue tint
    # Text: #c9d1d9 (rgb 0.788, 0.82, 0.851) - soft off-white with warm tone
    color_commands = """\\usepackage{xcolor}
\\pagecolor[rgb]{0.11,0.129,0.157}
\\color[rgb]{0.788,0.82,0.851}
"""

    # Find the position to inject
    if "\\begin{document}" in latex_content:
        # Insert right before \begin{document}
        latex_content = latex_content.replace(
            "\\begin{document}", f"{color_commands}\\begin{{document}}", 1
        )
    else:
        # Just prepend if no \begin{document} found
        latex_content = color_commands + latex_content

    return latex_content
