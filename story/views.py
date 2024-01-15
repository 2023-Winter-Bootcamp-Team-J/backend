from django.contrib.admin.templatetags.admin_list import results
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from neo4j import GraphDatabase
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
from user.models import User
from story.models import Story
from neo_db.apps import NeoDbConfig
from datetime import datetime


logger = logging.getLogger(__name__)
driver = GraphDatabase.driver(settings.NEO4J_BOLT_URL, auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD))
load_dotenv()  # 이 부분이 .env 파일을 로드합니다.
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
        image_url = request.data.get('image_url')
        user_nickname = User.objects.get(id=user_id).nickname

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

        image_url = s3_upload(image_url)  # s3 업로드 후 버킷 url

        with NeoDbConfig.session_scope() as session:  # neo4j 불러오기
            child_story = [] # 자식 스토리를 저장하기 위한 배열 , 처음에는 빈 배열이다.
            child_id = [] # 자식 스토리 Id를 저장
            # Neo4j에 스토리 저장
            fields = {
                'user_nickname': user_nickname,
                'content': content,
                'is_deleted': False,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'image_url': image_url,
                'child_id': child_id,
                'child_content': child_story,
            }
            NeoDbConfig.create_story(session, fields)  # 스토리 생성한 것 neo4j 에 집어넣기
            if parent_story >= 0: # 분기 스토리일 경우 부모와의 관계 업데이트
                NeoDbConfig.create_story_relationship(session, parent_story, image_url)
                NeoDbConfig.update_child_content(session, parent_story)
                NeoDbConfig.update_child_id(session, parent_story)

        if parent_story < 0: # parent_id가 음수일 시(루트 스토리) mysql 저장
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


@swagger_auto_schema(
    method='post',
    operation_id='이미지 생성',
    operation_description='내용에 맞게 ai 이미지를 생성합니다.',
    tags=['Story'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'content': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['content'],
    ),
)
@api_view(['POST'])
def generate_image(request): # 재생성을 위해 분리함
    content = request.data.get('content', None)

    messages = []
    promptmessages = """
우리는 지금 스토리를 작성하면 이미지를 생성해주는 서비스를 진행중이야
dalle-api를 사용하여 이미지를 생성하는데, 이미지 요청문을 gpt api를 이용하여 생성하고 , 그 요청문을 dalle에게 전달하는 형식으로 진행중이야.

내가 원하는 형식은 우리가 스토리를 작성하면 이야기 속에서 핵심 키워드 (인물, 장소, 사물, 분위기, 배경 등) 를 파악하여 뒤에 키워드로 붙여줘(예시 형태: charactor: Jone, place: school) 
이 출력값은 그림 생성 요청문으로 쓰일거니까 그림 생성에 적절한 핵심 키워드들을 출력해줘야해 
그리고 키워드들을 토대로 그림 생성 요청문을 작성해. 그 요청문을 출력하도록 해
출력값은 영어로 출력하도록 해

story: 

이제 내가 이야기를 입력할거야 바로 내가 원하는 결과값만 출력하도록 해 앞 뒤 설명 필요없이 그림 생성 요청문만 출력하면 돼 story: 
"""
    #키워드는 추가 가능
    prompt_keword =  """ \n image_characteristic: "High-Definition" ,"Epic Landscape", "Clear Outlines" , "Fantasy" or "Adventure" ,"High Level of Detail", ""An old, enchanted mansion interior in the style of a classic Disney animation. The image should have vibrant colors and a magical atmosphere, with exaggerated and whimsical design elements that give it a fairy tale-like quality. There should be intricate details and a sense of wonder, akin to the settings often found in animated musical adventures." """
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

    return Response({
        'message': '이미지가 생성되었습니다.',
        'data': {
            'image_url': image_url,
        }
    }, status=status.HTTP_201_CREATED)

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
    method='get',
    operation_id='단일 스토리 조회',
    operation_description='한 스토리를 조회합니다.',
    tags=['Story'],
)
@api_view(['GET'])
def story_detail(request, story_id):
    """
    스토리 1개 조회
    """
    with NeoDbConfig.session_scope() as session:
        query = """
            MATCH (s:Story)
            WHERE ID(s) = $story_id
            RETURN s.user_nickname, s.content, s.image_url, s.child_id, s.child_content
            """
        result = session.run(query, story_id=story_id).single()

        if not result: # 존재하지 않는 경우
            return Response({
                'messeage': "스토리가 존재하지 않습니다.",
            }, status=status.HTTP_400_BAD_REQUEST)

        story_details = {
            "user_nickname": result["s.user_nickname"],
            "content": result["s.content"],
            "image_url": result["s.image_url"],
            "child_id:": result["s.child_id"],
            "child_content": result["s.child_content"]
        }

        return Response({
            'messeage': f"스토리를 조회하였습니다. [id:{story_id}]",
            'data': story_details
        }, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_id='전체 스토리 조회',
    operation_description='전체 스토리를 조회합니다.',
    tags=['Story'],
)

@api_view(['GET'])
def story_all(request, story_id):
    """
    스토리와 그 자식 스토리들을 조회 (datetime 필드 제외)
    """
    with NeoDbConfig.session_scope() as session: # 조회할 때 깊이 탐색 순서로 조회함
        query = """
            MATCH (root:Story)-[r:CHILD*0..]->(child:Story)
            WHERE ID(root) = $story_id
            RETURN ID(child) AS child_id, child.child_id, child.child_content, child.user_nickname, child.content, child.image_url
            """
        results = session.run(query, story_id=story_id).data()

        if not results:  # 존재하지 않는 경우
            return Response({
                'message': "스토리가 존재하지 않습니다.",
            }, status=status.HTTP_400_BAD_REQUEST)

        story_list = []
        for result in results:
            story_detail = {
                "story": {
                    "user_nickname": result["child.user_nickname"],
                    "story_id": result["child_id"],
                    "content": result["child.content"],
                    "image_url": result["child.image_url"],
                    "child_id": result["child.child_id"],
                    "child_content": result["child.child_content"],
                }
            }
            story_list.append(story_detail)

        return Response({
            'message': f"스토리와 자식 스토리를 조회하였습니다. [id:{story_id}]",
            'data': story_list
        }, status=status.HTTP_200_OK)

