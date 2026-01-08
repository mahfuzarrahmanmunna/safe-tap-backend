# api/views.py
from django.http import HttpResponse
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from .models import Post, City, TechSpec, Division, District, Thana
from .serializers import (
    CitySerializer, CitySlideSerializer, CityStatsSerializer, 
    ProductSerializer, TechSpecSerializer, PostSerializer,
    DivisionSerializer, DistrictSerializer, ThanaSerializer, BangladeshDataSerializer
)

def home(request):
    return HttpResponse('hello api')

@api_view(['GET', 'POST'])
def post_list(request):
    """
    List all posts, or create a new post.
    """
    if request.method == 'GET':
        posts = Post.objects.all().order_by('-created_at')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            # This will fail if no user is logged in. Handle this.
            if request.user.is_authenticated:
                serializer.save(author=request.user)
            else:
                # For now, let's not save if no user is authenticated
                return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_serializer_context(self): 
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=False, methods=['get', 'post'])
    def bulk(self, request):
        if request.method == 'GET':
            cities = City.objects.all()
            serializer = CitySerializer(cities, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            cities_data = request.data.get('cities', [])
            
            if not cities_data:
                return Response(
                    {"error": "No cities data provided"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            created_cities = []
            errors = []
            
            for city_data in cities_data:
                try:
                    city_serializer = CitySerializer(data={
                        'name': city_data.get('name'),
                        'slug': city_data.get('slug', city_data.get('name', '').lower())
                    })
                    
                    if city_serializer.is_valid():
                        city = city_serializer.save()
                        
                        # Create slides
                        slides_data = city_data.get('slides', [])
                        for slide_data in slides_data:
                            slide_serializer = CitySlideSerializer(data={
                                **slide_data,
                                'city': city.id
                            })
                            if slide_serializer.is_valid():
                                slide_serializer.save()
                            else:
                                errors.append({
                                    'city': city.name,
                                    'slide': slide_data.get('title', 'Unknown'),
                                    'errors': slide_serializer.errors
                                })
                        
                        # Create stats
                        stats_data = city_data.get('stats')
                        if stats_data:
                            stats_serializer = CityStatsSerializer(data={
                                **stats_data,
                                'city': city.id
                            })
                            if stats_serializer.is_valid():
                                stats_serializer.save()
                            else:
                                errors.append({
                                    'city': city.name,
                                    'stats': stats_serializer.errors
                                })
                        
                        # Create products
                        products_data = city_data.get('products', [])
                        for product_data in products_data:
                            product_serializer = ProductSerializer(data={
                                **product_data,
                                'city': city.id
                            })
                            if product_serializer.is_valid():
                                product_serializer.save()
                            else:
                                errors.append({
                                    'city': city.name,
                                    'product': product_data.get('name', 'Unknown'),
                                    'errors': product_serializer.errors
                                })
                        
                        created_cities.append(city.name)
                    else:
                        errors.append({
                            'city': city_data.get('name', 'Unknown'),
                            'errors': city_serializer.errors
                        })
                
                except Exception as e:
                    errors.append({
                        'city': city_data.get('name', 'Unknown'),
                        'error': str(e)
                    })
            
            response_data = {
                'created_cities': created_cities,
                'count': len(created_cities)
            }
            
            if errors:
                response_data['errors'] = errors
                return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

class TechSpecViewSet(viewsets.ModelViewSet):
    queryset = TechSpec.objects.all()
    serializer_class = TechSpecSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]
    
    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_bulk_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return super().create(request, *args, **kwargs)
    
    def perform_bulk_create(self, serializer):
        return TechSpec.objects.bulk_create(
            [TechSpec(**item) for item in serializer.validated_data]
        )

# New viewsets for geographical data
class DivisionViewSet(viewsets.ModelViewSet):
    queryset = Division.objects.all()
    serializer_class = DivisionSerializer
    permission_classes = [permissions.AllowAny]
    # permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['post'])
    def bulk_import(self, request):
        """
        Bulk import Bangladesh geographical data
        """
        data = request.data
        
        if not isinstance(data, list):
            return Response(
                {"error": "Data should be a list of geographical entries"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_divisions = 0
        created_districts = 0
        created_thanas = 0
        errors = []
        
        for entry in data:
            try:
                # Create or get division
                division, created = Division.objects.get_or_create(
                    name=entry['division']
                )
                if created:
                    created_divisions += 1
                
                # Create or get district
                district, created = District.objects.get_or_create(
                    name=entry['district'],
                    division=division
                )
                if created:
                    created_districts += 1
                
                # Create thanas
                for thana_name in entry['thanas']:
                    thana, created = Thana.objects.get_or_create(
                        name=thana_name,
                        district=district
                    )
                    if created:
                        created_thanas += 1
                        
            except Exception as e:
                errors.append({
                    'entry': entry.get('_id', 'Unknown'),
                    'error': str(e)
                })
        
        response_data = {
            'created_divisions': created_divisions,
            'created_districts': created_districts,
            'created_thanas': created_thanas,
            'total_entries_processed': len(data)
        }
        
        if errors:
            response_data['errors'] = errors
            return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
        
        return Response(response_data, status=status.HTTP_201_CREATED)

class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [permissions.AllowAny]
    # permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = District.objects.all()
        division_id = self.request.query_params.get('division_id', None)
        if division_id is not None:
            queryset = queryset.filter(division_id=division_id)
        return queryset

class ThanaViewSet(viewsets.ModelViewSet):
    queryset = Thana.objects.all()
    serializer_class = ThanaSerializer
    permission_classes= [permissions.AllowAny]
    # permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Thana.objects.all()
        district_id = self.request.query_params.get('district_id', None)
        if district_id is not None:
            queryset = queryset.filter(district_id=district_id)
        return queryset

@api_view(['GET'])
def bangladesh_data(request):
    """
    Get all Bangladesh geographical data
    """
    divisions = Division.objects.all()
    result = []
    
    for division in divisions:
        for district in division.districts.all():
            thanas = [thana.name for thana in district.thanas.all()]
            result.append({
                'division': division.name,
                'district': district.name,
                'thanas': thanas
            })
    
    return Response(result)