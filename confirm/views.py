import asyncio
import os

import requests
from asgiref.sync import async_to_sync
from django.db import transaction
from django.http import HttpResponseRedirect, Http404
from requests import Response

from config.general_site_config import CLIENT_ID, CLIENT_SECRET
from confirm.SiteLogger import SiteLogger
from confirm.models import IsuData, WorkPlace, Group

logger = SiteLogger()

def get_required_parameters(request) -> [int, str]:
    if "state" in request.GET and "code" in request.GET:
        if not request.GET["state"].isdigit():
            async_to_sync(logger.print_error)("Invalid GET parameter: state should be integer")
            raise Http404("Invalid GET parameter: state should be integer")
        return int(request.GET["state"]), request.GET["code"]
    else:
        raise Http404("Expected GET parameters: state, code")


def getAccessToken(code: str) -> str:
    try:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": "https://rcoffeestudent.itmo.ru",
            "code": code
        }
        response: Response = requests.post(
            'https://id.itmo.ru/auth/realms/itmo/protocol/openid-connect/token',
            data=data, headers=headers)
        if response.status_code != 200:
            async_to_sync(logger.print_error)(f"Can't get access token. Error with itmo.id: {response.status_code}; {response.reason} \n"
                                   f"link: https://id.itmo.ru/auth/realms/itmo/protocol/openid-connect/token")
            raise Http404("Can't get access token")
        access_token = response.json().get("access_token", None)
        if access_token is None:
            async_to_sync(logger.print_error)(f"Can't get access token: access_token is None")
            raise Http404("Can't get access token, access token is None")
    except Exception as e:
        async_to_sync(logger.print_error)(f"Can't get access token" + str(e))
        raise Http404("Can't get access token")
    return access_token


def get_info(access_token: str):
    headers = {'Authorization': 'Bearer ' + access_token}
    response: Response = requests.get('https://id.itmo.ru/auth/realms/itmo/protocol/openid-connect/userinfo',
                                      headers=headers)
    if response.status_code != 200:
        async_to_sync(logger.print_error)(f"error during getting info: {response.status_code}; {response.reason} \n"
                                                   "link: https://id.itmo.ru/auth/realms/itmo/protocol/openid-connect/userinfo")
        raise Http404("error during getting info")
    return response.json()


def save_isu_data(t_user_id: int, info: dict, is_student: bool, is_worker: bool):
    isu_data = IsuData(
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
        email_verified=info['email_verified'],
        is_student=is_student,
        is_worker=is_worker
    )
    isu_data.save()
    return isu_data


def save_work_places(t_user_id: int, work_places: list):
    work_places_arr = []
    for work_place in work_places:
        work_place_entity = WorkPlace(id=work_place['id'],
                  name=work_place['name'],
                  short_name=work_place['short_name'])
        work_place_entity.save()
        work_places_arr.append(work_place_entity)
    return work_places_arr


def save_groups(t_user_id: int, groups: list):
    groups_arr = []
    for group in groups:
        qualification_name = None
        if 'qualification' in group:
            qualification_name = group['qualification']['name']
        group_entity = Group(
              name=group['name'],
              course=group['course'],
              faculty_name=group['faculty']['name'],
              qualification_name=qualification_name)
        group_entity.save()
        groups_arr.append(group_entity)
    return groups_arr


def save_info(t_user_id: int, info: dict):
    try:
        is_student, is_worker = info.get('is_student', False), info.get('is_worker', False)
        if len(info.get('groups', [])) != 0:
            is_student |= True
        if len(info.get('work_places', [])) != 0:
            is_worker |= True
        with transaction.atomic():
            isu_data = save_isu_data(t_user_id, info, is_student, is_worker)
            if is_worker:
                work_places = save_work_places(t_user_id, info.get('work_places', []))
                isu_data.groups.add(*work_places)
            if is_student:
                groups = save_groups(t_user_id, info.get('groups', []))
                isu_data.groups.add(*groups)
            isu_data.save()
    except Exception as e:
        async_to_sync(logger.print_error)(f"Trouble during save info user{t_user_id}. {info}. {e}")
        raise Http404("Trouble with user")


def index(request):
    t_user_id, code = get_required_parameters(request)
    access_token = getAccessToken(code)
    info = get_info(access_token)
    save_info(t_user_id, info)
    async_to_sync(logger.user_login_used_oauth)(t_user_id, info)
    return HttpResponseRedirect("https://t.me/itmoffe_bot")