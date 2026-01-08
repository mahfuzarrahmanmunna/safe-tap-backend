# api/serializers.py
from rest_framework import serializers
from .models import Post, City, CitySlide, CityStats, Product, TechSpec, Division, District, Thana

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at']

class CitySlideSerializer(serializers.ModelSerializer):
    class Meta:
        model = CitySlide
        fields = '__all__'

class CityStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityStats
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class TechSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechSpec
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    slides = CitySlideSerializer(many=True, read_only=True)
    stats = CityStatsSerializer(read_only=True)
    products = ProductSerializer(many=True, read_only=True)
    
    class Meta:
        model = City
        fields = ['id', 'name', 'slug', 'slides', 'stats', 'products']

# New serializers for geographical data
class ThanaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thana
        fields = ['id', 'name', 'district']

class DistrictSerializer(serializers.ModelSerializer):
    thanas = ThanaSerializer(many=True, read_only=True)
    
    class Meta:
        model = District
        fields = ['id', 'name', 'division', 'thanas']

class DivisionSerializer(serializers.ModelSerializer):
    districts = DistrictSerializer(many=True, read_only=True)
    
    class Meta:
        model = Division
        fields = ['id', 'name', 'districts']

class BangladeshDataSerializer(serializers.Serializer):
    _id = serializers.CharField(max_length=20)
    division = serializers.CharField(max_length=100)
    district = serializers.CharField(max_length=100)
    thanas = serializers.ListField(child=serializers.CharField(max_length=100))