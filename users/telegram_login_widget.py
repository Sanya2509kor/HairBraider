from django.conf import settings

from django_telegram_login.widgets.constants import (
    SMALL, 
    MEDIUM, 
    LARGE,
    DISABLE_USER_PHOTO,
)
from django_telegram_login.widgets.generator import (
    create_callback_login_widget,
    create_redirect_login_widget,
)


bot_name = settings.TELEGRAM_BOT_NAME
bot_token = settings.TELEGRAM_BOT_TOKEN
redirect_url = settings.TELEGRAM_LOGIN_REDIRECT_URL

telegram_login_widget_callback = create_callback_login_widget(bot_name, corner_radius=10, size=MEDIUM)

telegram_login_widget_redirect = create_redirect_login_widget(
    redirect_url, bot_name, size=LARGE, corner_radius=20, 
)