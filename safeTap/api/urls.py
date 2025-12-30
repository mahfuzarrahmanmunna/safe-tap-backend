from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='api-home'),
    path('posts/', views.post_list, name='post-list'),
    path('auth/token/', views.CustomAuthToken.as_view(), name='api_token_auth'),
]
