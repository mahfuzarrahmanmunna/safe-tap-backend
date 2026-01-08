# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CityViewSet, TechSpecViewSet, DivisionViewSet, 
    DistrictViewSet, ThanaViewSet, post_list, bangladesh_data, CustomAuthToken
)

router = DefaultRouter()
router.register(r'cities', CityViewSet)
router.register(r'tech-specs', TechSpecViewSet)
# Register the new viewsets
router.register(r'divisions', DivisionViewSet)
router.register(r'districts', DistrictViewSet)
router.register(r'thanas', ThanaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('posts/', post_list, name='post-list'),
    path('bangladesh-data/', bangladesh_data, name='bangladesh-data'),
    path('auth/token/', CustomAuthToken.as_view(), name='api_token_auth'),
]