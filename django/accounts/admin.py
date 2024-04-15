from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        'email',
        'id',
        'name',
        'is_active',
        'is_staff',
    ]
    # fields = list_display
    # fieldsets = UserAdmin.fieldsets + ((None, {'fields': ('name',)}),)
    # add_fieldsets = UserAdmin.add_fieldsets + ((None, {'fields': ('name',)}),)


# add_fieldsets = (
#     (None, {
#         'classes': ('wide',),
#         'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
#     }),
# )

admin.site.register(CustomUser, CustomUserAdmin)
