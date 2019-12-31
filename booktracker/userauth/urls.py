from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('login/', views.auth_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.auth_logout, name="logout"),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json'])
