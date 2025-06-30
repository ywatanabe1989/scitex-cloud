from rest_framework import serializers
from django.contrib.auth.models import User
from apps.document_app.models import Document
from apps.project_app.models import Project
from apps.auth_app.models import UserProfile
from apps.cloud_app.models import Subscription, CloudResource, APIKey, ServiceIntegration
from apps.writer_app.models import DocumentTemplate, Manuscript, ManuscriptSection, Figure, Table, Citation
from apps.engine_app.models import EngineConfiguration, EngineSession, EngineRequest


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile information."""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for research projects."""
    owner = serializers.ReadOnlyField(source='owner.username')
    document_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'hypothesis', 'owner',
            'created_at', 'updated_at', 'is_public', 'is_archived',
            'document_count', 'github_repo', 'gitlab_repo'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at', 'document_count']
    
    def get_document_count(self, obj):
        return obj.documents.count()


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for documents."""
    project_title = serializers.ReadOnlyField(source='project.title')
    
    class Meta:
        model = Document
        fields = [
            'id', 'project', 'project_title', 'title', 'document_type',
            'content', 'file_path', 'version', 'created_at', 'updated_at',
            'is_compiled', 'compiled_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'version']


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscription information."""
    plan_name = serializers.ReadOnlyField(source='plan.name')
    plan_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'plan_name', 'status', 'trial_start', 'trial_end',
            'current_period_start', 'current_period_end', 'canceled_at',
            'plan_details'
        ]
        read_only_fields = fields
    
    def get_plan_details(self, obj):
        return {
            'max_projects': obj.plan.max_projects,
            'storage_gb': obj.plan.storage_gb,
            'cpu_cores': obj.plan.cpu_cores,
            'gpu_vram_gb': obj.plan.gpu_vram_gb,
            'has_watermark': obj.plan.has_watermark,
            'requires_citation': obj.plan.requires_citation,
        }


class ResourceUsageSerializer(serializers.ModelSerializer):
    """Serializer for resource usage tracking."""
    
    class Meta:
        model = CloudResource
        fields = [
            'id', 'resource_type', 'amount_used', 'unit',
            'period_start', 'period_end', 'created_at'
        ]
        read_only_fields = fields


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for API keys."""
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'name', 'prefix', 'can_read', 'can_write', 'can_delete',
            'rate_limit_per_hour', 'is_active', 'last_used', 'created_at', 'expires_at'
        ]
        read_only_fields = ['id', 'prefix', 'last_used', 'created_at']
        extra_kwargs = {
            'key': {'write_only': True}  # Never expose the full key
        }


class ServiceIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for service integrations."""
    
    class Meta:
        model = ServiceIntegration
        fields = [
            'id', 'integration_type', 'external_id', 'is_active',
            'last_synced', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        # Never serialize tokens
        exclude = ['access_token', 'refresh_token']


# SciTeX-Doc Serializers
class DocumentTemplateSerializer(serializers.ModelSerializer):
    """Serializer for document templates."""
    created_by_username = serializers.ReadOnlyField(source='created_by.username')
    
    class Meta:
        model = DocumentTemplate
        fields = [
            'id', 'name', 'description', 'template_type', 'content',
            'is_public', 'created_by', 'created_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class ManuscriptSectionSerializer(serializers.ModelSerializer):
    """Serializer for manuscript sections."""
    
    class Meta:
        model = ManuscriptSection
        fields = [
            'id', 'section_type', 'title', 'content', 'order',
            'is_ai_generated', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FigureSerializer(serializers.ModelSerializer):
    """Serializer for figures."""
    
    class Meta:
        model = Figure
        fields = [
            'id', 'number', 'caption', 'file', 'width', 'position',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TableSerializer(serializers.ModelSerializer):
    """Serializer for tables."""
    
    class Meta:
        model = Table
        fields = [
            'id', 'number', 'caption', 'content', 'position',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CitationSerializer(serializers.ModelSerializer):
    """Serializer for citations."""
    
    class Meta:
        model = Citation
        fields = [
            'id', 'key', 'citation_type', 'authors', 'title', 'year',
            'journal', 'volume', 'number', 'pages', 'doi', 'url', 'bibtex'
        ]
        read_only_fields = ['id']


class ManuscriptSerializer(serializers.ModelSerializer):
    """Serializer for manuscripts."""
    owner_username = serializers.ReadOnlyField(source='owner.username')
    sections = ManuscriptSectionSerializer(many=True, read_only=True)
    figures = FigureSerializer(many=True, read_only=True)
    tables = TableSerializer(many=True, read_only=True)
    citations = CitationSerializer(many=True, read_only=True)
    
    class Meta:
        model = Manuscript
        fields = [
            'id', 'title', 'slug', 'abstract', 'keywords',
            'template', 'owner', 'owner_username', 'collaborators',
            'status', 'is_public', 'sections', 'figures', 'tables',
            'citations', 'created_at', 'updated_at', 'last_compiled'
        ]
        read_only_fields = ['id', 'slug', 'owner', 'created_at', 'updated_at']


# SciTeX-Engine Serializers
class EngineConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for engine configurations."""
    
    class Meta:
        model = EngineConfiguration
        fields = [
            'id', 'name', 'description', 'emacs_version', 'packages',
            'settings', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EngineSessionSerializer(serializers.ModelSerializer):
    """Serializer for engine sessions."""
    configuration_name = serializers.ReadOnlyField(source='configuration.name')
    
    class Meta:
        model = EngineSession
        fields = [
            'id', 'session_id', 'configuration', 'configuration_name',
            'started_at', 'ended_at', 'is_active', 'total_requests'
        ]
        read_only_fields = fields


class EngineRequestSerializer(serializers.ModelSerializer):
    """Serializer for engine requests."""
    
    class Meta:
        model = EngineRequest
        fields = [
            'id', 'session', 'request_type', 'prompt', 'context',
            'response', 'tokens_used', 'processing_time', 'status',
            'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']