# api/models.py
from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class CitySlide(models.Model):
    city = models.ForeignKey('City', related_name='slides', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200)
    description = models.TextField()
    image = models.CharField(max_length=200)  # URL or path to image
    color = models.CharField(max_length=50)  # CSS gradient classes
    
    def __str__(self):
        return f"{self.city.name} - {self.title}"

class CityStats(models.Model):
    city = models.OneToOneField('City', related_name='stats', on_delete=models.CASCADE)
    users = models.CharField(max_length=50)
    rating = models.CharField(max_length=10)
    installations = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.city.name} Stats"

class Product(models.Model):
    city = models.ForeignKey('City', related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price = models.CharField(max_length=50)
    features = models.JSONField()  # Using JSONField for features array
    description = models.TextField()
    
    def __str__(self):
        return f"{self.city.name} - {self.name}"

class TechSpec(models.Model):
    icon_name = models.CharField(max_length=50)  # Store icon name like "Shield", "Zap"
    title = models.CharField(max_length=200)
    details = models.CharField(max_length=200)
    
    def __str__(self):
        return self.title