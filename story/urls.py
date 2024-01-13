from django.urls import path
from .views import story_list_create, story_destroy, all_scenario

urlpatterns = [
    path('stories/', story_list_create, name='story-list-create'),
    path('stories/<int:id>/', story_destroy, name='story-destroy'),
]