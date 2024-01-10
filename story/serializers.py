from rest_framework import serializers

from user.models import User
from .models import Story

class StorySerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(write_only=True)

    class Meta:
        model = Story
        fields = ['id', 'nickname', 'content', 'image_url', 'created_at', 'updated_at', 'is_deleted']

    def validate_nickname(self, value):
        if not User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("존재하지 않는 닉네임입니다.")
        return value

    def create(self, validated_data):
        validated_data.pop('nickname', None)
        return Story.objects.create(**validated_data)
