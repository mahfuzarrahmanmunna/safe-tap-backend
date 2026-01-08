# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CityViewSet, TechSpecViewSet, post_list, home, CustomAuthToken

router = DefaultRouter()
router.register(r'cities', CityViewSet, basename='city')
router.register(r'tech-specs', TechSpecViewSet, basename='techspec')

urlpatterns = [
    path('', home),
    path('posts/', post_list, name='post-list'),
    path('auth/token/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('', include(router.urls)),
]