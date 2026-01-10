# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CityViewSet, TechSpecViewSet, DivisionViewSet, 
    DistrictViewSet, ThanaViewSet, post_list, bangladesh_data, CustomAuthToken, ProductFeatureViewSet,
    register_user, send_verification_code, verify_code, get_support_info
)

router = DefaultRouter()
router.register(r'cities', CityViewSet)
router.register(r'tech-specs', TechSpecViewSet)
# Register the new viewsets
router.register(r'divisions', DivisionViewSet)
router.register(r'districts', DistrictViewSet)
router.register(r'thanas', ThanaViewSet)
router.register(r'product-features', ProductFeatureViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('posts/', post_list, name='post-list'),
    path('bangladesh-data/', bangladesh_data, name='bangladesh-data'),
    path('auth/token/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('auth/register/', register_user, name='register_user'),
    path('auth/send-code/', send_verification_code, name='send_verification_code'),
    path('auth/verify-code/', verify_code, name='verify_code'),
    path('auth/support-info/', get_support_info, name='get_support_info'),
]