from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('books/', views.get_books, name="get_books"),
    path('books/<int:book_id>/', views.get_book, name="get_book")
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json'])
