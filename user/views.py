from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view

from user.models import User
from user.serializers import NicknameCreateSerializer

def index(request):
    return HttpResponse("닉네임 생성 페이지입니다.")

@swagger_auto_schema(
    method='post',
    operation_id='닉네임 생성',
    operation_description='닉네임을 이용해 유저를 생성합니다.',
    tags=['User'],
    request_body=NicknameCreateSerializer
)
@api_view(['POST'])
def create_nickname(request):
    serializer = NicknameCreateSerializer(data=request.data)
    if serializer.is_valid():
        # 닉네임 중복 검사는 모델에서 unique=True 추가하는 방법 사용
        serializer.save()
        return JsonResponse({
            'message': 'User가 성공적으로 생성되었습니다.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    return JsonResponse({
        'message': '유효하지 않은 입력값입니다.',
        'data': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)