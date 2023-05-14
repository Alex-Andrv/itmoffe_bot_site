import requests
from django.http import HttpResponseRedirect, Http404
from requests import Response

from config.general_site_config import CLIENT_ID, CLIENT_SECRET
from confirm.models import IsuData


def get_required_parameters(request) -> [int, str]:
    if "state" in request.GET and "code" in request.GET:
        if not request.GET["state"].isdigit():
            raise Http404("Invalid GET parameter: state should be integer")
        return int(request.GET["state"]), request.GET["code"]
    else:
        raise Http404("Expected GET parameters: state, code")


def getAccessToken(code: str) -> str:
    headers={"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri":"https://rcoffeestudent.itmo.ru",
        "code": code
    }
    try:
        response: Response = requests.post(
            'https://id.itmo.ru/auth/realms/itmo/protocol/openid-connect/token',
            data=data, headers=headers)
        if response.status_code != 200:
            raise Http404("error with itmo.id")
        access_token = response.json().get("access_token", None)
        if access_token is None:
            raise Http404("error with itmo.id")
    except:
        raise Http404("error with itmo.id")
    return access_token


def get_info(access_token: str):
    headers = {'Authorization': 'Bearer ' + access_token}
    response: Response = requests.get('https://id.itmo.ru/auth/realms/itmo/protocol/openid-connect/userinfo', headers=headers)
    if response.status_code != 200:
        raise Http404("error with itmo.id")
    return response.json()


def save_info(t_user_id: int, info):
    IsuData(
        t_user_id = t_user_id,
        sub = info['sub'],
        gender = info['gender'],
        name = info['name'],
        isu = info.get('isu', None),
        preferred_username = info['preferred_username'],
        given_name = info['given_name'],
        middle_name = info.get('middle_name', None),
        family_name = info['family_name'],
        email = info['email'],
        email_verified = info['email_verified']).save()


def index(request):
    t_user_id, code = get_required_parameters(request)
    access_token = getAccessToken(code)
    info = get_info(access_token)
    save_info(t_user_id, info)
    return HttpResponseRedirect("https://t.me/itmoffe_bot")