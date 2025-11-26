<!-- ---
!-- Timestamp: 2025-11-18 20:05:33
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/examples/scitex-research-template/README.md
!-- --- -->

# SciTeX Research Template

A boilerplate template for scientific research projects using the [SciTeX](https://scitex.ai) framework.

## What is This?

This is a **template project** designed to be used as a starting point for your research. It demonstrates the standard SciTeX workflow with an MNIST example pipeline.

Part of the [scitex](https://github.com/ywatanabe1989/scitex-code) package (`scitex.template` module).

## Quick Start

```bash
# Clone and setup
git clone https://github.com/ywatanabe1989/scitex-research-template.git
cd scitex-research-template
make install
make setup

# Run example pipeline
make run-mnist
```

## Project Structure

```
scitex-research-template/
├── config/            # YAML configuration files
├── data/              # Centralized data storage
├── scripts/           # Analysis scripts
│   ├── mnist/         # MNIST example pipeline
│   └── template.py    # Template for new scripts
├── tests/             # Test suite
├── scitex/            # SciTeX managed resources
│   ├── writer/        # Manuscript projects
│   ├── scholar/       # Research notes
│   ├── vis/           # Figure management
│   └── ai/            # AI prompts
└── Makefile           # Automation commands
```

## Using as a Template

1. **Clone or fork** this repository
2. **Remove MNIST example** if not needed
3. **Add your scripts** to `scripts/your_project/`
4. **Configure** paths in `config/PATH.yaml`
5. **Run** `make run-your-script`

## Key Features

- **Standardized structure** for reproducible research
- **Automated workflows** via Makefile
- **Manuscript management** with LaTeX compilation
- **Testing framework** included
- **Figure provenance** tracking

## Common Commands

```bash
make run-mnist          # Run MNIST example
make setup-writer       # Create manuscript project
make test              # Run tests
make format            # Format code
make clean             # Clean outputs
make help              # Show all commands
```

## Documentation

For detailed documentation, see:
- [SciTeX Documentation](https://scitex.ai)
- [SciTeX GitHub](https://github.com/ywatanabe1989/scitex-code)
- [MNIST Example README](scripts/mnist/README.md)

## License

AGPL-3.0

## Contact

Yusuke Watanabe (ywatanabe@scitex.ai)

<!-- EOF -->