"""
Admin configuration for SearchIndex, Collection, and UserLibrary models.
"""
from django.contrib import admin
from ..models import SearchIndex, Collection, UserLibrary


@admin.register(SearchIndex)
class SearchIndexAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "document_type",
        "publication_date",
        "citation_count",
        "view_count",
        "status",
    ]
    list_filter = [
        "document_type",
        "status",
        "source",
        "is_open_access",
        "publication_date",
    ]
    search_fields = ["title", "abstract", "doi", "pmid", "arxiv_id"]
    date_hierarchy = "publication_date"
    ordering = ["-publication_date"]


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "is_public", "paper_count_display", "created_at"]
    list_filter = ["is_public", "created_at"]
    search_fields = ["name", "description", "user__username"]

    def paper_count_display(self, obj):
        return obj.paper_count()

    paper_count_display.short_description = "Paper Count"


@admin.register(UserLibrary)
class UserLibraryAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "paper_title",
        "reading_status",
        "importance_rating",
        "saved_at",
    ]
    list_filter = ["reading_status", "importance_rating", "saved_at"]
    search_fields = ["user__username", "paper__title", "project", "tags"]

    def paper_title(self, obj):
        return (
            obj.paper.title[:50] + "..."
            if len(obj.paper.title) > 50
            else obj.paper.title
        )

    paper_title.short_description = "Paper"
