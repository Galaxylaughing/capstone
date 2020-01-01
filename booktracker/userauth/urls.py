from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path('login/', views.auth_login, name='login'), #unused
    path('signup/', views.signup, name='signup'),
    path('logout/', views.auth_logout, name="logout"),
    path('auth-token/', obtain_auth_token, name="get-auth-token"),
    path('helloworld/', views.helloworld, name="helloworld"),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json'])
