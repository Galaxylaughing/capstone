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
    return Response('Account not found', status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def signup(request):
  """
  return 403 forbidden if user is already present.
  create new user otherwise.
  """

  username = request.data['username']
  password = request.data['password']

  # filter() returns a QuerySet
  filteredUsers = User.objects.filter(username=username)
  # exists() returns True if the QuerySet contains any results, and False if not
  if filteredUsers.exists():
    return Response('Account already exists', status=status.HTTP_403_FORBIDDEN)
  else:
    # create new user
    new_user = User(username=username)
    new_user.set_password(request.data['password'])
    new_user.save()
    # login the new user
    login(request, new_user)
    # return the new user's data
    serializer = UserSerializer(new_user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
