"""
Django admin customization
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users"""
    ordering = ["email", ]
    list_display = ["email", "name"]
    fieldsets = (
        (
            None,
            {'fields': ('name', 'email', 'password', 'phone')},
        ),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser', )},
        ),
        (
            _('Important Dates'),
            {'fields': ('last_login', )},
        )
    )
    readonly_fields = ['last_login', ]
    add_fieldsets = (
        (
            None,
            {'fields': (
                'name',
                'email',
                'password1',
                'password2',
                'name',
                'phone',
                'is_active',
                'is_staff',
                'is_superuser',
            )}
        ),
    )


class SectorAdmin(admin.ModelAdmin):
    """Define admin page for Sector"""
    ordering = ['name']
    list_display = ['id', 'name', 'created_by']
    fieldsets = [
        (
            None,
            {'fields': ['id', 'name', 'created_by']},
        ),
    ]
    readonly_fields = ['id', 'created_by']
    add_fieldsets = (
        (
            None,
            {'fields': (
                'name',
            )}
        ),
    )

    def save_model(self, request, obj, form, change):
        obj.name = obj.name.lower()
        # Perform case-insensitive check for unique name
        if models.Sector.objects.filter(
                    name__iexact=obj.name).exclude(pk=obj.pk).exists():
            raise ValidationError(
                _("A sector with the name '%(value)s' already exists."),
                params={'value': obj.name},
            )
        if not obj.created_by:
            obj.created_by = request.user
        return super().save_model(request, obj, form, change)


class SkillAdmin(admin.ModelAdmin):
    """Define admin page for Sector"""
    ordering = ['name']
    list_display = ['id', 'name', 'created_by']
    fieldsets = [
        (
            None,
            {'fields': ['id', 'name', 'sectors', 'created_by']},
        ),
    ]
    readonly_fields = ['id', 'created_by']
    add_fieldsets = (
        (
            None,
            {'fields': (
                'name',
                'sectors',
            )}
        ),
    )
    filter_horizontal = ['sectors']

    def save_model(self, request, obj, form, change):
        obj.name = obj.name.lower()
        # Perform case-insensitive check for unique name
        if models.Skill.objects.filter(
                    name__iexact=obj.name).exclude(pk=obj.pk).exists():
            raise ValidationError(
                _("A sector with the name '%(value)s' already exists."),
                params={'value': obj.name},
            )
        if not obj.created_by:
            obj.created_by = request.user
        obj.full_clean()
        super().save_model(request, obj, form, change)


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Sector, SectorAdmin)
admin.site.register(models.Skill, SkillAdmin)
