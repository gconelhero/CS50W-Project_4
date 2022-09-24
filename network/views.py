import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import User, Post


def index(request):
    if request.user.is_authenticated:
        if request.method == "POST" and str(request.POST["new-post"]).replace(" ", '').split() != []:
            content = request.POST['new-post']
            post = Post.objects.create(user=request.user, content=content)
            post.save()
            return HttpResponseRedirect(reverse("index"))
        try:
            posts = Post.objects.order_by('-timestamp').all()
            posts_paginator = Paginator(posts, 10)
            page_num = request.GET.get("pagina")
            page = posts_paginator.get_page(page_num)
            page_range = posts_paginator.page_range
        except Post.DoesNotExist:
            JsonResponse({"error": "No Posts"}, status=400)
        return render(request, "network/index.html", {
            "posts": [post.serialize() for post in page],
            "page": page,
            "page_range": page_range,
        })
    else:
        return render(request, "network/login.html")


def profile(request, username):
    if request.user.is_authenticated:
        context = {}
        user = User.objects.get(username=username)
        context["follower"] = user.serialize()["follower"]
        context["following"] = user.serialize()["following"]
        if request.user != user:
            context["follow"] = True
            if request.user.username in context["follower"]:
                context["unfollow"] = True
        try:
            posts = Post.objects.filter(user=user.id).order_by('-timestamp')
            posts_paginator = Paginator(posts, 10)
            page_num = request.GET.get("pagina")
            page = posts_paginator.get_page(page_num)
            context["page"] = page
            context["username"] = user.username
            context["posts"] = [post.serialize() for post in page]
            context["page_range"] = posts_paginator.page_range
            return render(request, "network/profile.html", context=context)
        except:
            return HttpResponseRedirect(reverse("index"))
        
    else:
        return render(request, "network/login.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def following(request):
    if request.user.is_authenticated:
        context = {}
        context["following"] = []
        user = User.objects.get(id=request.user.id)
        for username in user.serialize()["following"]:
            context["following"].append(User.objects.get(username=username))
            posts = Post.objects.filter(user__in=context["following"]).order_by("-timestamp")
            posts_paginator = Paginator(posts, 10)
            page_num = request.GET.get("pagina")
            page = posts_paginator.get_page(page_num)
            context["page"] = page
            context["page_range"] = posts_paginator.page_range
            context["posts"] = [post.serialize() for post in page]
        return render(request, "network/following.html", context=context)
    else:
        return render(request, "network/login.html")
        

@csrf_exempt
@login_required
def follow(request):
    if request.method == "PUT":
        follow = "Follow"
        try:
            user = User.objects.get(username=json.loads(request.body)["user"])
            if request.user.username not in user.serialize()['follower'] and user != request.user:
                user.follower.add(request.user)
                user.save()
                follow = "Unfollow"
            else:
                user.follower.remove(request.user)
                user.save()
        except User.DoesNotExist:
            return JsonResponse({
                "error": f"User does not exist."
            }, status=400)
        return JsonResponse({
            "follow": follow,
            "followers": user.serialize()['follower']
            })#HttpResponse(status=204)
    else:
        return HttpResponseRedirect(reverse("index"))


@csrf_exempt
@login_required
def send_post(request):
    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("post") is not None:
            post = Post.objects.get(id=data["post"])
            if str(request.user) not in post.serialize()['like']:
                post.like.add(request.user)
                like = "Unlike"
            else:
                post.like.remove(request.user)
                like = "Like"
            post.save()
            return JsonResponse({
                "likes": post.serialize()['like'],
                "like": like
            })
        elif data.get("edit") is not None and request.user.id == Post.objects.get(id=data.get("edit")).user.id:
            post_content = Post.objects.get(id=data.get("edit"))
            return JsonResponse({
                "post_content": post_content.serialize()['content'],
                "post_id": str(post_content.id),
                "user": request.user.username
            })
        elif data.get("edit_content") is not None and request.user.id == Post.objects.get(id=data.get("edit_content")).user.id:
            data = json.loads(request.body)
            post_edit = Post.objects.get(id=int(data["edit_content"]))
            post_edit.content = data["content"]
            post_edit.save()
            return JsonResponse({
                "post_content": post_edit.content,
            })
    else:
        return HttpResponseRedirect(reverse("index"))