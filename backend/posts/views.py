from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Post, Like, Comment
from .forms import PostForm



@login_required
def feed_view(request):
    posts = Post.objects.all().select_related('author')
    return render(request, 'posts/feed.html', {'posts': posts})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:feed')
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'posts/post_detail.html', {'post': post})

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        like.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': created,
            'likes_count': post.likes.count()
        })
    
    return redirect('posts:post_detail', pk=pk)