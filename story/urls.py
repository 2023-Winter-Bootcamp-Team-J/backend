from django.urls import path
from .views import story_list_create, story_detail, story_all

urlpatterns = [
    path('stories/', story_list_create, name='story-list-create'),
    path('stories/<int:story_id>/', story_detail, name='story-detail'),
    path('storiess/<int:story_id>/', story_all, name='story-all')
]

