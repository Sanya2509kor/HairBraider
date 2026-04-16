import requests
from django.conf import settings
from django.urls import reverse
from threading import Thread


class TelegramNotifier:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, message):
        """Отправляет сообщение в Telegram"""
        if not self.bot_token or not self.chat_id:
            print("Telegram credentials not set")
            return False
            
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print("Telegram message sent successfully")
                return True
            else:
                print(f"Telegram API error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False
    
    def send_appointment_notification(self, appointment):
        """Отправляет уведомление о новой записи"""
        message = self._format_appointment_message(appointment)
        return self.send_message(message)
    
    # def send_appointment_cancellation_notification(self, appointment):
    #     """Отправляет уведомление об отмене записи"""
    #     message = self._format_cancellation_message(appointment)
    #     return self.send_message(message)
    
    def _format_appointment_message(self, appointment):
        """Форматирует сообщение о новой записи"""
        # Получаем URL для админки (если нужно)
        admin_url = settings.SITE_URL if hasattr(settings, 'SITE_URL') else ''
        
        # Формируем список цветов
        colors_text = ""
        if appointment.colors.exists():
            color_names = [color.name for color in appointment.colors.all()]
            colors_text = f"\n🎨 <b>Цвета:</b> {', '.join(color_names)}"
        
        # Формируем комментарий
        comment_text = ""
        if appointment.comment:
            comment_text = f"\n💬 <b>Комментарий:</b> {appointment.comment}"
        
        # Информация о пользователе (если авторизован)
        user_info = ""
        if appointment.user:
            user_info = f"\n👤 <b>Пользователь:</b> @{appointment.user.username} (ID: {appointment.user.id})"
        
        message = f"""
🔔 <b>НОВАЯ ЗАПИСЬ!</b> 🔔

━━━━━━━━━━━━━━━━━━━━
👤 <b>Клиент:</b> {appointment.name}
📞 <b>Телефон:</b> {appointment.phone}
📅 <b>Дата:</b> {appointment.date.date.strftime('%d.%m.%Y')}
⏰ <b>Время:</b> {appointment.time.time.strftime('%H:%M')}
💇 <b>Услуга:</b> {appointment.product.name}{colors_text}{comment_text}{user_info}
━━━━━━━━━━━━━━━━━━━━

🆔 <b>ID записи:</b> {appointment.id}
📅 <b>Создана:</b> {appointment.created_at.strftime('%d.%m.%Y %H:%M')}
        """.strip()
        
        # Добавляем ссылку на админку, если есть
        if admin_url:
            admin_link = f"{admin_url}{reverse('admin:orders_appointment_change', args=[appointment.id])}"
            message += f"\n\n🔗 <a href='{admin_link}'>Посмотреть в админке</a>"
        
        return message
    
#     def _format_cancellation_message(self, appointment):
#         """Форматирует сообщение об отмене записи"""
#         message = f"""
# ❌ <b>ЗАПИСЬ ОТМЕНЕНА!</b> ❌

# ━━━━━━━━━━━━━━━━━━━━
# 👤 <b>Клиент:</b> {appointment.name}
# 📞 <b>Телефон:</b> {appointment.phone}
# 📅 <b>Дата:</b> {appointment.date.date.strftime('%d.%m.%Y')}
# ⏰ <b>Время:</b> {appointment.time.time.strftime('%H:%M')}
# 💇 <b>Услуга:</b> {appointment.product.name}
# ━━━━━━━━━━━━━━━━━━━━

# 🆔 <b>ID записи:</b> {appointment.id}
#         """.strip()
        
#         return message


def send_telegram_async(notifier, appointment, notification_type='appointment'):
    """
    Асинхронная отправка уведомления
    
    Args:
        notifier: экземпляр TelegramNotifier
        appointment: объект Appointment
        notification_type: тип уведомления ('appointment' или 'cancellation')
    """
    if notification_type == 'cancellation':
        Thread(target=notifier.send_appointment_cancellation_notification, args=(appointment,)).start()
    else:
        Thread(target=notifier.send_appointment_notification, args=(appointment,)).start()