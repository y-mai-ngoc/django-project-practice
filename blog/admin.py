from django.contrib import admin
from .models import Post, Category, Tag, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status',
                    'published_at', 'views_count']
    list_filter = ['status', 'category', 'published_at', 'author']
    search_fields = ['title', 'body']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'published_at'
    ordering = ['-published_at']
    list_editable = ['status']
    list_per_page = 25
    filter_horizontal = ['tags']

    actions = ['make_published', 'make_draft']

    @admin.action(description='Mark selected as Published')
    def make_published(self, request, queryset):
        count = queryset.update(status='published')
        self.message_user(request, f'{count} posts marked as published.')

    @admin.action(description='Mark selected as Draft')
    def make_draft(self, request, queryset):
        queryset.update(status='draft')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'post', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['author_name', 'body']
    list_editable = ['is_active']
