# Update your api/admin.py file
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import UserProfile, ProductFeature

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'role', 'is_phone_verified')
    list_filter = ('role', 'is_phone_verified')
    search_fields = ('user__username', 'user__email', 'phone')
    readonly_fields = ('support_link', 'qr_code_preview')
    
    def qr_code_preview(self, obj):
        if obj.qr_code:
            return mark_safe(f'<img src="data:image/png;base64,{obj.qr_code}" width="100" height="100" />')
        return "No QR Code"
    qr_code_preview.short_description = 'QR Code'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'phone', 'role', 'is_phone_verified')
        }),
        ('Support Information', {
            'fields': ('support_link', 'qr_code_preview'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Auto-assign admin role to staff users"""
        if request.user.is_staff and not change:
            # Optionally auto-set role for new users created from admin
            pass
        super().save_model(request, obj, form, change)

@admin.register(ProductFeature)
class ProductFeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'id')
    search_fields = ('title', 'description')