from django.contrib import admin

from .models import Following, Post, User

admin.site.register(Following)
admin.site.register(Post)
admin.site.register(User)
