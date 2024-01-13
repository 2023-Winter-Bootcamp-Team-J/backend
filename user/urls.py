from django.urls import path

from user import views

app_name = 'user'

urlpatterns = [
    path('', views.create_nickname, name='create-nickname')
]