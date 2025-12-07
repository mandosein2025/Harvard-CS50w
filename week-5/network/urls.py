from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.post, name="post"),
    path("post/<str:post_id>", views.post, name="post"),
    path("index", views.index, name="index"),
    path("following", views.get_following_posts, name="following"),
    path("user/<str:user_id>", views.get_user, name="get_user"),
    path("like_post/<str:post_id>", views.like_post, name="like_post"),
    path("follow_user/<str:user_id>", views.follow_user, name="follow_user"),
]
