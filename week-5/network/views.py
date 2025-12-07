import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .models import POST_MAX_LENGTH, Following, Post, User


def index(request):
    post_objects = Post.objects.all().order_by("-created_on")

    paginator = Paginator(post_objects, 10)

    page_number = request.GET.get("page", 1)
    posts = paginator.get_page(page_number)

    return render(
        request,
        "network/index.html",
        {
            "posts": posts,
            "num_page_range": range(posts.paginator.num_pages),
            "current_page": page_number,
            "post_max_length": POST_MAX_LENGTH,
        },
    )


@login_required
def get_following_posts(request):
    user = User.objects.get(id=request.user.id)
    following = user.following.all()
    following_users = [follow.user for follow in following]

    post_objects = Post.objects.filter(user__in=following_users).order_by("-created_on")
    paginator = Paginator(post_objects, 10)

    page_number = request.GET.get("page", 1)
    posts = paginator.get_page(page_number)

    return render(
        request,
        "network/following.html",
        {
            "posts": posts,
            "num_page_range": range(posts.paginator.num_pages),
            "current_page": page_number,
        },
    )


def login_view(request):
    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "network/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "network/register.html", {"message": "Passwords must match."}
            )

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request, "network/register.html", {"message": "Username already taken."}
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def like_post(request, post_id):
    if request.method == "POST":

        post = Post.objects.get(id=post_id)

        user = request.user
        if user in post.likes.all():
            post.likes.remove(user)
            post.save()
            return JsonResponse({"liked": "False", "post_id": post_id}, status=200)

        post.likes.add(user)
        post.save()
        return JsonResponse({"liked": "True", "post_id": post_id}, status=200)


@login_required
def post(request, post_id=None):
    if request.method == "POST":
        if not post_id:
            user = User.objects.get(id=request.user.id)
            user_post = Post.objects.create(
                user=user, message=request.POST["post-message"]
            )
            user_post.likes.add(user)
            user_post.save()

            return HttpResponseRedirect(reverse("index"))

        post = Post.objects.get(id=post_id)

        if request.user.id != post.user.id:
            return HttpResponseRedirect(reverse("index"))

        data = json.loads(request.body)
        if len(data.get("message", "")) <= 0:
            return JsonResponse({"message": "Posts cannot be empty"}, status=406)

        if len(data.get("message")) > POST_MAX_LENGTH:
            return JsonResponse(
                {"message": "Posts cannot be over 240 characters"}, status=406
            )

        post.message = data.get("message")
        post.save()

        return JsonResponse({"saved": True}, status=200)

    return render(request, "network/post.html", {"post_max_length": POST_MAX_LENGTH})


def get_user(request, user_id):
    user_profile = User.objects.get(id=user_id)

    followed_user, _ = Following.objects.get_or_create(user=user_profile)
    is_following = request.user in followed_user.followers.all()

    numbers_of_followers = followed_user.followers.count()
    number_of_users_followed = user_profile.following.count()

    post_objects = Post.objects.filter(user=user_profile).order_by("-created_on")
    paginator = Paginator(post_objects, 10)

    page_number = request.GET.get("page", 1)
    posts = paginator.get_page(page_number)

    return render(
        request,
        "network/profile.html",
        {
            "user": user_profile,
            "following": is_following,
            "number_of_followers": numbers_of_followers,
            "number_of_users_followed": number_of_users_followed,
            "posts": posts,
            "num_page_range": range(posts.paginator.num_pages),
            "current_page": page_number,
            "post_max_length": POST_MAX_LENGTH,
        },
    )


def follow_user(request, user_id):
    if request.method == "POST":

        user = User.objects.get(id=user_id)

        if request.user == user:
            return JsonResponse({"message": "Can not follow yourself"}, status=400)

        user_following, _ = Following.objects.get_or_create(user=user)

        if request.user not in user_following.followers.all():
            user_following.followers.add(request.user)
            user_following.save()

            return JsonResponse(
                {"followed": True, "user_id": user.id, "follower": request.user.id},
                status=200,
            )

        user_following.followers.remove(request.user)
        user_following.save()

        return JsonResponse(
            {"followed": False, "user": user.id, "follower": request.user.id},
            status=200,
        )

    return JsonResponse({"message": "Can only post to method"}, status=400)
