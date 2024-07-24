from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post, Followers, Likes
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


def index(request):
    all_posts = Post.objects.all().order_by('-date')
    paginator = Paginator(all_posts, 10)

    # Initialize an empty list to store liked post IDs
    user_liked_posts = []

    # Populate the list with post IDs liked by the user
    if request.user.is_authenticated:
        for like in Likes.objects.filter(user=request.user):
            user_liked_posts.append(like.post_id) 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'network/index.html', {
        'page_obj': page_obj,
        'all_posts': all_posts,
        "user_liked_posts": user_liked_posts
        })    

class PostListView(ListView):
    paginate_by = 10
    model = Post

def new_post(request):    
    if request.method == "POST":
        message = request.POST['post']
        if message:
            user =  request.user
            post = Post(post=message, author=user)
            post.save()
            return HttpResponseRedirect(reverse(index))
        else:
            return JsonResponse({'error': 'This field can not be empty.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def profile_view(request, id):
    user = User.objects.get(pk=id)
    user_posts = Post.objects.filter(author=user).order_by('-date')
    followers = Followers.objects.filter(followers=user)
    followings = Followers.objects.filter(followings=user)

    is_following = Followers.objects.filter(followers=user, followings=request.user).exists()

    # create list to store liked posts
    user_liked_posts = []
    if request.user.is_authenticated:
        for like in Likes.objects.filter(user=request.user):
            user_liked_posts.append(like.post_id) 
    
    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'network/profile.html', {
        "user": user,
        "page_obj": page_obj,
        "followers": followers,
        "followings": followings,
        "is_following": is_following,
        "posts": user_posts,
        "user_liked_posts": user_liked_posts
    })

@csrf_exempt
@login_required
def edit_post(request, post_id):
    if request.method == "PUT":
        post = Post.objects.get(pk=post_id)
        data = json.loads(request.body)
        post_content = data.get('post')
        if post_content:
            post.post = post_content
            post.is_edited = True
            post.save()
            return HttpResponseRedirect(reverse(index))
    return JsonResponse({'error': 'Invalid request method.'}, status=400) 

@csrf_exempt
@login_required
def follow_unfollow(request, user_id):
    current_user = request.user
    target_user = User.objects.get(id=user_id)
    if request.method == "POST":
    # check if the current user is already following the user
        follow_relation = Followers.objects.filter(followings = current_user, followers = target_user)

        if follow_relation:
            # if exists, unfollow
            follow_relation.delete()
        else:
            # if not exists, follow
            Followers.objects.create(followings = current_user, followers = target_user)
        
        return HttpResponseRedirect(reverse('profile', kwargs={'id': user_id}))
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

@login_required
def following(request):
    current_user = request.user
    # get the list of users the current user is following
    user_following = Followers.objects.filter(followings=current_user)
    #create list of followings 
    user_ids = []
    for relation in user_following:
        user_ids.append(relation.followers.id)
    # get the posts authored by the users the current user is following
    user_posts = Post.objects.filter(author__in = user_ids).order_by('-date')    
    
    # list of liked posts
    user_liked_posts = []
    for like in Likes.objects.filter(user=request.user):
        user_liked_posts.append(like.post_id)
   
    paginator = Paginator(user_posts, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'network/following.html', {     
        "page_obj": page_obj,
        "user_liked_posts": user_liked_posts
    })

@csrf_exempt
@login_required
def like_post(request, post_id):
    if request.method == "PUT":
        post = Post.objects.get(pk=post_id)
        user = request.user

        like = Likes.objects.filter(user=user, post=post)

        if like:
            like.delete()
            liked = False
        else:
            Likes.objects.create(user=user, post=post)
            liked = True
        post.save()
        like_count = Likes.objects.filter(post=post).count()
        return JsonResponse({'liked': liked, 'like_count': like_count})
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


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
