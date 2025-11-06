#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-04 14:02:25 (ywatanabe)"
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
Comprehensive App Structure Validation Script
Checks both frontend (templates, CSS, TypeScript) and backend (models, views, services) structure
against FULLSTACK.md compliance.

Usage:
    python scripts/maintenance/validate_app_structure.py [app_name]
    python scripts/maintenance/validate_app_structure.py project_app
    python scripts/maintenance/validate_app_structure.py

If app_name is not provided, validates all apps in INSTALLED_APPS.
"""

import sys
from pathlib import Path
from collections import defaultdict


class AppStructureValidator:
    def __init__(self, app_path, app_name):
        self.app_path = Path(app_path)
        self.app_name = app_name
        self.templates_path = self.app_path / "templates" / app_name
        self.css_path = self.app_path / "static" / app_name / "css"
        self.ts_path = self.app_path / "static" / app_name / "ts"
        self.models_path = self.app_path / "models"
        self.views_path = self.app_path / "views"
        self.urls_path = self.app_path / "urls"

        self.errors = []
        self.warnings = []
        self.successes = []

    def validate(self):
        """Run all validations"""
        print(f"\n🔍 VALIDATING APP: {self.app_name}")
        print(f"   Path: {self.app_path}\n")

        # Check if app has frontend structure
        has_frontend = self.templates_path.exists()
        if has_frontend:
            self.validate_frontend_structure()

        # Check if app has backend structure
        has_backend = self.models_path.exists() or self.views_path.exists()
        if has_backend:
            self.validate_backend_structure()

        if not has_frontend and not has_backend:
            print(f"   ⚠️  No frontend or backend structure found")
            return False

        return self.print_summary()

    def validate_frontend_structure(self):
        """Validate frontend (templates, CSS, TypeScript) structure"""
        print("📱 FRONTEND STRUCTURE:")

        # Check main templates exist
        main_templates = self._get_main_templates()
        print(f"   • Templates: {len(main_templates)} main templates")

        # Group by feature
        features = defaultdict(list)
        for tmpl in main_templates:
            rel_path = tmpl.relative_to(self.templates_path)
            feature = rel_path.parts[0] if len(rel_path.parts) > 1 else "root"
            features[feature].append(tmpl.stem)

        print(f"   • Features: {len(features)} feature directories")

        # Check CSS files
        css_files = (
            list(self.css_path.rglob("*.css"))
            if self.css_path.exists()
            else []
        )
        print(f"   • CSS Files: {len(css_files)}")

        # Check TypeScript files
        ts_files = (
            list(self.ts_path.rglob("*.ts")) if self.ts_path.exists() else []
        )
        print(f"   • TypeScript Files: {len(ts_files)}")

        # Verify 1:1:1 correspondence for main templates
        mismatches = []
        for feature, templates in features.items():
            if feature == "root":
                continue
            for tmpl_name in templates:
                css_file = (
                    self.css_path / feature / f"{tmpl_name}.css"
                    if self.css_path.exists()
                    else None
                )
                ts_file = (
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
                f"✅ Frontend structure consistent (templates ↔ CSS ↔ TypeScript)"
            )
        else:
            if len(mismatches) <= 10:
                for m in mismatches:
                    self.warnings.append(m)
            else:
                self.warnings.append(
                    f"⚠️ {len(mismatches)} template-CSS-TS correspondence issues"
                )

    def validate_backend_structure(self):
        """Validate backend (models, views, services) structure"""
        print("\n🔧 BACKEND STRUCTURE:")

        # Check models organization
        if self.models_path.exists():
            self._validate_models_layer()

        # Check views organization
        if self.views_path.exists():
            self._validate_views_layer()

        # Check URLs organization
        if self.urls_path.exists():
            self._validate_urls_layer()

    def _validate_models_layer(self):
        """Validate models are feature-organized"""
        feature_dirs = [
            d
            for d in self.models_path.iterdir()
            if d.is_dir() and not d.name.startswith("_")
        ]

        if feature_dirs:
            print(
                f"   • Models: {len(feature_dirs)} feature-organized modules"
            )
            self.successes.append(
                f"✅ Models organized by feature ({len(feature_dirs)} modules)"
            )
        else:
            monolithic_files = [
                f
                for f in self.models_path.glob("*.py")
                if f.name != "__init__.py"
            ]
            if monolithic_files:
                self.warnings.append(
                    f"⚠️ Models appear monolithic ({len(monolithic_files)} files at root level)"
                )

    def _validate_views_layer(self):
        """Validate views are feature-organized"""
        feature_dirs = [
            d
            for d in self.views_path.iterdir()
            if d.is_dir() and not d.name.startswith("_")
        ]

        if feature_dirs:
            print(
                f"   • Views: {len(feature_dirs)} feature-organized directories"
            )
            self.successes.append(
                f"✅ Views organized by feature ({len(feature_dirs)} directories)"
            )
        else:
            view_files = [
                f
                for f in self.views_path.glob("*.py")
                if f.name != "__init__.py"
            ]
            if view_files:
                self.warnings.append(
                    f"⚠️ Views appear monolithic ({len(view_files)} files at root level)"
                )

    def _validate_urls_layer(self):
        """Validate URLs are feature-organized"""
        url_files = [
            f for f in self.urls_path.glob("*.py") if f.name != "__init__.py"
        ]

        if url_files:
            print(f"   • URLs: {len(url_files)} feature-organized modules")
            self.successes.append(
                f"✅ URLs organized by feature ({len(url_files)} modules)"
            )

    def _get_main_templates(self):
        """Get main templates (excluding partials and base)"""
        if not self.templates_path.exists():
            return []

        templates = []
        for tmpl_file in self.templates_path.rglob("*.html"):
            # Skip partials and base files
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

    def print_summary(self):
        """Print validation summary"""
        print(f"\n{'='*60}")
        print(f"SUMMARY: {self.app_name}")
        print(f"{'='*60}")

        if self.successes:
            print(f"\n✅ SUCCESSES ({len(self.successes)}):")
            for success in self.successes:
                print(f"   {success}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   {warning}")

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   {error}")
            return False

        print(f"\n✅ VALIDATION PASSED\n")
        return True


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent.parent
    apps_path = project_root / "apps"

    # Determine which apps to validate
    if len(sys.argv) > 1:
        app_names = sys.argv[1:]
    else:
        # Validate all apps
        app_names = [
            d.name
            for d in apps_path.iterdir()
            if d.is_dir() and not d.name.startswith("_")
        ]

    print(f"\n{'='*60}")
    print(f"APP STRUCTURE VALIDATION")
    print(f"{'='*60}")

    all_passed = True
    for app_name in sorted(app_names):
        app_path = apps_path / app_name

        if not app_path.exists():
            print(f"\n❌ App not found: {app_name}")
            all_passed = False
            continue

        validator = AppStructureValidator(app_path, app_name)
        if not validator.validate():
            all_passed = False

    print(f"{'='*60}")
    if all_passed:
        print("✅ ALL VALIDATIONS PASSED")
    else:
        print("❌ SOME VALIDATIONS FAILED")
    print(f"{'='*60}\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

# EOF
