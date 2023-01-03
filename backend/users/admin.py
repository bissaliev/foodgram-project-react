from django.contrib import admin

from .models import Subscribe, User

EMPTY = '-пусто-'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name']
    search_fields = ['username', 'email']
    list_filter = ['username', 'email']
    ordering = ['username']
    empty_value_display = EMPTY


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ['subscriber', 'author']
    search_fields = [
        'author__username', 'author__email',
        'subscriber__username', 'subscriber__email'
    ]
    list_filter = ['author__username', 'subscriber__username']
    empty_value_display = EMPTY
