from .views import *
from . import views
from .views import HomePageView
from django.urls import path

urlpatterns = [
    path("", HomePageView.as_view(), name="index"),
    path("blog", BlogView.as_view(), name="blog"),
    path("signin", SigninView.as_view(), name="signin"),
    path("signup", SignupView.as_view(), name="signup"),
    path("signout", SignoutView.as_view(), name="signout"),
    path("create", CreateView.as_view(), name="create"),
    path("profile/<int:id>", ProfileView.as_view(), name='profile'),
    path("profile/<int:id>/edit", ProfileEditView.as_view(), name='profileedit'),
    path("post/<int:id>", PostDetailView.as_view(), name="post"),
    path("post/<int:id>/comment", SaveCommentView.as_view(), name="savecomment"),
    path("post/<int:id>/comment/delete", DeleteCommentView.as_view(), name="deletecomment"),
    path("post/<int:id>/edit", PostEditView.as_view(), name="editpost"),
    path("post/<int:id>/delete", DeletePostView.as_view(), name="deletepost"),
    path("post/<int:id>/increaselikes", IncreaselikesView.as_view(), name='increaselikes'),
    path("post/<int:id>/decreaselikes", DecreaselikesView.as_view(), name='decreaselikes'),
    ]