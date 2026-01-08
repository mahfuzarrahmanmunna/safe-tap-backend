# api/serializers.py
from rest_framework import serializers
from .models import City, CitySlide, CityStats, Product, TechSpec, Post

class CitySlideSerializer(serializers.ModelSerializer):
    class Meta:
        model = CitySlide
        fields = ['id', 'title', 'subtitle', 'description', 'image', 'color']

class CityStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityStats
        fields = ['users', 'rating', 'installations']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'price', 'features', 'description']

class CitySerializer(serializers.ModelSerializer):
    slides = CitySlideSerializer(many=True, read_only=True)
    stats = CityStatsSerializer(read_only=True)
    products = ProductSerializer(many=True, read_only=True)
    
    class Meta:
        model = City
        fields = ['id', 'name', 'slug', 'slides', 'stats', 'products']

class TechSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechSpec
        fields = ['id', 'icon_name', 'title', 'details']

class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'author_name', 'created_at', 'updated_at']
        read_only_fields = ['author', 'created_at', 'updated_at']