from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Invite,PasswordReset


# --------------------------
# User Forms
# --------------------------

class ATSUserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "role")


class ATSUserUpdateForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "role")


# --------------------------
# User Admin Configuration
# --------------------------
class ATSUserAdmin(UserAdmin):
    add_form = ATSUserCreateForm
    form = ATSUserUpdateForm
    model = User

    ordering = ("email",)

    list_display = ("email", "first_name", "last_name", "role", "is_active")
    list_filter = ("role", "is_active")

    fieldsets = (
        ("Login Credentials", {"fields": ("email", "password")}),
        ("Personal Details", {"fields": ("first_name", "last_name")}),
        ("Access Controls", {"fields": ("role", "is_active", "is_staff", "is_superuser")}),
        ("Security", {"fields": ("must_change_password",)}),
    )

    add_fieldsets = (
        ("Create New User", {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "role", "password1", "password2"),
        }),
    )

    search_fields = ("email",)

    # -----------------------------------------
    # ❌ 1) Stop Delete (even superuser can't delete users)
    # -----------------------------------------
    def has_delete_permission(self, request, obj=None):
        return False

    # -----------------------------------------
    # ❌ 2) Remove bulk delete action
    # -----------------------------------------
    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions



# --------------------------
# Invite Admin Configuration
# --------------------------
class InviteAdminConfig(admin.ModelAdmin):
    list_display = ("email", "created_by_email", "used")
    exclude = ('created_by',)
    readonly_fields = ("created_by_email",)
    search_fields = ("email",)
    list_filter = ("used", "created_at")



admin.site.register(User, ATSUserAdmin)
admin.site.register(Invite, InviteAdminConfig)
admin.site.register(PasswordReset)
