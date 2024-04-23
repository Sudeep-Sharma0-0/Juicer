from django.urls import path
from . import views


urlpatterns = [
        path("", views.index, name="index"),
        path("pralaya/", views.pralaya, name="prayala"),
        path("register/", views.register, name="register"),
        path("login/", views.login, name="login"),
        path("login/callback", views.login_callback, name="login_callback"),
]
