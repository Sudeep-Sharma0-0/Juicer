import re
from django.http import HttpResponse
from django.shortcuts import render, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings
from splitter.spotify_display import get_tracks


SPOTIPY_CLIENT_ID = settings.SPOTIPY_CLIENT_ID
SPOTIPY_CLIENT_SECRET = settings.SPOTIPY_CLIENT_SECRET
SPOTIPY_REDIRECT_URI = settings.SPOTIPY_REDIRECT_URI
SPOTIPY_CACHE_PATH = settings.SPOTIPY_CACHE_PATH
SPOTIPY_SCOPE = settings.SPOTIPY_SCOPE


def index(request):
    if len(get_user_info(request)) > 0:
        token_refresher(request)
        context = get_user_info(request)
        return render(request, 'splitter/index.html', context)
    else:
        return render(request, 'splitter/index.html')


def splitter(request):
    if request.method == "POST":
        if not request.session.get('access_token'):
            return HttpResponse("Please Login First!")

        playlist_link = request.POST.get("playlist_link")
        split_type = request.POST.get("split_type")
        playlist_id = get_id(playlist_link)

        return redirect(f'/splitter?playlist_id={playlist_id}&split_type={split_type}')
    else:
        playlist_id = request.GET.get("playlist_id")
        split_type = request.GET.get("split_type")

        context = {
            "playlist_id": playlist_id,
            "split_type": split_type,
        }
        context.update(get_user_info(request))

        tracks = get_tracks(request, playlist_id)
        context.update({"tracks": tracks})

        return render(request, 'splitter/index.html', context)


def get_id(playlist_link):
    pattern = r'^https?:\/\/(?:open|play)\.spotify\.com\/playlist\/([a-zA-Z0-9]+)'
    match = re.match(pattern, playlist_link)
    if match:
        return match.group(1)
    else:
        return None


def login_spotify(request):
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope=SPOTIPY_SCOPE,
            cache_path=SPOTIPY_CACHE_PATH,
        )
    )
    auth_url = sp.auth_manager.get_authorize_url()
    return redirect(auth_url)


def logout_spotify(request):
    request.session['access_token'] = None
    return redirect("/")


def callback_spotify(request):
    code = request.GET.get("code")
    if code:
        sp_oauth = SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope=SPOTIPY_SCOPE,
            cache_path=SPOTIPY_CACHE_PATH,
        )
        token_info = sp_oauth.get_access_token(code)

        if token_info:
            access_token = token_info["access_token"]
            refresh_token = token_info["refresh_token"]

            request.session['access_token'] = access_token
            request.session['refresh_token'] = refresh_token
            return redirect("/")
        else:
            return HttpResponse("Token retrieval failed")
    else:
        return HttpResponse("Code not found in request")


def get_user_info(request):
    access_token = request.session.get('access_token')

    if access_token:
        sp = spotipy.Spotify(auth=access_token)
        user_id = sp.me()["id"]

        context = {
            "access_token": access_token,
            "profile_pic": sp.user(user_id)["images"][0]["url"],
            "display_name": sp.user(user_id)["display_name"],
            "user_id": user_id,
        }
        return context
    else:
        return {}


def token_refresher(request):
    refresh_token = request.session.get('refresh_token')

    if refresh_token:
        sp_oauth = SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope=SPOTIPY_SCOPE,
            cache_path=SPOTIPY_CACHE_PATH,
        )
        token_info = sp_oauth.refresh_access_token(refresh_token)

        if token_info:
            access_token = token_info["access_token"]
            refresh_token = token_info["refresh_token"]

            request.session['access_token'] = access_token
            request.session['refresh_token'] = refresh_token
