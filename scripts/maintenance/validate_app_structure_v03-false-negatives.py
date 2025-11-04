#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-04 14:04:33 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/scripts/maintenance/validate_app_structure.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./scripts/maintenance/validate_app_structure.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  * Validates app structure compliance with FULLSTACK.md standards
  * Checks frontend structure (templates, CSS, TypeScript) consistency
  * Validates backend structure (models, views, URLs) organization
  * Reports mismatches and organizational issues
  * Saves validation results to console

Dependencies:
  * scripts:
    * None
  * packages:
    * pathlib, collections

Input:
  * Command-line argument: app_name (optional)
  * Directory structure: apps/[app_name]/

Output:
  * Console output: validation results and summary
"""

"""Imports"""
import sys
from pathlib import Path
from collections import defaultdict
from typing import List

"""Parameters"""

"""Functions & Classes"""
class AppStructureValidator:
    """Validates Django app structure against FULLSTACK.md standards.

    Example
    -------
    >>> app_path = Path("./apps/project_app")
    >>> validator = AppStructureValidator(app_path, "project_app")
    >>> passed = validator.validate()
    >>> print(passed)
    True

    Parameters
    ----------
    app_path : str or Path
        Path to the app directory
    app_name : str
        Name of the app

    Attributes
    ----------
    app_path : Path
        Path object for app directory
    app_name : str
        Name of the app
    templates_path : Path
        Path to templates directory
    css_path : Path
        Path to CSS files directory
    ts_path : Path
        Path to TypeScript files directory
    models_path : Path
        Path to models directory
    views_path : Path
        Path to views directory
    urls_path : Path
        Path to URLs directory
    errors : list
        List of validation errors
    warnings : list
        List of validation warnings
    successes : list
        List of validation successes
    """

    def __init__(self, app_path: str | Path, app_name: str) -> None:
        self.app_path: Path = Path(app_path)
        self.app_name: str = app_name
        self.templates_path: Path = self.app_path / "templates" / app_name
        self.css_path: Path = self.app_path / "static" / app_name / "css"
        self.ts_path: Path = self.app_path / "static" / app_name / "ts"
        self.models_path: Path = self.app_path / "models"
        self.views_path: Path = self.app_path / "views"
        self.urls_path: Path = self.app_path / "urls"
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.successes: List[str] = []

    def validate(self) -> bool:
        """Runs all validations.

        Returns
        -------
        bool
            True if all validations passed, False otherwise
        """
        print(f"\n🔍 VALIDATING APP: {self.app_name}")
        print(f"   Path: {self.app_path}\n")

        has_frontend: bool = self.templates_path.exists()
        if has_frontend:
            self.validate_frontend_structure()

        has_backend: bool = (
            self.models_path.exists() or self.views_path.exists()
        )
        if has_backend:
            self.validate_backend_structure()

        if not has_frontend and not has_backend:
            print("   ⚠️  No frontend or backend structure found")
            return False

        return self.print_summary()

    def validate_frontend_structure(self) -> None:
        """Validates frontend (templates, CSS, TypeScript) structure."""
        print("📱 FRONTEND STRUCTURE:")

        main_templates: List[Path] = self._get_main_templates()
        print(f"   • Templates: {len(main_templates)} main templates")

        features: defaultdict = defaultdict(list)
        for tmpl in main_templates:
            rel_path: Path = tmpl.relative_to(self.templates_path)
            feature: str = (
                rel_path.parts[0] if len(rel_path.parts) > 1 else "root"
            )
            features[feature].append(tmpl.stem)

        print(f"   • Features: {len(features)} feature directories")

        css_files: List[Path] = (
            list(self.css_path.rglob("*.css"))
            if self.css_path.exists()
            else []
        )
        print(f"   • CSS Files: {len(css_files)}")

        ts_files: List[Path] = (
            list(self.ts_path.rglob("*.ts")) if self.ts_path.exists() else []
        )
        print(f"   • TypeScript Files: {len(ts_files)}")

        mismatches: List[str] = []
        for feature, templates in features.items():
            if feature == "root":
                continue

            for tmpl_name in templates:
                css_file: Path | None = (
                    self.css_path / feature / f"{tmpl_name}.css"
                    if self.css_path.exists()
                    else None
                )
                ts_file: Path | None = (
                    self.ts_path / feature / f"{tmpl_name}.ts"
                    if self.ts_path.exists()
                    else None
                )

                if css_file and not css_file.exists():
                    mismatches.append(
                        f"Missing CSS: {feature}/{tmpl_name}.css"
                    )
                if ts_file and not ts_file.exists():
                    mismatches.append(f"Missing TS: {feature}/{tmpl_name}.ts")

        if not mismatches:
            self.successes.append(
                "✅ Frontend structure consistent (templates ↔ CSS ↔ TypeScript)"
            )
        else:
            if len(mismatches) <= 10:
                for mismatch in mismatches:
                    self.warnings.append(mismatch)
            else:
                warning_msg: str = (
                    f"⚠️ {len(mismatches)} template-CSS-TS correspondence issues"
                )
                self.warnings.append(warning_msg)

    def validate_backend_structure(self) -> None:
        """Validates backend (models, views, services) structure."""
        print("\n🔧 BACKEND STRUCTURE:")

        if self.models_path.exists():
            self._validate_models_layer()

        if self.views_path.exists():
            self._validate_views_layer()

        if self.urls_path.exists():
            self._validate_urls_layer()

    def _validate_models_layer(self) -> None:
        """Validates models are feature-organized."""
        feature_dirs: List[Path] = [
            directory
            for directory in self.models_path.iterdir()
            if directory.is_dir() and not directory.name.startswith("_")
        ]

        if feature_dirs:
            num_modules: int = len(feature_dirs)
            print(f"   • Models: {num_modules} feature-organized modules")
            self.successes.append(
                f"✅ Models organized by feature ({num_modules} modules)"
            )
        else:
            monolithic_files: List[Path] = [
                file
                for file in self.models_path.glob("*.py")
                if file.name != "__init__.py"
            ]
            if monolithic_files:
                num_files: int = len(monolithic_files)
                warning_msg: str = (
                    f"⚠️ Models appear monolithic ({num_files} files at root level)"
                )
                self.warnings.append(warning_msg)

    def _validate_views_layer(self) -> None:
        """Validates views are feature-organized."""
        feature_dirs: List[Path] = [
            directory
            for directory in self.views_path.iterdir()
            if directory.is_dir() and not directory.name.startswith("_")
        ]

        if feature_dirs:
            num_dirs: int = len(feature_dirs)
            print(f"   • Views: {num_dirs} feature-organized directories")
            self.successes.append(
                f"✅ Views organized by feature ({num_dirs} directories)"
            )
        else:
            view_files: List[Path] = [
                file
                for file in self.views_path.glob("*.py")
                if file.name != "__init__.py"
            ]
            if view_files:
                num_files: int = len(view_files)
                warning_msg: str = (
                    f"⚠️ Views appear monolithic ({num_files} files at root level)"
                )
                self.warnings.append(warning_msg)

    def _validate_urls_layer(self) -> None:
        """Validates URLs are feature-organized."""
        url_files: List[Path] = [
            file
            for file in self.urls_path.glob("*.py")
            if file.name != "__init__.py"
        ]

        if url_files:
            num_modules: int = len(url_files)
            print(f"   • URLs: {num_modules} feature-organized modules")
            self.successes.append(
                f"✅ URLs organized by feature ({num_modules} modules)"
            )

    def _get_main_templates(self) -> List[Path]:
        """Gets main templates (excluding partials and base).

        Returns
        -------
        List[Path]
            List of main template file paths
        """
        if not self.templates_path.exists():
            return []

        templates: List[Path] = []
        for tmpl_file in self.templates_path.rglob("*.html"):
            if tmpl_file.stem.startswith("_"):
                continue
            if "_partials" in tmpl_file.parts:
                continue
            if "base" in tmpl_file.parts or tmpl_file.name == "base.html":
                continue
            if ".old" in tmpl_file.parts or "legacy" in tmpl_file.parts:
                continue
            templates.append(tmpl_file)

        return templates

    def print_summary(self) -> bool:
        """Prints validation summary.

        Returns
        -------
        bool
            True if validation passed, False otherwise
        """
        separator: str = "=" * 60
        print(f"\n{separator}")
        print(f"SUMMARY: {self.app_name}")
        print(f"{separator}")

        if self.successes:
            num_successes: int = len(self.successes)
            print(f"\n✅ SUCCESSES ({num_successes}):")
            for success in self.successes:
                print(f"   {success}")

        if self.warnings:
            num_warnings: int = len(self.warnings)
            print(f"\n⚠️  WARNINGS ({num_warnings}):")
            for warning in self.warnings:
                print(f"   {warning}")

        if self.errors:
            num_errors: int = len(self.errors)
            print(f"\n❌ ERRORS ({num_errors}):")
            for error in self.errors:
                print(f"   {error}")
            return False

        print("\n✅ VALIDATION PASSED\n")
        return True


def main() -> int:
    """Main entry point.

    Returns
    -------
    int
        Exit status (0 for success, 1 for failure)
    """
    project_root: Path = Path(__file__).parent.parent.parent
    apps_path: Path = project_root / "apps"

    if len(sys.argv) > 1:
        app_names: List[str] = sys.argv[1:]
    else:
        app_names: List[str] = [
            directory.name
            for directory in apps_path.iterdir()
            if directory.is_dir() and not directory.name.startswith("_")
        ]

    separator: str = "=" * 60
    print(f"\n{separator}")
    print("APP STRUCTURE VALIDATION")
    print(f"{separator}")

    all_passed: bool = True
    for app_name in sorted(app_names):
        app_path: Path = apps_path / app_name
        if not app_path.exists():
            print(f"\n❌ App not found: {app_name}")
            all_passed = False
            continue

        validator: AppStructureValidator = AppStructureValidator(
            app_path, app_name
        )
        if not validator.validate():
            all_passed = False

    print(f"{separator}")
    if all_passed:
        print("✅ ALL VALIDATIONS PASSED")
    else:
        print("❌ SOME VALIDATIONS FAILED")
    print(f"{separator}\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

# EOF
