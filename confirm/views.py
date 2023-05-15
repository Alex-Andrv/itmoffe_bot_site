import asyncio

import requests
from django.http import HttpResponseRedirect, Http404
from requests import Response

from config.general_site_config import CLIENT_ID, CLIENT_SECRET
from confirm.SiteLogger import SiteLogger
from confirm.models import IsuData

logger = SiteLogger()
loop = asyncio.get_event_loop()

def get_required_parameters(request) -> [int, str]:
    if "state" in request.GET and "code" in request.GET:
        if not request.GET["state"].isdigit():
            loop.run_until_complete(logger.print_error("Invalid GET parameter: state should be integer"))
            raise Http404("Invalid GET parameter: state should be integer")
        return int(request.GET["state"]), request.GET["code"]
    else:
        loop.run_until_complete(logger.print_error("Expected GET parameters: state, code"))
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
            loop.run_until_complete(logger.print_error(f"error with itmo.id: {response.status_code}; {response.reason} \n"
                               f"link: https://id.itmo.ru/auth/realms/itmo/protocol/openid-connect/token"))
            raise Http404("error with itmo.id")
        access_token = response.json().get("access_token", None)
        if access_token is None:
            loop.run_until_complete(logger.print_error(f"error with itmo.id: access_token is None"))
            raise Http404("error with itmo.id")
    except Exception as e:
        loop.run_until_complete(logger.print_error(f"error with itmo.id" + str(e)))
        raise Http404("error with itmo.id")
    return access_token


def get_info(access_token: str):
    headers = {'Authorization': 'Bearer ' + access_token}
    response: Response = requests.get('https://id.itmo.ru/auth/realms/itmo/protocol/openid-connect/userinfo', headers=headers)
    if response.status_code != 200:
        loop.run_until_complete(logger.print_error(f"error with itmo.id: {response.status_code}; {response.reason} \n"
                           "link: https://id.itmo.ru/auth/realms/itmo/protocol/openid-connect/userinfo"))
        raise Http404("error with itmo.id")
    return response.json()


def save_info(t_user_id: int, info):
    try:
        IsuData(
            t_user_id=t_user_id,
            sub=info['sub'],
            gender=info['gender'],
            name=info['name'],
            isu=info.get('isu', None),
            preferred_username=info['preferred_username'],
            given_name=info['given_name'],
            middle_name=info.get('middle_name', None),
            family_name=info['family_name'],
            email=info['email'],
            email_verified=info['email_verified']).save()
    except:
        loop.run_until_complete(logger.print_error(f"Trouble with user{t_user_id}. Probably he was registered"))
        raise Http404("Trouble with user. Probably he was registered")


def index(request):
    t_user_id, code = get_required_parameters(request)
    access_token = getAccessToken(code)
    info = get_info(access_token)
    save_info(t_user_id, info)
    loop.run_until_complete(logger.user_login_used_oauth(t_user_id, info))
    return HttpResponseRedirect("https://t.me/itmoffe_bot")