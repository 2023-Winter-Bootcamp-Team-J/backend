from django.shortcuts import render

# Create your views here.
from rest_framework import views, status
from rest_framework.response import Response
from .models import Story, User
from .serializers import StorySerializer, UserSerializer
from neo4j import GraphDatabase
import backend.mysettings as mysettings  # mysettings를 임포트합니다.

# Neo4j 드라이버 생성
# mysettings에서 설정을 로드합니다.
driver = GraphDatabase.driver(mysettings.NEO4J_BOLT_URL, auth=(mysettings.NEO4J_USERNAME, mysettings.NEO4J_PASSWORD))

class StoryView(views.APIView):
    def post(self, request):
        serializer = StorySerializer(data=request.data)
        if serializer.is_valid():
            story = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, story_id=None):
        if story_id:
            try:
                story = Story.nodes.get(story_id=story_id)
                serializer = StorySerializer(story)
                return Response(serializer.data)
            except Story.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            stories = Story.nodes.all()
            serializer = StorySerializer(stories, many=True)
            return Response(serializer.data)

class UserView(views.APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, user_id=None):
        if user_id:
            try:
                user = User.nodes.get(user_id=user_id)
                serializer = UserSerializer(user)
                return Response(serializer.data)
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            users = User.nodes.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
