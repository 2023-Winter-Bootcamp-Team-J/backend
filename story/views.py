from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from .models import Story
from .serializers import StorySerializer
from user.models import User
from rest_framework.exceptions import ValidationError

class StoryListCreateAPIView(ListCreateAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer

    def perform_create(self, serializer):
        nickname = serializer.validated_data.get('nickname')
        user = User.objects.get(nickname=nickname)
        serializer.save(user=user)


class StoryDestroyAPIView(DestroyAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    lookup_field = 'id'