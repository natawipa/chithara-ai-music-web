from django.urls import path

from api.views.auth_controller import google_callback, login, logout, me
from api.views.generation_controller import cancel, create, status
from api.views.library_controller import filter_songs, list_songs, search_songs
from api.views.sharing_controller import access, share
from api.views.song_controller import delete, set_privacy, update, upload_cover
from api.views.suno_callback_controller import suno_callback

urlpatterns = [
    # Auth
    path("api/auth/login/", login, name="auth_login"),
    path("api/auth/google/callback/", google_callback, name="auth_google_callback"),
    path("api/auth/logout/", logout, name="auth_logout"),
    path("api/auth/me/", me, name="auth_me"),

    # Generation
    path("api/generate/", create, name="generate_create"),
    path("api/generate/<int:id>/status/", status, name="generate_status"),
    path("api/generate/<int:id>/cancel/", cancel, name="generate_cancel"),

    # Song management
    path("api/songs/<int:id>/update/", update, name="song_update"),
    path("api/songs/<int:id>/delete/", delete, name="song_delete"),
    path("api/songs/<int:id>/privacy/", set_privacy, name="song_set_privacy"),
    path("api/songs/<int:id>/upload-cover/", upload_cover, name="song_upload_cover"),
    path("api/songs/<int:id>/share/", share, name="song_share"),

    # Library
    path("api/songs/", list_songs, name="song_list"),
    path("api/songs/filter/", filter_songs, name="song_filter"),
    path("api/songs/search/", search_songs, name="song_search"),

    # Public share access
    path("api/songs/share/<str:token>/", access, name="song_share_access"),

    # Suno webhook
    path("api/suno/callback/", suno_callback, name="suno_callback"),
]

