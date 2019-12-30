from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.contrib.auth import login, logout
from django.contrib.auth import authenticate

from .models import User
from .serializers import UserSerializer


# Create your views here.

@api_view(['POST'])
def auth_login(request, format=None):
  """
  login an existing user.
  return 401 unauthorized if user is not found.
  """

  username = request.data['username']
  password = request.data['password']
  user = authenticate(username=username, password=password)

  if user:
    login(request, user)
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)
  else:
    serializer = UserSerializer(data=request.data)
    is_valid = serializer.is_valid()
    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
