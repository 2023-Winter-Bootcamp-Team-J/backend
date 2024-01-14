from rest_framework import serializers

from story.serializers import StorySerializer
from .models import Story, User

class StorySerializer(serializers.ModelSerializer):
    parent_story = StorySerializer(read_only=True)
    child_stories = StorySerializer(many=True, read_only=True)

    class Meta:
        model = Story
        fields = ['story_id', 'content', 'createdAt', 'updatedAt', 'is_deleted', 'image_url', 'parent_story', 'child_stories']
        read_only_fields = ['story_id']
    def create(self, validated_data):
        return Story.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.updatedAt = validated_data.get('updatedAt', instance.updatedAt)
        instance.is_deleted = validated_data.get('is_deleted', instance.is_deleted)
        instance.image_url = validated_data.get('image_url', instance.image_url)
        instance.save()
        return instance

class UserSerializer(serializers.ModelSerializer):
    stories_written = StorySerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['user_id', 'nickname', 'createdAt', 'updatedAt', 'is_deleted', 'stories_written']
        read_only_fields = ['user_id']
    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.nickname = validated_data.get('nickname', instance.nickname)
        instance.updatedAt = validated_data.get('updatedAt', instance.updatedAt)
        instance.is_deleted = validated_data.get('is_deleted', instance.is_deleted)
        instance.save()
        return instance
