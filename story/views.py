import os
import openai
from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from .models import Story
from .serializers import StorySerializer
from user.models import User
from rest_framework.exceptions import ValidationError

class StoryListCreateAPIView(ListCreateAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer

    def perform_create(self, serializer):
        content = serializer.validated_data.get('content')

        # AI를 사용하여 이미지 URL 생성
        image_url = self.generate_image(content)

        # 생성된 이미지 URL을 포함하여 스토리 저장 (사용자 없이)
        serializer.save(image_url=image_url)

    def generate_image(self, content):
        # Construct a prompt for OpenAI
        prompt = f"Generate an image related to the following story:\n{content}"

        # Request image generation from OpenAI
        response = openai.Image.create(prompt=prompt, n=1, size="256x256")

        # Extract the generated image URL
        image_url = response["data"][0]["url"]

        return image_url


class StoryDestroyAPIView(DestroyAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    lookup_field = 'id'
