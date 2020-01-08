from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('books/', views.books, name="books"),
    path('books/<int:book_id>/', views.book, name="book"),
    path('series/', views.all_series, name="series_list"),
    path('series/<int:series_id>/', views.one_series, name="series_details"),
    path('tags/', views.tags, name="tags"),
    path('tags/<str:tag_name>', views.tag, name="tag"),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json'])
