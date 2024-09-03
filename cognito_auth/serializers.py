from rest_framework import serializers
from rest_framework.serializers import Serializer


class CognitoUserSerializer(Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class TokenSerializer(Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()





