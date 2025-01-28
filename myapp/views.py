from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, ListView, UpdateView
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.db.models import F
from django.conf import settings
from .models import *


class HomePageView(TemplateView):
    template_name = "blog/index.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)

        # Fetch all posts from the database
        posts = Post.objects.all()

        # Add the posts to the context
        context["posts"] = posts

        # Optionally, you can add a flag to indicate whether posts exist
        context["has_posts"] = posts.exists()

        return context

@method_decorator(login_required(login_url='signin'), name='dispatch')
class ProfileView(TemplateView):
    template_name = 'blog/profile.html'
    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get('id')

        # Check if the requested profile belongs to the logged-in user
        if request.user.id != user_id:
            return redirect('index')

        # Fetch the user or return a 404 error if not found
        user = get_object_or_404(User, id=user_id)

        # Fetch the user's posts with pagination
        posts_list = Post.objects.filter(user_id=request.user.id)
        paginator = Paginator(posts_list, 3)  # Show 3 posts per page
        page_number = request.GET.get('page')  # Get the page number from the request
        posts = paginator.get_page(page_number)

        # Prepare the context data
        context = {
            'user': user,
            'posts': posts,
            'media_url': settings.MEDIA_URL,
        }

        return self.render_to_response(context)

@method_decorator(login_required, name='dispatch')
class ProfileEditView(TemplateView):
    template_name = 'blog/profileedit.html'

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.error_message = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('id')

        # Fetch the user or return a 404 error if not found
        user = get_object_or_404(User, id=user_id)
        context['user'] = user

        # Add error message to context if it exists
        if hasattr(self, 'error_message'):
            context['error_message'] = self.error_message

        return context

    def post(self, request, *args, **kwargs):
        user_id = self.kwargs.get('id')

        # Check if the requested profile belongs to the logged-in user
        if request.user.id != user_id:
            return redirect('index')

        # Fetch the user or return a 404 error if not found
        user = get_object_or_404(User, id=user_id)

        try:
            # Get data from the form
            firstname = request.POST.get('firstname', '').strip()
            lastname = request.POST.get('lastname', '').strip()
            email = request.POST.get('email', '').strip()

            # Update only non-empty fields
            if firstname:
                user.first_name = firstname
            if lastname:
                user.last_name = lastname
            if email:
                # Validate the email format if provided
                validate_email(email)
                user.email = email

            # Save the updated user object
            user.save()

            # Redirect to the profile page after saving
            return redirect('profile', id=user_id)

        except ValidationError as e:
            # Handle invalid email
            self.error_message = str(e)
            return self.render_to_response(self.get_context_data())

