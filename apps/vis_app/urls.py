from django.urls import path
from . import views, api_views

app_name = "vis"

urlpatterns = [
    # Main editor
    path(
        "",
        views.figure_editor,
        name="figure_editor",
    ),
    # Figure management
    path(
        "figures/",
        views.figure_list,
        name="figure_list",
    ),
    path(
        "figures/create/",
        views.create_figure,
        name="create_figure",
    ),
    path(
        "figures/<uuid:figure_id>/",
        views.figure_detail,
        name="figure_detail",
    ),
    # API endpoints
    path(
        "api/presets/",
        api_views.get_journal_presets,
        name="api_presets",
    ),
    path(
        "api/presets/<int:preset_id>/",
        api_views.get_preset_detail,
        name="api_preset_detail",
    ),
    path(
        "api/figures/<uuid:figure_id>/save/",
        api_views.save_figure_state,
        name="api_save_figure",
    ),
    path(
        "api/figures/<uuid:figure_id>/load/",
        api_views.load_figure_state,
        name="api_load_figure",
    ),
    path(
        "api/figures/<uuid:figure_id>/upload-panel/",
        api_views.upload_panel_image,
        name="api_upload_panel",
    ),
    path(
        "api/figures/<uuid:figure_id>/config/",
        api_views.update_figure_config,
        name="api_update_config",
    ),
]
