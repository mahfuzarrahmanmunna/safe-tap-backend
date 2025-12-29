from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='api-home'),
     path('posts/', views.post_list, name='post-list'),
]
