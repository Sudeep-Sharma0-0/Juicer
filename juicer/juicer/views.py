from django.shortcuts import redirect
from django.http import HttpResponse


def index(req):
    return HttpResponse("Juicer Home Page")


def register(req):
    return redirect("/shiva/register")
