"""
Blog views - Both FBV and CBV examples with HTMX support
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.http import HttpResponse

from .models import Post, Category, Comment
from .forms import PostForm, CommentForm


# ===== CLASS-BASED VIEWS (Recommended) =====

class PostListView(ListView):
    """List published posts with search, filter, pagination"""
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        qs = Post.objects.filter(
            status='published'
        ).select_related('author', 'category')

        # Search
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(
                Q(title__icontains=query) |
                Q(body__icontains=query) |
                Q(excerpt__icontains=query)
            )

        # Category filter
        category = self.request.GET.get('category')
        if category:
            qs = qs.filter(category__slug=category)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(
            post_count=Count('posts')
        ).filter(post_count__gt=0)
        context['query'] = self.request.GET.get('q', '')
        context['current_category'] = self.request.GET.get('category', '')
        return context

    def get_template_names(self):
        """Return partial template for HTMX requests"""
        if self.request.htmx:
            return ['blog/partials/post_list_partial.html']
        return [self.template_name]


class PostDetailView(DetailView):
    """Display single post with comments"""
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(
            status='published'
        ).select_related('author', 'category')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Increment view count
        Post.objects.filter(pk=obj.pk).update(
            views_count=obj.views_count + 1
        )
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(is_active=True)
        context['comment_form'] = CommentForm()
        # Related posts
        context['related_posts'] = Post.objects.filter(
            status='published',
            category=self.object.category
        ).exclude(pk=self.object.pk)[:3]
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Create new post"""
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post created successfully!')
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edit existing post"""
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def test_func(self):
        return self.get_object().author == self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Post updated successfully!')
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete post with confirmation"""
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog:post_list')

    def test_func(self):
        return self.get_object().author == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Post deleted successfully!')
        return super().delete(request, *args, **kwargs)


# ===== HTMX VIEWS =====

def add_comment(request, slug):
    """Add comment via HTMX (returns partial HTML)"""
    post = get_object_or_404(Post, slug=slug, status='published')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            # Return just the new comment HTML for HTMX
            if request.htmx:
                return render(request, 'blog/partials/comment.html',
                              {'comment': comment})
            messages.success(request, 'Comment added!')
            return redirect(post.get_absolute_url())

    return HttpResponse(status=400)


def search_results(request):
    """HTMX live search - returns partial results"""
    query = request.GET.get('q', '').strip()
    posts = []
    if len(query) >= 2:
        posts = Post.objects.filter(
            Q(title__icontains=query) | Q(body__icontains=query),
            status='published'
        ).select_related('author', 'category')[:10]

    template = 'blog/partials/search_results.html'
    return render(request, template, {'posts': posts, 'query': query})


def category_posts(request, slug):
    """Posts filtered by category"""
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(
        category=category,
        status='published'
    ).select_related('author', 'category')

    context = {
        'category': category,
        'posts': posts,
        'categories': Category.objects.annotate(
            post_count=Count('posts')
        ).filter(post_count__gt=0),
        'current_category': category.name,
    }
    return render(request, 'blog/post_list.html', context)
