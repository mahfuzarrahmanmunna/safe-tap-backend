from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Post
from .serializers import PostSerializer
from django.http import HttpResponse

def home(request):
    return HttpResponse('hello api')

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated]) # Only logged-in users can access this
def post_list(request):
    """
    List all posts, or create a new post.
    """
    if request.method == 'GET':
        # Handle GET request: Retrieve all posts
        posts = Post.objects.all().order_by('-created_at')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Handle POST request: Create a new post
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            # Automatically set the author to the logged-in user
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
