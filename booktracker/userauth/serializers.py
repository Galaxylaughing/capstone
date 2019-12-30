# userauth/serializers.py
                             
from rest_framework import serializers
         
from .models import User
                             
                             
class UserSerializer(serializers.ModelSerializer):
    """ serializer for the User model """

    """ pull hash_id field """
    id = serializers.CharField(source='hash_id', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username']