from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, Product


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('bio', 'profile_image')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительно', {'fields': ('email', 'bio', 'profile_image')}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'kaspi_url')
    list_filter = ('category',)
    search_fields = ('name', 'description')