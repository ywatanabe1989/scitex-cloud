# SciTeX Integration in SciTeX Cloud

SciTeX Cloud provides seamless integration with the scitex Python package, offering enhanced features for scientific computing and visualization.

## Features

### 1. Import and Use SciTeX Package

The scitex package is pre-installed in all SciTeX Cloud workspaces and can be imported directly:

```python
import scitex

# Access all scitex modules
import scitex.plt as plt  # Publication-ready plotting
import scitex.io as io    # Advanced I/O
import scitex.stats as stats  # Statistical tools
# ... and many more
```

**Available scitex modules:**
- `scitex.plt` - Enhanced matplotlib wrapper with publication-ready defaults
- `scitex.io` - Unified I/O for various formats (NPY, HDF5, CSV, etc.)
- `scitex.ai` / `scitex.ml` - Machine learning utilities
- `scitex.stats` - Statistical analysis
- `scitex.pd` - Pandas extensions
- `scitex.scholar` - Academic paper management
- `scitex.writer` - LaTeX document generation
- And many more...

### 2. Inline Figure Rendering

Figures created with matplotlib or scitex.plt are automatically displayed inline in the terminal output:

```python
import matplotlib.pyplot as plt
import numpy as np

# Create a plot
x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(10, 6))
plt.plot(x, y)
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Sine Wave')

# Show inline in terminal
plt.show()  # Automatically renders inline in SciTeX Cloud!
```

**How it works:**
- When you call `plt.show()`, figures are automatically saved to `.scitex_figures/` in your project directory
- The terminal detects the inline image markers and renders them directly in the output
- No need for separate image viewers or external tools!

**Supported formats:**
- PNG, JPEG, GIF, WebP, SVG
- Base64-encoded for efficient transmission

### 3. Relative Path Detection & File Links

File paths in terminal output are automatically converted to clickable links:

```python
import scitex.io as io
import numpy as np

# Save data
data = np.random.randn(100, 100)
io.save(data, './output/results.npy')
# Output: "Saved to: ./output/results.npy" becomes a clickable link!

# Save figures
import matplotlib.pyplot as plt
plt.figure()
plt.plot([1, 2, 3], [1, 4, 9])
plt.savefig('./output/plot.png')
# Output: "Figure saved to: ./output/plot.png" becomes a clickable link!
```

**Supported path patterns:**
- Relative paths: `./file.ext`, `../dir/file.ext`
- Paths following keywords: "Saved to:", "Created:", "Output:", etc.
- Common file extensions: `.png`, `.jpg`, `.pdf`, `.csv`, `.py`, `.json`, etc.

**Clickable link features:**
- Click to open file in the editor
- File type icons (🖼️ for images, 📊 for data, 💻 for code, etc.)
- Hover to see full path

## Environment Variables

SciTeX Cloud sets the following environment variables in terminal sessions:

```bash
SCITEX_CLOUD_CODE_WORKSPACE=true      # Indicates cloud environment
SCITEX_CLOUD_CODE_BACKEND=inline      # Backend type for rendering
SCITEX_CLOUD_CODE_SESSION_ID=<id>    # Current session ID
SCITEX_CLOUD_CODE_PROJECT_ROOT=<path> # Project root directory
SCITEX_CLOUD_CODE_USERNAME=<user>    # Current username
```

## Cloud-Aware Code

You can write code that adapts to the cloud environment:

```python
import scitex.cloud as cloud

if cloud.is_cloud_environment():
    print("Running in SciTeX Cloud!")
    backend = cloud.get_cloud_backend()  # 'inline'
    project_root = cloud.get_project_root()  # Path object
else:
    print("Running locally")

# Manually emit inline images (usually automatic)
cloud.emit_inline_image('./my_figure.png')

# Manually emit file links
cloud.emit_file_link('./my_data.csv', line_number=42)
```

## Best Practices

### 1. Use scitex.plt for Publication-Ready Figures

```python
import scitex.plt as plt

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# scitex.plt provides enhanced axes with additional methods
axes[0, 0].plot([1, 2, 3], [1, 4, 9])
axes[0, 0].set_title('Quadratic')

# Save with metadata (scitex feature)
plt.savefig('./output/multi_panel.png')
plt.show()  # Inline display in cloud
```

### 2. Use Relative Paths

Always use relative paths (starting with `./` or `../`) for better portability:

```python
# Good ✓
output_file = './results/experiment_1.csv'

# Avoid ✗
output_file = '/home/user/proj/project/results/experiment_1.csv'
```

### 3. Organize Output in Subdirectories

```python
import os

# Create output directories
os.makedirs('./figures', exist_ok=True)
os.makedirs('./data', exist_ok=True)
os.makedirs('./reports', exist_ok=True)

# Save organized outputs
plt.savefig('./figures/plot_1.png')
io.save(data, './data/results.npy')
```

## Examples

### Complete Example: Data Analysis with Visualization

```python
#!/usr/bin/env python3
import numpy as np
import scitex.plt as plt
import scitex.io as io

print("Running data analysis...")

# Generate data
x = np.linspace(0, 10, 100)
y = 2 * x + 1 + np.random.randn(100) * 0.5

# Create figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Scatter plot
ax1.scatter(x, y, alpha=0.5)
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_title('Raw Data')

# Histogram
ax2.hist(y, bins=20, alpha=0.7)
ax2.set_xlabel('Y values')
ax2.set_ylabel('Frequency')
ax2.set_title('Distribution')

# Save outputs
plt.savefig('./figures/analysis.png')
print("Figure saved to: ./figures/analysis.png")

io.save({'x': x, 'y': y}, './data/raw_data.pkl')
print("Data saved to: ./data/raw_data.pkl")

# Display inline
plt.show()

print("Analysis complete!")
```

## Troubleshooting

### Figures not displaying inline

1. Ensure you're calling `plt.show()` or `plt.savefig()`
2. Check that matplotlib is imported
3. Verify cloud environment variables: `echo $SCITEX_CLOUD_CODE_WORKSPACE`

### File links not working

1. Use relative paths starting with `./` or `../`
2. Ensure files exist before referencing them
3. Check file extension is supported

### Import errors

1. Check scitex is installed: `python -c "import scitex; print(scitex.__version__)"`
2. Verify you're in the cloud environment: `echo $SCITEX_CLOUD_CODE_WORKSPACE`

## API Reference

### scitex.cloud

- `is_cloud_environment() -> bool`: Check if running in SciTeX Cloud
- `get_cloud_backend() -> str`: Get cloud backend type ('inline', 'default')
- `get_project_root() -> Path | None`: Get project root directory
- `emit_inline_image(path, alt_text='Figure')`: Manually emit inline image
- `emit_file_link(path, line_number=None)`: Manually emit file link

## See Also

- [SciTeX Documentation](https://scitex.readthedocs.io)
- [SciTeX GitHub](https://github.com/ywatanabe1989/scitex-code)
- [Matplotlib Documentation](https://matplotlib.org)
