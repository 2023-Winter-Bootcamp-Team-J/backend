from rest_framework import serializers
from .models import Story, User

class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ['story_id', 'content', 'createdAt', 'updatedAt', 'is_deleted', 'image_url', 'parent_story', 'child_stories']

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
    class Meta:
        model = User
        fields = ['user_id', 'nickname', 'createdAt', 'updatedAt', 'is_deleted', 'stories_written']

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.nickname = validated_data.get('nickname', instance.nickname)
        instance.updatedAt = validated_data.get('updatedAt', instance.updatedAt)
        instance.is_deleted = validated_data.get('is_deleted', instance.is_deleted)
        instance.save()
        return instance
