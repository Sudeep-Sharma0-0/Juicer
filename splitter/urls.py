from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("splitter", views.splitter, name="splitter"),
    path("login", views.login_spotify, name="login"),
    path("callback_spotify", views.callback_spotify, name="callback_spotify"),
    path("logout", views.logout_spotify, name="logout"),
]
