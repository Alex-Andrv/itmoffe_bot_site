import asyncio

from aiogram import Bot
from asgiref.sync import async_to_sync

from config.general_site_config import ALARM_BOT_TOKEN, CHAT_ID_ALARM, CHAT_ID_ALARM_WITH_HR


class SiteLogger:

    def __init__(self):
        self.alarm_bot: Bot = Bot(token=ALARM_BOT_TOKEN)

    async def print_error(self, message: str):
        await self.alarm_bot.send_message(CHAT_ID_ALARM, message)
        await self.alarm_bot.send_message(CHAT_ID_ALARM, "https://www.youtube.com/watch?v=sjakGpdgWUw")

    async def user_login_used_oauth(self, t_user_id: int, data):
        name = data['name'],
        isu = data.get('isu', None)
        email = data['email']
        await self.alarm_bot.send_message(CHAT_ID_ALARM_WITH_HR,
                                          f"""
        Пользователь зарегистрировался через OAuth: \n 
        user: {name}
        email: {email}
        isu: {isu}
        t_user_id: {t_user_id}
        """)
