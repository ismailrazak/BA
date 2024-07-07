from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Patient, Doctor,BlogPost,Category

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'is_staff', 'is_active', 'is_patient', 'is_doctor')
    list_filter = ('is_staff', 'is_active', 'is_patient', 'is_doctor')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_patient', 'is_doctor')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active', 'is_patient', 'is_doctor')}
        ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile)
admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(BlogPost)
admin.site.register(Category)