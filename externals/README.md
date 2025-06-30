# SciTeX External Components

This directory contains the core SciTeX ecosystem components that integrate with the cloud platform.

## Core SciTeX Components

### 🔧 SciTeX-Engine (emacs-claude-code)
- **Purpose**: LLM agent system for Emacs enabling seamless human-AI collaboration
- **Integration**: Code execution and development environment
- **Status**: External component

### 🐍 SciTeX-Code (SciTeX-Code)
- **Purpose**: Standardized Python framework for scientific analysis and computation
- **Integration**: Jupyter notebooks, data analysis workflows
- **Status**: ✅ Cloned (git repository)

### 📊 SciTeX-Viz (SciTeX-Viz)
- **Purpose**: Python wrapper for SigmaPlot enabling programmatic scientific visualization
- **Integration**: Visualization pipeline, figure generation
- **Status**: ✅ Cloned (git repository)

### 🔍 SciTeX-Scholar (SciTeX-Scholar)
- **Purpose**: Literature search, knowledge gap identification, and hypothesis generation
- **Integration**: Paper search and recommendation system
- **Status**: ✅ Cloned (git repository)

### 📝 SciTeX-Writer (SciTeX-Writer)
- **Purpose**: Automated LaTeX compilation system with predefined tex, bibtex, table, and figure files
- **Integration**: Cloud compilation, project templates
- **Status**: ✅ Cloned (git repository)

### 📋 SciTeX-Example-Research-Project
- **Purpose**: Complete research project boilerplate and template
- **Integration**: Project creation template, directory structure
- **Status**: ✅ Cloned (git repository)

### ☁️ SciTeX-Cloud (Current Repository)
- **Purpose**: Cloud platform for the SciTeX ecosystem (https://scitex.ai)
- **Integration**: Django web platform, API endpoints
- **Status**: ✅ Active

## Directory Structure

```
SciTeX-Cloud/
├── externals/
│   ├── SciTeX-Engine/                    (to be cloned)
│   ├── SciTeX-Code/                      ✅ Cloned
│   ├── SciTeX-Viz/                       ✅ Cloned
│   ├── SciTeX-Scholar/                   ✅ Cloned
│   ├── SciTeX-Writer/                    ✅ Cloned
│   ├── SciTeX-Example-Research-Project/  ✅ Cloned
│   ├── setup_externals.sh               (automated setup)
│   └── README.md                         (this file)
├── apps/                                 # Django applications
├── config/                               # Django settings
└── ...
```

## Adding New Components

To add a new SciTeX component:

1. Add repository URL to `scripts/setup_externals.sh`
2. Update Django settings in `config/settings/base.py`
3. Run `bash scripts/setup_externals.sh`
4. Update this README

## Integration Notes

- **Template System**: `SciTeX-Example-Research-Project` used as project boilerplate
- **Cloud Access**: All components accessible via Django settings paths
- **CUI Workflows**: Local components available for command-line use
- **Auto-Customization**: Templates personalized with project name/author
- **Version Control**: Each component maintains independent git repository