import uuid
import qrcode
from io import BytesIO
import base64

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

# New models for Bangladesh geographical data
class Division(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Division"
        verbose_name_plural = "Divisions"

class District(models.Model):
    name = models.CharField(max_length=100)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='districts')
    
    def __str__(self):
        return f"{self.name}, {self.division.name}"
    
    class Meta:
        unique_together = ('name', 'division')
        verbose_name = "District"
        verbose_name_plural = "Districts"

class Thana(models.Model):
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='thanas')
    
    def __str__(self):
        return f"{self.name}, {self.district.name}"
    
    class Meta:
        unique_together = ('name', 'district')
        verbose_name = "Thana"
        verbose_name_plural = "Thanas"
        
class ProductFeature(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.URLField(max_length=500)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Product Feature'
        verbose_name_plural = "Product Features"
        
        
        
# Authentication related model
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('service_man', 'Service Man'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    is_phone_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    support_link = models.URLField(max_length=255, blank=True, null=True)
    qr_code = models.TextField(blank=True, null=True)  # Store base64 encoded QR code
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
    def generate_support_link(self):
        if not self.support_link:
            unique_id = str(uuid.uuid4())
            self.support_link = f"https://yourapp.com/support/{unique_id}"
            self.save()
        return self.support_link
    
    def generate_qr_code(self):
        if not self.qr_code and self.support_link:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(self.support_link)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()
            self.qr_code = img_str
            self.save()
        return self.qr_code

# Add a signal to create UserProfile when a User is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)