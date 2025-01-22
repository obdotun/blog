from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.db.models import F
from django.conf import settings
from .models import *

# Create your views here.
def index(request):
    posts=Post.objects.all()
    if posts.count() != 0:
        return render(request, "blog/index.html",{"posts":posts})
    return render(request, "blog/index.html")

@login_required(login_url='signin')
def profile(request,id):
    if request.user.id != id:
        return redirect('index')
    # Fetch the user or return a 404 error if not found
    user = get_object_or_404(User, id=id)

    # Fetch the user's posts with pagination
    posts_list = Post.objects.filter(user_id=request.user.id)  # Order by most recent
    paginator = Paginator(posts_list, 3)  # Show 10 posts per page
    page_number = request.GET.get('page')  # Get the page number from the request
    posts = paginator.get_page(page_number)

    # Render the template with context
    return render(request, 'blog/profile.html', {
        'user': user,
        'posts': posts,
        'media_url': settings.MEDIA_URL,
    })

@login_required
def profileedit(request, id):
    # Ensure the user is editing their own profile
    if request.user.id != id:
        return redirect('profile', id=request.user.id)

    # Fetch the user object or return a 404 error
    user = get_object_or_404(User, id=id)

    if request.method == 'POST':
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
            return redirect('profile', id=id)

        except ValidationError as e:
            # Handle invalid email
            error_message = str(e)
            return render(request, "blog/profileedit.html", {
                'user': user,
                'error_message': error_message,
            })

    # Render the edit form for GET requests
    return render(request, "blog/profileedit.html", {
        'user': user,
    })

def blog(request):
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        return render(request, "blog/blog.html", {
            'posts': [],
            'top_posts': [],
            'recent_posts': [],
            'user': None,
            'media_url': settings.MEDIA_URL
        })

    # Fetch posts by the logged-in user
    user_posts = Post.objects.filter(user_id=request.user.id).order_by("-id")
    paginator_user_posts = Paginator(user_posts, 3)  # Show 10 posts per page
    page_number_user_posts = request.GET.get('page_user_posts')
    posts = paginator_user_posts.get_page(page_number_user_posts)

    # Fetch top posts (ordered by likes)
    top_posts = Post.objects.all().order_by("-likes")[:10]  # Limit to 10 posts

    # Fetch recent posts (ordered by ID)
    recent_posts = Post.objects.all().order_by("-id")[:10]  # Limit to 10 posts

    # Render the template with context
    return render(request, "blog/blog.html", {
        'posts': posts,
        'top_posts': top_posts,
        'recent_posts': recent_posts,
        'user': request.user,
        'media_url': settings.MEDIA_URL
    })

def post(request,id):
    post=get_object_or_404(Post, id=id)

    return render(request, 'blog/post.html', {
        'post': post,
        'media_url': settings.MEDIA_URL,
        'comments': Comment.objects.filter(post_id=post.id),
    })

def editpost(request,id):
    post = Post.objects.get(id=id)
    if request.method == 'POST':
        try:
            postname = request.POST.get('postname').strip()
            content = request.POST.get('content').strip()
            category = request.POST.get('category').strip()
            image = request.FILES.get('image')

            if postname:
                post.postname = postname
            if content:
                post.content = content
            if category:
                post.category = category
            if image:
                post.image = image

            post.save()

        except:
            print("Error")
        return redirect('post', post.id)

    return render(request, "blog/postedit.html", {
        'post': post
    })

@login_required
def deletepost(request,id):
    post = Post.objects.get(id=id)
    post.delete()
    return redirect("blog")

@login_required
def increaselikes(request, id):
    # Fetch the post or return a 404 error if not found
    post = get_object_or_404(Post, id=id)

    # Prevent duplicate likes by the same user
    if request.user not in post.liked_by.all():
        # Use F() to avoid race conditions
        post.likes = F('likes') + 1
        post.liked_by.add(request.user)  # Track the user who liked the post
        post.save()
    # Redirect to the post's detail page
    return redirect("post", id=post.id)

@login_required
def decreaselikes(request, id):
    post = get_object_or_404(Post, id=id)
    if request.user in post.liked_by.all():
        post.likes = F('likes') - 1
        post.liked_by.remove(request.user)
        post.save()
    return redirect("post", id=post.id)

def savecomment(request,id):
    post = Post.objects.get(id=id)
    if request.method == 'POST':
        content = request.POST['message']
        Comment(post_id=post.id, user_id=request.user.id, content=content).save()
        return redirect("post",id=id)

def deletecomment(request,id):
    comment = Comment.objects.get(id=id)
    postid = comment.post.id
    comment.delete()
    return redirect("post",id=postid)


@login_required(login_url='signin')
def create(request):
    if request.method == 'POST':
        try:
            # Extract form data
            postname = request.POST.get('postname', '').strip()
            content = request.POST.get('content', '').strip()
            category = request.POST.get('category', '').strip()
            image = request.FILES.get('image')

            # Validate required fields
            if not postname or not content:
                return render(request, "blog/create.html", {'error': "Postname and content are required."})

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
            return render(request, "blog/create.html", {'error': "A database error occurred."})
        except Exception as e:
            print(f"Unexpected error: {e}")
            return render(request, "blog/create.html", {'error': "An unexpected error occurred."})

        # Render the create template for GET requests
    return render(request, "blog/create.html")

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        # Validate input
        if not username or not password or not confirm_password:
            messages.error(request, "All fields are required.")
            return render(request, "blog/signup.html")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "blog/signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "blog/signup.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, "blog/signup.html")

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Log the user in
        login(request, user)
        messages.success(request, "Signup successful!")
        return redirect('index')

    return render(request, "blog/signup.html")

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "blog/signin.html")

def signout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('signin')