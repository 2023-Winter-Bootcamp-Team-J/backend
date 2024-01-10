from django.urls import path
from .views import StoryListCreateAPIView, StoryDestroyAPIView

urlpatterns = [
    path('', StoryListCreateAPIView.as_view(), name='story-list-create'),
    path('<int:id>/', StoryDestroyAPIView.as_view(), name='story-destroy'),  # 삭제 경로 추가
]



