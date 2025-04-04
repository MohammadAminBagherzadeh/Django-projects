from typing import Any
from django.http import HttpRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from posts.models import Post, Comment, Vote
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from posts.forms import PostCreateUpdateForm, CommentCreateForm, CommentReplyForm, PostSearchForm
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class HomeView(View):
    form_class = PostSearchForm

    def get(self, request):
        posts = Post.objects.all()
        if request.GET.get('search'):
            posts = posts.filter(body__contains=request.GET['search'])
        return render(request, 'home/index.html', {'posts':posts, 'form':self.form_class})
    

class PostDetailView(View):
    form_class = CommentCreateForm
    form_class_reply = CommentReplyForm

    def setup(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        self.post_instance = get_object_or_404(Post, pk=kwargs['post_id'], slug=kwargs['post_slug'])
        return super().setup(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        comment = self.post_instance.pcomments.filter(is_reply=False)
        cant_like = False
        if request.user.is_authenticated and self.post_instance.user_cant_like(request.user):
            cant_like = True
        return render(request, 'home/detail.html', {'post':self.post_instance, 'comments':comment, 'form':self.form_class, 'reply_form':self.form_class_reply, 'cant_like':cant_like})
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid:
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.post = self.post_instance
            new_comment.save()
            messages.success(request, "You've submitted your comment successfully", 'success')
            return redirect('home:post_detail', self.post_instance.id, self.post_instance.slug)


class PostDeleteView(LoginRequiredMixin, View):

    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)

        if post.user.id == request.user.id:
            post.delete()
            messages.success(request, 'psot deleted succssesfully', 'success')

        else:
            messages.error(request, "You can't delete this post!", 'danger')
        
        return redirect('home:home')
    

class PostUpdateView(LoginRequiredMixin, View):
    form_class = PostCreateUpdateForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().setup(request, *args, **kwargs)
    
    def dispatch(self, request, *args, **kwargs):
        post = self.post_instance

        if not post.user.id == request.user.id:
            messages.error(request, "You can't update this post!", 'danger')
            return redirect('home:home')
        
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        post = self.post_instance
        form = self.form_class(instance=post)
        return render(request, 'home/update.html', {'form':form})

    def post(self, request, *args, **kwargs):
        post = self.post_instance
        form = self.form_class(request.POST, instance=post)

        if form.is_valid:
            new_post = form.save(commit=False)
            new_post.slug = slugify(form.cleaned_data['body'][:30])
            new_post.save()
            messages.success(request, "you're post updated successfully", 'success')
            return redirect('home:post_detail', post.pk, post.slug)
        

class PostCreateView(LoginRequiredMixin, View):
    form_class = PostCreateUpdateForm
    
    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(request, 'home/create.html', {'form':form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.slug = slugify(form.cleaned_data['body'][:30])
            new_post.user = request.user
            new_post.save()
            messages.success(request, "you're post created successfully", 'success')
            return redirect('home:post_detail', new_post.pk, new_post.slug)


class PostAddReplyView(LoginRequiredMixin, View):
    form_class = CommentReplyForm

    def post(self, request, post_id, comment_id):
        post = get_object_or_404(Post, id=post_id)
        comment = get_object_or_404(Comment, id=comment_id)
        form =self.form_class(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.post = post
            reply.reply = comment
            reply.is_reply = True
            reply.save()
            messages.success(request, "Your reply submitted successfully", 'success')
        return redirect('home:post_detail', post.id, post.slug)


class PostLikeView(LoginRequiredMixin, View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id = post_id)
        like = Vote.objects.filter(post=post, user=request.user)
        if like.exists():
            messages.error(request, "You can't like a post, twice", 'danger')
        else:
            Vote.objects.create(post=post, user=request.user)
            messages.success(request, 'You liked this post', 'success')
        return redirect('home:post_detail', post.id, post.slug)