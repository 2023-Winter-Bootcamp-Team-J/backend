import openai
from rest_framework import serializers

from user.models import User
from .models import Story

class StorySerializer(serializers.ModelSerializer):
    content = serializers.CharField(write_only=True)  # Keep the write-only content field

    class Meta:
        model = Story
        fields = ['id', 'content', 'image_url', 'created_at', 'updated_at', 'is_deleted']
        read_only_fields = ['image_url']  # Keep image_url as read-only

    def create(self, validated_data):
        story = Story.objects.create(**validated_data)
        return story


class ExtendedStorySerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id')
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    class Meta:
        model = Story
        fields = ['id', 'user_id', 'user_nickname', 'content', 'image_url']

    def validate_content(self, value):
        """
        내용 공백 검사
        """
        if not value:  # 내용이 없는 경우
            raise serializers.ValidationError('내용을 입력하세요.')