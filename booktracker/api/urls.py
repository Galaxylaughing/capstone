from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('books/', views.get_books, name="get_books"),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json'])
