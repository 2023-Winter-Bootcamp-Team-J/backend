# import os
# import openai
# from django.shortcuts import render
# from drf_yasg.utils import swagger_auto_schema
# from rest_framework.decorators import api_view
# from rest_framework.generics import ListCreateAPIView, DestroyAPIView, ListAPIView
#
# from user.serializers import UserCreateSerializer
# from .models import Story
# from .serializers import StorySerializer, ExtendedStorySerializer
# from user.models import User
# from rest_framework.exceptions import ValidationError
# from dotenv import load_dotenv
#
# load_dotenv()  # 이 부분이 .env 파일을 로드합니다.
#
# openai.api_key = os.getenv("GPT_API_KEY")
#
# class StoryListCreateAPIView(ListCreateAPIView):
#     queryset = Story.objects.all()
#     serializer_class = StorySerializer
#
#     def perform_create(self, serializer):
#         content = serializer.validated_data.get('content')
#
#         # AI를 사용하여 이미지 URL 생성
#         image_url = self.generate_image(content)
#
#         # 생성된 이미지 URL을 포함하여 스토리 저장 (사용자 없이)
#         serializer.save(image_url=image_url)
#
#     def generate_image(self, content):
#         # Construct a prompt for OpenAI
#         prompt = f"Generate an image related to the following story:\n{content}"
#
#         # Request image generation from OpenAI
#         response = openai.Image.create(prompt=prompt, n=1, size="256x256")
#
#         # Extract the generated image URL
#         image_url = response["data"][0]["url"]
#
#         return image_url
#
#
# class StoryDestroyAPIView(DestroyAPIView):
#     queryset = Story.objects.all()
#     serializer_class = StorySerializer
#     lookup_field = 'id'
#
#
# class AllStoriesAPIView(ListAPIView):
#     queryset = Story.objects.all()
#     serializer_class = ExtendedStorySerializer
#
#
#
#
#
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Story
from .serializers import StorySerializer, ExtendedStorySerializer
import openai
from dotenv import load_dotenv
import os

load_dotenv()  # 이 부분이 .env 파일을 로드합니다.

openai.api_key = os.getenv("GPT_API_KEY")

@swagger_auto_schema(
    method='post',
    operation_id='스토리 생성',
    operation_description='내용을 작성하여 스토리를 생성합니다.',
    tags=['Story'],
    request_body=StorySerializer,
)
@api_view(['POST'])
def story_list_create(request):
    if request.method == 'GET':
        stories = Story.objects.all()
        serializer = StorySerializer(stories, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = StorySerializer(data=request.data)
        if serializer.is_valid():
            content = serializer.validated_data.get('content')
            image_url = generate_image(content)
            serializer.save(image_url=image_url)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def generate_image(content):
    # Construct a prompt for OpenAI
    prompt = f"Generate an image related to the following story:\n{content}"
    # Request image generation from OpenAI
    response = openai.Image.create(prompt=prompt, n=1, size="256x256")
    # Extract the generated image URL
    image_url = response["data"][0]["url"]
    return image_url

@swagger_auto_schema(
    method='delete',
    operation_id='시나리오 삭제',
    operation_description='시나리오를 삭제합니다',
    tags=['Story'],
)
@api_view(['DELETE'])
def story_destroy(request, id):
    try:
        story = Story.objects.get(id=id)
    except Story.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        story.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@swagger_auto_schema(
    method='get',
    operation_id='시나리오 전체 조회',
    operation_description='전체 시나리오를 조회합니다.',
    tags=['Story'],
)
@api_view(['GET'])
def all_scenario(request):
    if request.method == 'GET':
        stories = Story.objects.all()
        serializer = ExtendedStorySerializer(stories, many=True)
        return Response(serializer.data)
