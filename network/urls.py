
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.new_post, name="new_post"),
    path('edit_post/<int:post_id>/', views.edit_post, name='edit_post'),
    path("profile/<int:id>", views.profile_view, name="profile"),
    path('profile/<int:user_id>/follow-unfollow/',  views.follow_unfollow, name='follow_unfollow'),
    path("following/", views.following, name="following"),
    path("like_post/<int:post_id>/", views.like_post, name='like_post'),
]