class BlogView(ListView):
    template_name = 'blog/blog.html'
    context_object_name = 'posts'
    paginate_by = 1

    def dispatch(self, request, *args, **kwargs):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            # Render the template with empty data for unauthenticated users
            return render(request, self.template_name, {
                'posts': [],
                'top_posts': [],
                'recent_posts': [],
                'user': None,
                'media_url': settings.MEDIA_URL,
            })
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Fetch posts by the logged-in user
        return Post.objects.filter(user_id=self.request.user.id).order_by("-id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add additional context data
        context['top_posts'] = Post.objects.all().order_by("-likes")[:10]  # Top 10 posts by likes
        context['recent_posts'] = Post.objects.all().order_by("-id")[:10]  # Recent 10 posts
        context['media_url'] = settings.MEDIA_URL
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post.html'
    context_object_name = 'post'  # The name of the variable to use in the template
    pk_url_kwarg = 'id'  # Use 'id' instead of 'pk' in the URL

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        # Add additional context data
        context['media_url'] = settings.MEDIA_URL
        context['comments'] = Comment.objects.filter(post_id=self.object.id)
        return context


class PostEditView(TemplateView):
    template_name = 'blog/postedit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch the post object to be edited
        post_id = self.kwargs.get('id')
        post = get_object_or_404(Post, id=post_id)
        context['post'] = post
        return context

    def post(self, request, *args, **kwargs):
        # Fetch the post object to be edited
        post_id = self.kwargs.get('id')
        post = get_object_or_404(Post, id=post_id)

        try:
            # Get data from the form
            postname = request.POST.get('postname', '').strip()
            content = request.POST.get('content', '').strip()
            category = request.POST.get('category', '').strip()
            image = request.FILES.get('image')

            # Update only non-empty fields
            if postname:
                post.postname = postname
            if content:
                post.content = content
            if category:
                post.category = category
            if image:
                post.image = image

            # Save the updated post object
            post.save()

            # Redirect to the post detail page after saving
            return redirect('post', id=post.id)

        except ValidationError as e:
            # Handle validation errors
            error_message = str(e)
            return self.render_to_response(self.get_context_data(error_message=error_message))

@method_decorator(login_required, name='dispatch')
class DeletePostView(TemplateView):
    def get(self, request, *args, **kwargs):
        post_id = kwargs.get('id')
        post = get_object_or_404(Post, id=post_id)
        post.delete()
        return redirect("blog")

@method_decorator(login_required, name='dispatch')
class IncreaselikesView(TemplateView):
    def post(self, request, *args, **kwargs):
        post_id = kwargs.get('id')
        # Fetch the post or return a 404 error if not found
        post = get_object_or_404(Post, id=post_id)

        # Prevent duplicate likes by the same user
        if request.user not in post.liked_by.all():
            # Use F() to avoid race conditions
            post.likes = F('likes') + 1
            post.liked_by.add(request.user)  # Track the user who liked the post
            post.save()
        # Redirect to the post's detail page
        # return redirect(reverse('post', kwargs={'id': post_id}))
        return (redirect("post", id=post.id))


@method_decorator(login_required, name='dispatch')
class DecreaselikesView(TemplateView):
    def post(self, request, *args, **kwargs):
        post_id = kwargs.get('id')
        post = get_object_or_404(Post, id=post_id)
        if request.user in post.liked_by.all():
            post.likes = F('likes') - 1
            post.liked_by.remove(request.user)
            post.save()
        return redirect("post", id=post.id)

class SaveCommentView(TemplateView):
    def post(self, request, *args, **kwargs):
        post_id = kwargs.get('id')
        post = Post.objects.get(id=post_id)
        content = request.POST['message']
        Comment(post_id=post.id, user_id=request.user.id, content=content).save()
        return redirect("post", id=post_id)

class DeleteCommentView(TemplateView):
    def get(self, request, *args, **kwargs):
        comment_id= kwargs.get('id')
        comment = Comment.objects.get(id=comment_id)
        post_id = comment.post.id
        comment.delete()
        return redirect("post",id=post_id)


# @login_required(login_url='signin')
class CreateView(TemplateView):
    template_name = 'blog/create.html'
    context_object_name = 'post'

    def get(self,request,*args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):

        try:
            # Extract form data
            postname = request.POST.get('postname', '').strip()
            content = request.POST.get('content', '').strip()
            category = request.POST.get('category', '').strip()
            image = request.FILES.get('image')

            # Validate required fields
            if not postname or not content:
                return render(request, self.template_name, {'error': "Postname and content are required."})

            # Save the post
            Post.objects.create(
                postname=postname,
                content=content,
                category=category,
                image=image,
                user=request.user
            )
            return redirect('index')  # Redirect to the index page on success

        except IntegrityError as e:
            print(f"Database error: {e}")
            return render(request, self.template_name, {'error': "A database error occurred."})
        except Exception as e:
            print(f"Unexpected error: {e}")
            return render(request, self.template_name, {'error': "An unexpected error occurred."})

class SignupView(TemplateView):
    template_name = "blog/signup.html"

    def get(self,request,*args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):

        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        # Validate input
        if not username or not password or not confirm_password:
            messages.error(request, "All fields are required.")
            return render(request, self.template_name)

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, self.template_name)

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, self.template_name)

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, self.template_name)

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Log the user in
        login(request, user)
        messages.success(request, "Signup successful!")
        return redirect('index')



class SigninView(TemplateView):
    template_name= "blog/signin.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password.")

class SignoutView(TemplateView):
    def get(self,request, *args, **kwargs):
        logout(request)
        messages.success(request, "You have been logged out.")
        return redirect('signin')