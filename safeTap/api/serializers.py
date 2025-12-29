from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    # Read-only field to display the author's username
    author_username = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Post
        # Fields to include in the API output
        fields = ['id', 'title', 'content', 'author', 'author_username', 'created_at', 'updated_at']
        # These fields will be set automatically, not by the user in the request
        read_only_fields = ['author', 'created_at', 'updated_at']