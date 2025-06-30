from django.core.management.base import BaseCommand
from apps.ai_assistant_app.models import AIModel


class Command(BaseCommand):
    help = 'Set up initial AI models for research assistance'

    def handle(self, *args, **options):
        """Create initial AI models if they don't exist."""
        
        models_to_create = [
            {
                'name': 'Claude-3-Sonnet',
                'model_type': 'claude',
                'api_endpoint': 'https://api.anthropic.com/v1/messages',
                'api_key_required': True,
                'max_tokens': 4096,
                'temperature': 0.7,
                'cost_per_1k_tokens': 0.003,
                'capabilities': [
                    'text_generation',
                    'research_analysis',
                    'literature_review',
                    'methodology_design',
                    'writing_assistance',
                    'citation_analysis'
                ],
                'description': 'Anthropic Claude 3 Sonnet for research assistance',
                'version': '3.0',
                'is_default': True,
                'is_active': True,
            },
            {
                'name': 'GPT-4',
                'model_type': 'openai_gpt4',
                'api_endpoint': 'https://api.openai.com/v1/chat/completions',
                'api_key_required': True,
                'max_tokens': 4096,
                'temperature': 0.7,
                'cost_per_1k_tokens': 0.03,
                'capabilities': [
                    'text_generation',
                    'research_analysis',
                    'literature_review',
                    'methodology_design',
                    'statistical_guidance',
                    'writing_assistance',
                    'trend_analysis'
                ],
                'description': 'OpenAI GPT-4 for comprehensive research assistance',
                'version': '4.0',
                'is_default': False,
                'is_active': True,
            },
            {
                'name': 'GPT-3.5-Turbo',
                'model_type': 'openai_gpt35',
                'api_endpoint': 'https://api.openai.com/v1/chat/completions',
                'api_key_required': True,
                'max_tokens': 4096,
                'temperature': 0.7,
                'cost_per_1k_tokens': 0.002,
                'capabilities': [
                    'text_generation',
                    'research_analysis',
                    'writing_assistance',
                    'citation_analysis'
                ],
                'description': 'OpenAI GPT-3.5 Turbo for basic research assistance',
                'version': '3.5',
                'is_default': False,
                'is_active': True,
            },
            {
                'name': 'Local-Research-LLM',
                'model_type': 'local_llm',
                'api_endpoint': 'http://localhost:11434/api/generate',
                'api_key_required': False,
                'max_tokens': 2048,
                'temperature': 0.7,
                'cost_per_1k_tokens': 0.0,
                'capabilities': [
                    'text_generation',
                    'research_analysis',
                    'writing_assistance'
                ],
                'description': 'Local LLM for research assistance (e.g., Ollama)',
                'version': '1.0',
                'is_default': False,
                'is_active': False,  # Disabled by default
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for model_data in models_to_create:
            model, created = AIModel.objects.get_or_create(
                name=model_data['name'],
                defaults=model_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created AI model: {model.name}')
                )
            else:
                # Update existing model with new data
                for key, value in model_data.items():
                    setattr(model, key, value)
                model.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated AI model: {model.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Setup complete! Created {created_count} models, updated {updated_count} models.'
            )
        )
        
        # Show current default model
        default_model = AIModel.objects.filter(is_default=True).first()
        if default_model:
            self.stdout.write(
                self.style.SUCCESS(f'Default AI model: {default_model.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING('No default AI model set!')
            )