from rest_framework import serializers
from .models import Story

class StorySerializer(serializers.ModelSerializer): # neo4j 스토리 1개 조회 시 사용
    # content = serializers.CharField(write_only=True)  # Keep the write-only content field

    class Meta:
        model = Story
        fields = ['id', 'content', 'image_url', 'created_at', 'updated_at', 'is_deleted']
        # fields = ['id', 'content', 'image_url', 'created_at', 'updated_at', 'is_deleted']
        # read_only_fields = ['image_url']  # Keep image_url as read-only

    # def create(self, validated_data):
    #     story = Story.objects.create(**validated_data)
    #     return story

class StoryCreateSerializer(serializers.ModelSerializer): # 스토리 생성 시 request_body 용
    user_id = serializers.IntegerField(source='user.id')
    parent_story = serializers.IntegerField()

    class Meta:
        model = Story
        fields = ['id', 'user_id', 'content', 'parent_story']

    def validate_content(self, value):
        """
        내용 공백 검사
        """
        if not value:  # 내용이 없는 경우
            raise serializers.ValidationError('내용을 입력하세요.')


class ExtendedStorySerializer(serializers.ModelSerializer): # 생성 후 response, 전체 시나리오 조회 시 사용
    user_id = serializers.IntegerField(source='user.id')
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    class Meta:
        model = Story
        fields = ['id', 'user_id', 'user_nickname', 'content', 'image_url']

