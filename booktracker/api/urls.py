from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('books/', views.books, name="books"),
    path('books/<int:book_id>/', views.book, name="book"),
    path('series/', views.series, name="series_list")
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json'])
