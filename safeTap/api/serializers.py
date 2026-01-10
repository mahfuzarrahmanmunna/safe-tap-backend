# api/serializers.py
from rest_framework import serializers
from .models import Post, City, CitySlide, CityStats, Product, TechSpec, Division, User, District, Thana, ProductFeature, UserProfile

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


class ProductFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFeature
        fields = ['id', 'title', 'description', 'image']
        
        
# Authentication and User Related Serializers
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=15)
    role = serializers.ChoiceField(choices=['customer', 'service_man', 'admin'], required=False, default='customer')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'phone', 'role')
    
    def create(self, validated_data):
        phone = validated_data.pop('phone')
        role = validated_data.pop('role', 'customer')
        password = validated_data.pop('password')
        
        # Create user
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create user profile with role
        profile = UserProfile.objects.create(user=user, phone=phone, role=role)
        
        return user

class PhoneVerificationSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    
    def validate_phone(self, value):
        if not UserProfile.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number not registered")
        return value

class CodeVerificationSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6)
    
    def validate(self, attrs):
        phone = attrs.get('phone')
        code = attrs.get('code')
        
        try:
            profile = UserProfile.objects.get(phone=phone)
            if profile.verification_code != code:
                raise serializers.ValidationError("Invalid verification code")
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError("Phone number not registered")
        
        return attrs

class SupportLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('support_link', 'qr_code')