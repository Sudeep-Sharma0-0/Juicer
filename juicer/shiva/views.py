import base64
import requests
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.conf import settings
from . import user_validatian as uv
from . import gen_data
from . import models


client_id = settings.SPOTIFY_CLIENT_ID
client_secret = settings.SPOTIFY_CLIENT_SECRET
redirect_uri = settings.SPOTIFY_REDIRECT_URI

scope = '''playlist-read-private
 playlist-modify-private
 playlist-modify-public
 user-read-email'''
response_type = "code"

login_status = False


def index(req):
    if req.method == "POST":
        raise PermissionDenied

    userdata = req.session.get("userdata", {})
    context = {
        "platforms": gen_data.platforms,
        "login": login_status,
        "username": userdata.get("display_name", ""),
    }
    return render(req, "shiva/pralayaAwait.html", context)


def pralaya(req):
    if req.method == "POST":
        playlist_url = req.POST["playlist"]

        return render(req, "shiva/pralaya.html", {})
    return redirect("/shiva")


def register(req):
    if req.method == "POST":
        username = req.POST["username"]
        email = req.POST["email"]
        password = req.POST["password"]

        auth_validated = uv.validate_auth(username, password, email)
        user_exists = uv.check_existing(username, email)

        if auth_validated and not user_exists:
            print("Saved", auth_validated, user_exists)
            return render(req, "shiva/registerSuccess.html", {})
        elif user_exists:
            return render(req, "shiva/registrationFailed.html",
                          {"error": "user_exists"})
        return render(req, "shiva/registerFailed.html",
                      {"error": "auth_fail"})
    else:
        return render(req, "shiva/registerPage.html", {})


def login(req):
    if req.method == "POST":
        return redirect("https://accounts.spotify.com/authorize?"
                        + f"client_id={client_id}&"
                        + f"redirect_uri={redirect_uri}&"
                        + f"response_type={response_type}&"
                        + f"scope={scope}")
    else:
        return render(req, "shiva/loginPage.html", {"login": login_status})


def login_callback(req):
    if req.method == "POST":
        raise PermissionDenied

    auth_code = req.GET["code"]
    if auth_code:
        encoded_credentials = base64.b64encode(
            client_id.encode() + b':' + client_secret.encode()).decode("utf-8")
        auth_header = f"Basic {encoded_credentials}"

        url = "https://accounts.spotify.com/api/token"
        data = {
            "code": auth_code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            response = requests.post(url, data=data, headers=headers)

            if response.ok:
                global login_status
                login_status = True

                url = "https://api.spotify.com/v1/me"
                auth_header = f"Bearer {response.json()['access_token']}"
                headers = {
                    "Authorization": auth_header,
                }

                userdata = requests.get(url, headers=headers).json()
                req.session["userdata"] = userdata

                useremail = userdata["email"]

                user, created = models.Manushya.objects.get_or_create(
                    useremail=useremail,
                    defaults={
                        "oauth_provider": "Spotify",
                        "access_token": response.json()["access_token"],
                        "refresh_token": response.json()["refresh_token"],
                        "token_expiry": response.json()["expires_in"],
                    }
                )

                if created:
                    user.set_unusable_password()
                    user.save()

                return redirect("/shiva")
            else:
                raise SuspiciousOperation
        except requests.RequestException as e:
            print("Exception: " + e)

        raise PermissionDenied
