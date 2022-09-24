
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("send-post", views.send_post, name="send-post"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("following", views.following, name="following"),
    # API routes
    path("follow", views.follow, name="follow"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)