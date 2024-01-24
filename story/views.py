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
from .tasks import generate_image_async

logger = logging.getLogger(__name__)
driver = GraphDatabase.driver(settings.NEO4J_BOLT_URL, auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD))
load_dotenv()  # 이 부분이 .env 파일을 로드합니다.
openai.api_key = os.getenv("GPT_API_KEY")

@swagger_auto_schema(
    method='get',
    operation_id='모든 루트 스토리 조회',
    operation_description='모든 루트 스토리를 조회합니다.\n\nstory_id는 neo4j의 스토리 아이디 입니다.',
    tags=['Story'],
)
@swagger_auto_schema(
    method='post',
    operation_id='스토리 생성',
    operation_description='내용을 작성하여 스토리를 생성합니다.\n\n루트 스토리인 경우, parent_story를 음수로 설정해야합니다. 분기 스토리일 경우에는 분기를 만들 스토리의 아이디가 들어가야합니다.\n\nresponse_body의 id는 스토리의 아이디를 의미합니다.',
    tags=['Story'],
    request_body=StoryCreateSerializer,
)
@api_view(['GET', 'POST'])
def story_list_create(request, *args, **kwargs):
    if request.method == 'GET': # 모든 루트 스토리 조회
        stories = Story.objects.all()
        # neo4j 아이디 가져오기
        with NeoDbConfig.session_scope() as session:
            for story in stories:
                story.story_id = NeoDbConfig.get_story_id(session, story.image_url)

        serializer = ExtendedStorySerializer(stories, many=True)
        return Response({
            "message": "모든 루트 스토리를 조회했습니다.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

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
            story_id = NeoDbConfig.get_story_id(session, image_url)
            if parent_story >= 0: # 분기 스토리일 경우 부모와의 관계 업데이트
                NeoDbConfig.create_story_relationship(session, parent_story, image_url)
                NeoDbConfig.update_child_content(session, parent_story)
                NeoDbConfig.update_child_id(session, parent_story)

        if parent_story < 0: # parent_id가 음수일 시(루트 스토리) mysql 저장
            story = Story.objects.create(user_id=user_id, content=content, image_url=image_url)
            story.story_id = story_id # neo4j 스토리 아이디
            mysqlstory = ExtendedStorySerializer(story)
            logger.error("mysqlstory: ", mysqlstory)
            return Response({
                'message': '루트 스토리가 생성되었습니다.',
                'data': mysqlstory.data
                }, status=status.HTTP_201_CREATED)

        return Response({
            'message': '분기 스토리가 생성되었습니다.',
            'data': {
                'story_id': story_id,
                'content': content,
                'image_url': image_url,
            }
        }, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='post',
    operation_id='이미지 생성 요청',
    operation_description='내용에 맞게 ai 이미지를 생성합니다.\n\n반환되는 URL은 임시이며, 버킷에 저장되는 URL은 스토리 생성 이후 생성됩니다.',
    tags=['Story'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'content': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['content'],
    ),
)
@swagger_auto_schema(
    method='get',
    operation_id='생성된 이미지 조회',
    operation_description='생성 요청된 이미지를 조회합니다.',
    tags=['Story'],
    manual_parameters=[
        openapi.Parameter('task_id', openapi.IN_QUERY, description="Task ID", type=openapi.TYPE_STRING, required=True)
    ]
)
@api_view(['GET', 'POST'])
def generate_image(request): # 비동기적 이미지 생성
    if request.method == 'POST': #이미지 생성 비동기요청
        content = request.data.get('content', None)
        if content:
            task = generate_image_async.delay(content) # 비동기식 task를 여기서 호출
            return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'error': 'No content provided'}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET': #생성된 이미지 조회
        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response({'error' : 'Task ID required'}, status=status.HTTP_400_BAD_REQUEST)

        task = generate_image_async.AsyncResult(task_id)
        if task.state == 'SUCCESS':
            return Response({'status': task.state, 'image_url': task.result})
        elif task.state == 'FAILURE':
            return Response({'status': task.state, 'error': str(task.result)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': task.state})

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
            "child_id": result["s.child_id"],
            "child_content": result["s.child_content"]
        }

        return Response({
            'messeage': f"스토리를 조회하였습니다. [id:{story_id}]",
            'data': story_details
        }, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_id='전체 스토리 조회',
    operation_description='전체 스토리를 조회합니다.\n\n스토리는 깊이 탐색 순서로 나열 됩니다.',
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

