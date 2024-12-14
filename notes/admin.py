from django.contrib import admin
from .models import Note, Category, Tag, Comment, Notification

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'is_public', 'views')
    list_filter = ('is_public', 'created_at', 'category')
    search_fields = ('title', 'content', 'author__username')
    date_hierarchy = 'created_at'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('note', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'note__title')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'content')

