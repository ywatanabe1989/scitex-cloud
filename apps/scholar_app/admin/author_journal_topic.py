"""
Admin configuration for Author, Journal, and Topic models.
"""
from django.contrib import admin
from ..models import Author, Journal, Topic


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = [
        "last_name",
        "first_name",
        "orcid",
        "affiliation",
        "h_index",
        "total_citations",
    ]
    list_filter = ["created_at", "h_index"]
    search_fields = ["first_name", "last_name", "orcid", "email", "affiliation"]
    ordering = ["last_name", "first_name"]


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "abbreviation",
        "issn",
        "publisher",
        "impact_factor",
        "open_access",
    ]
    list_filter = ["open_access", "publisher", "impact_factor"]
    search_fields = ["name", "abbreviation", "issn", "publisher"]


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "paper_count"]
    list_filter = ["parent"]
    search_fields = ["name", "description"]
