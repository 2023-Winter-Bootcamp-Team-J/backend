from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from .serializers import ExtendedStorySerializer, StoryCreateSerializer
import os
import uuid

import boto3
import openai
import requests
from rest_framework import status, serializers
from rest_framework.response import Response

from backend import settings
from dotenv import load_dotenv
import logging
from neo_db.models import Story as NeoStory
from story.models import Story
from neo_db.apps import NeoDbConfig
from datetime import datetime
logger = logging.getLogger(__name__)

load_dotenv()  # env 파일 로드

openai.api_key = os.getenv("GPT_API_KEY")

@swagger_auto_schema(
    method='get',
    operation_id='시나리오 전체 조회',
    operation_description='전체 시나리오를 조회합니다.',
    tags=['Story'],
)
@swagger_auto_schema(
    method='post',
    operation_id='스토리 생성',
    operation_description='내용을 작성하여 스토리를 생성합니다.',
    tags=['Story'],
    request_body=StoryCreateSerializer,
)
@api_view(['GET', 'POST'])
def story_list_create(request, *args, **kwargs):
    if request.method == 'GET':
        stories = Story.objects.all()
        serializer = ExtendedStorySerializer(stories, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        """
        스토리 생성
        """
        parent_story = request.data.get('parent_story') # 부모 스토리 아이디
        content = request.data.get('content')
        user_id = request.data.get('user_id')

        # 내용 공백 검사
        serializer = StoryCreateSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            logger.error("e: ", e)
            error_message = {
                "error": e.detail["content"][0],
                "error_code": e.get_codes()["content"][0]
            }
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

        temp_url = generate_image(content)  # ai 이미지 생성 후 임시 url
        image_url = s3_upload(temp_url)  # s3 업로드 후 버킷 url

        with NeoDbConfig.session_scope() as session:  # neo4j 불러오기
            # Neo4j에 스토리 저장
            fields = {
                'content': content,
                'is_deleted': False,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'image_url': image_url,
            }
            NeoDbConfig.create_story(session, fields)  # 스토리 생성한 것 neo4j 에 집어넣기
            if parent_story >= 0:
                NeoDbConfig.create_story_relationship(session, parent_story, image_url)

        if parent_story < 0: # parent_id가 0일 시(루트 스토리) mysql 저장
            story = Story.objects.create(user_id=user_id, content=content, image_url=image_url)
            mysqlstory = ExtendedStorySerializer(story)
            logger.error("mysqlstory: ", mysqlstory)
            return Response({
                'message': '루트 스토리가 생성되었습니다.',
                'data': mysqlstory.data}, status=status.HTTP_201_CREATED)

        return Response({
            'message': '분기 스토리가 생성되었습니다.',
            'data': {
                'content': content,
                'image_url': image_url,
            }
        }, status=status.HTTP_201_CREATED)


def generate_image(content):

    messages = []
    promptmessages = "이야기를 기반으로 dall-e api 기반으로 그림을 생성하는 서비스야. 내가 이야기를 작성하면 너가 장면이나 인물 묘사를 훨씬 구체적으로 영어로 변경해주고 이야기와 구체적 묘사들을 영어로 바꿔서 출력해줘. 그리고 너가 생각하기에 그림의 중요 포인트들을 문장 맨 뒤에 키워드로 추가해줘. 사람과 관련된 키워드가 나오면 인물이 들어가도록 키워드에 추가해줘. 날씨나 분위기에 대한 키워드가 너오면 그것도 추가해줘\n"
    #키워드는 추가 가능
    prompt_keword = ""
    # """"Detailed textures", "High resolution", "Dynamic lighting", "Cinematic composition", "Storytelling elements", "Suspenseful atmosphere", "Immersive environment", "Visual storytelling","Sophisticated Style", "Modern Feel","realistic", "fine work",  """

    story_content = promptmessages+content
    messages.append({"role": "user", "content": story_content})

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    assistant_response = completion['choices'][0]['message']['content'] + prompt_keword


    messages.append({"role": "assistant", "content": assistant_response})

    prompt = assistant_response[0:999] # 프롬프트가 1000자가 최대이므로

    response = openai.Image.create(prompt=prompt, n=1, size="256x256") # gpt에게 받은 프롬프팅을 전달하여 그림생성
    image_url = response["data"][0]["url"]

    return image_url  # 임시로 이미지 url을 리턴하도록 설정

def s3_upload(image_url):  # 생성한 이미지를 s3에 저장
    # 이미지 다운로드
    image = requests.get(image_url)

    # S3 클라이언트 생성
    s3_client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                             region_name=settings.AWS_REGION)

    # 이미지를 S3에 업로드
    unique_url = f'{uuid.uuid4()}.jpeg' # 파일 명을 고유한 값으로 지정
    image_url = f'{settings.MEDIA_URL}{unique_url}' # db에 들어갈 접근 가능한 url
    s3_client.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=unique_url,
        Body=image.content,
        ContentType="image/jpeg", # 이미지의 적절한 Content-Type 지정
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