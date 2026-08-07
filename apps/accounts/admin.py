from django.contrib import admin
from apps.accounts.models import Organization, Branch, Position, User, UserSession

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'organization', 'status')

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'status')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'full_name', 'role', 'status')
    search_fields = ('username', 'full_name', 'phone')

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
