from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('books/', views.books, name="books"),
    path('books/<int:book_id>/', views.book, name="book")
    # path('books/', views.post_books, name="post_books")
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json'])
