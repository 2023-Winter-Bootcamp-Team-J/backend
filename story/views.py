from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from .serializers import ExtendedStorySerializer
import os
import uuid

import boto3
import openai
import requests
from rest_framework import status
from rest_framework.response import Response

from .models import Story
from .serializers import StorySerializer
from backend import settings
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

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

            temp_url = generate_image(content) # ai 이미지 생성 후 임시 url
            image_url = s3_upload(temp_url) # s3 업로드 후 버킷 url

            serializer.save(image_url=image_url)
            return Response({
                'message': '스토리가 생성되었습니다.',
                'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({
            'message': '유효하지 않은 값입니다.',
            'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

def generate_image(content):
    # Construct a prompt for OpenAI
    prompt = f"Generate an image related to the following story:\n{content}"
    # Request image generation from OpenAI
    response = openai.Image.create(prompt=prompt, n=1, size="256x256")
    # Extract the generated image URL
    image_url = response["data"][0]["url"]
    return image_url

def s3_upload(image_url):  # 생성한 이미지를 s3에 저장
    # 이미지 다운로드
    image = requests.get(image_url)

    # S3 클라이언트 생성
    s3_client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                             region_name=settings.AWS_REGION)

    # 이미지를 S3에 업로드
    unique_url = f'{uuid.uuid4()}.jpeg'
    image_url = f'{settings.MEDIA_URL}{unique_url}'
    s3_client.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=unique_url,
        Body=image.content,
        ContentType="image/jpeg", # 이미지의 적절한 Content-Type을 지정해야 합니다.
    )

    # 업로드된 URL반환
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