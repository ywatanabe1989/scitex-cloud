import uuid
from django.db import migrations

def generate_slugs(apps, schema_editor):
    Project = apps.get_model('project_app', 'Project')
    from django.utils.text import slugify
    
    for project in Project.objects.all():
        if not project.slug or project.slug == 'project':
            base_slug = slugify(project.name) or 'project'
            counter = 1
            unique_slug = base_slug
            
            while Project.objects.filter(slug=unique_slug).exclude(id=project.id).exists():
                unique_slug = f'{base_slug}-{counter}'
                counter += 1
            
            project.slug = unique_slug
            project.save()

class Migration(migrations.Migration):
    atomic = False
    
    dependencies = [
        ('project_app', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(generate_slugs, migrations.RunPython.noop),
    ]
