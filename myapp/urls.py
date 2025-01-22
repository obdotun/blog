from . import views
from django.urls import path

urlpatterns = [
    path("", views.index, name="index"),
    path("blog", views.blog, name="blog"),
    path("signin", views.signin, name="signin"),
    path("signup", views.signup, name="signup"),
    path("signout", views.signout, name="signout"),
    path("create", views.create, name="create"),
    path("profile/<int:id>", views.profile, name='profile'),
    path("profile/<int:id>/edit", views.profileedit, name='profileedit'),
    path("post/<int:id>", views.post, name="post"),
    path("post/<int:id>/comment", views.savecomment, name="savecomment"),
    path("post/<int:id>/comment/delete", views.deletecomment, name="deletecomment"),
    path("post/<int:id>/edit", views.editpost, name="editpost"),
    path("post/<int:id>/delete", views.deletepost, name="deletepost"),
    path("post/<int:id>/increaselikes", views.increaselikes, name='increaselikes'),
    path("post/<int:id>/decreaselikes", views.decreaselikes, name='decreaselikes'),
    ]