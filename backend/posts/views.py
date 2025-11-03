from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Post, Like, Comment
from .forms import PostForm, CommentForm
from django.contrib import messages



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


from django.http import JsonResponse
from .forms import CommentForm



@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            
            return redirect('posts:feed')  
    
    return redirect('posts:feed')  


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Check if user owns the post
    if post.author != request.user:
        messages.error(request, "You can't delete this post.")
        return redirect('posts:feed')
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted successfully.")
        return redirect('posts:feed')
    
    return redirect('posts:feed')


@login_required
def update_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    # Check if user owns the comment
    if comment.author != request.user:
        return JsonResponse({'success': False, 'error': 'Not authorized'})
    
    if request.method == 'POST':
        new_content = request.POST.get('content', '').strip()
        if new_content:
            comment.content = new_content
            comment.is_edited = True
            comment.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'content': comment.content,
                    'is_edited': comment.is_edited
                })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    # Check if user owns the comment
    if comment.author != request.user:
        return JsonResponse({'success': False, 'error': 'Not authorized'})
    
    if request.method == 'POST':
        comment.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        return redirect('posts:feed')
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})