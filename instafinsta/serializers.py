from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField( read_only=True)
    class Meta:
        model = Profile
        fields = ['id', 'user', 'bio', 'avatar', 'followers', 'following']
class ProfileUpdateSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False)
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']
class ProfileDetailSerializer(serializers.ModelSerializer):
    profile = serializers.CharField(source='bio', read_only=True)
    class Meta:
        model = Profile
        fields = ['id', 'user', 'profile', 'avatar', 'followers', 'following']