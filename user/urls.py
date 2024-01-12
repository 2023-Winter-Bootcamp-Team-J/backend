from django.urls import path

from user import views
# from user.views import UserCreateAPIView

app_name = 'user'

urlpatterns = [
    path('create', views.create_user, name='user-create')
]