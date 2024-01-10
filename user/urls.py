from django.urls import path

from user import views

app_name = 'user'

urlpatterns = [
    path('', views.index),
    path('/nickname', views.create_nickname)
]