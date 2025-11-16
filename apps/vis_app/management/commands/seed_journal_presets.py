"""
Seed journal presets for scientific figure editor
Based on official journal submission guidelines
"""

from django.core.management.base import BaseCommand
from apps.vis_app.models import JournalPreset


class Command(BaseCommand):
    help = "Seed journal presets for scientific figures"

    def handle(self, *args, **options):
        presets = [
            # Nature
            {
                "name": "Nature",
                "column_type": "single",
                "width_mm": 89,
                "height_mm": None,  # Auto
                "dpi": 300,
                "font_family": "Arial",
                "font_size_pt": 7,
                "line_width_pt": 0.5,
            },
            {
                "name": "Nature",
                "column_type": "double",
                "width_mm": 183,
                "height_mm": None,
                "dpi": 300,
                "font_family": "Arial",
                "font_size_pt": 7,
                "line_width_pt": 0.5,
            },
            # Science
            {
                "name": "Science",
                "column_type": "single",
                "width_mm": 87,
                "height_mm": None,
                "dpi": 300,
                "font_family": "Arial",
                "font_size_pt": 8,
                "line_width_pt": 0.5,
            },
            {
                "name": "Science",
                "column_type": "double",
                "width_mm": 180,
                "height_mm": None,
                "dpi": 300,
                "font_family": "Arial",
                "font_size_pt": 8,
                "line_width_pt": 0.5,
            },
            # Cell
            {
                "name": "Cell",
                "column_type": "single",
                "width_mm": 85,
                "height_mm": None,
                "dpi": 300,
                "font_family": "Helvetica",
                "font_size_pt": 7,
                "line_width_pt": 0.5,
            },
            {
                "name": "Cell",
                "column_type": "double",
                "width_mm": 180,
                "height_mm": None,
                "dpi": 300,
                "font_family": "Helvetica",
                "font_size_pt": 7,
                "line_width_pt": 0.5,
            },
            # PNAS
            {
                "name": "PNAS",
                "column_type": "single",
                "width_mm": 87,
                "height_mm": None,
                "dpi": 300,
                "font_family": "Arial",
                "font_size_pt": 6,
                "line_width_pt": 0.5,
            },
            {
                "name": "PNAS",
                "column_type": "double",
                "width_mm": 180,
                "height_mm": None,
                "dpi": 300,
                "font_family": "Arial",
                "font_size_pt": 6,
                "line_width_pt": 0.5,
            },
        ]

        created_count = 0
        updated_count = 0

        for preset_data in presets:
            preset, created = JournalPreset.objects.update_or_create(
                name=preset_data["name"],
                column_type=preset_data["column_type"],
                defaults=preset_data,
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Created: {preset.name} - {preset.get_column_type_display()}"
                    )
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"⟳ Updated: {preset.name} - {preset.get_column_type_display()}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Done: {created_count} created, {updated_count} updated"
            )
        )
