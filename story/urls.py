from django.urls import path
from .views import story_list_create, story_detail, story_all, generate_image

urlpatterns = [
    path('stories/', story_list_create, name='story-list-create'),
    path('stories/images', generate_image, name='generate-image'),
    path('stories/<int:story_id>/', story_detail, name='story-detail'),
    path('stories/branches/<int:story_id>/', story_all, name='story-all')
]

