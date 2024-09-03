from django.contrib.auth.models import User
from rest_framework import serializers

from api.models import Review
from api.utils import get_thumbnail_url


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


class ReviewSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)

    def get_thumbnail(self, obj):
        thumbnail_key = obj.image.name.split('/')[-1]
        return get_thumbnail_url(thumbnail_key)

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['author', 'date_posted']
