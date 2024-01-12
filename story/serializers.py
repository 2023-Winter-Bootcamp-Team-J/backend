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
        # Directly create a Story object without a user
        story = Story.objects.create(**validated_data)
        return story

    # Generate image function remains the same
    def generate_image(self, content):
        # 기존의 promptmessages와 prompt_keword를 유지합니다.
        promptmessages = "이야기를 기반으로 dall-e api 기반으로 그림을 생성하는 서비스야. 내가 이야기를 작성하면 너가 장면이나 인물 묘사를 훨씬 구체적으로 영어로 변경해주고 이야기와 구체적 묘사들을 영어로 바꿔서 출력해줘 \n"
        prompt_keword = """"Detailed textures", "High resolution", "Dynamic lighting", "Cinematic composition", 
                "Storytelling elements", "Suspenseful atmosphere", "Immersive environment", "Visual storytelling" """

        # 이야기 내용을 조합하여 프롬프트를 생성합니다.
        prompt = promptmessages + f"Story by {content}\n" + prompt_keword

        # OpenAI로부터 이미지를 생성하는 요청을 보냅니다.
        response = openai.Image.create(prompt=prompt, n=1, size="256x256")

        # 생성된 이미지의 URL을 추출합니다.
        image_url = response["data"][0]["url"]

        return image_url

class ExtendedStorySerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    class Meta:
        model = Story
        fields = ['id', 'user', 'user_nickname', 'content', 'image_url', 'created_at']
