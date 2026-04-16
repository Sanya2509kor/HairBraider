import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SMSRUService:
    """Сервис для работы с API SMS.RU (авторизация по звонку)"""
    BASE_URL = "https://sms.ru/callcheck"
    
    def __init__(self):
        self.api_id = getattr(settings, 'SMSRU_API_ID', None)
        print(f"DEBUG: SMSRU_API_ID = {self.api_id}")
    
    def _clean_phone(self, phone):
        """Очищает номер телефона до формата 79XXXXXXXXX"""
        # Удаляем все кроме цифр
        phone = ''.join(filter(str.isdigit, phone))
        # Если начинается с 8, заменяем на 7
        if phone.startswith('8'):
            phone = '7' + phone[1:]
        # Если не начинается с 7, добавляем 7
        if not phone.startswith('7'):
            phone = '7' + phone
        print(f"DEBUG: Cleaned phone: {phone}")
        return phone
    
    def create_call_auth(self, phone):
        """Создает запрос на авторизацию по звонку"""
        if not self.api_id:
            return {
                'success': False,
                'error': 'Не настроен API ID SMS.RU. Добавьте SMSRU_API_ID в settings.py'
            }
        
        phone = self._clean_phone(phone)
        
        url = f"{self.BASE_URL}/add"
        params = {
            'api_id': self.api_id,
            'phone': phone,
            'json': 1
        }
        
        print(f"DEBUG: Calling SMS.RU API: {url} with params {params}")
        
        try:
            response = requests.get(url, params=params, timeout=30)
            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response text: {response.text}")
            data = response.json()
            print(f"DEBUG: Parsed data: {data}")
            
            if data.get('status') == 'OK':
                return {
                    'success': True,
                    'check_id': data['check_id'],
                    'call_phone': data['call_phone'],
                    'call_phone_pretty': data['call_phone_pretty']
                }
            else:
                return {
                    'success': False,
                    'error': f"Ошибка {data.get('status_code')}: {data.get('status_text', 'Неизвестная ошибка')}"
                }
        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Request error: {e}")
            return {
                'success': False,
                'error': f"Ошибка подключения: {str(e)}"
            }
    
    def check_status(self, check_id):
        """Проверяет статус авторизации"""
        url = f"{self.BASE_URL}/status"
        params = {
            'api_id': self.api_id,
            'check_id': check_id,
            'json': 1
        }
        
        print(f"DEBUG: Checking status for check_id={check_id}")
        
        try:
            response = requests.get(url, params=params, timeout=30)
            print(f"DEBUG: Status response status: {response.status_code}")
            print(f"DEBUG: Status response text: {response.text}")
            data = response.json()
            print(f"DEBUG: Status data: {data}")
            
            if data.get('status') == 'OK':
                status_code = data.get('check_status')
                print(f"DEBUG: check_status = {status_code}, type = {type(status_code)}")
                
                # Исправлено: сравниваем как число, а не как строку
                is_confirmed = (status_code == 401)  # Теперь число, а не '401'
                
                return {
                    'success': True,
                    'is_confirmed': is_confirmed,
                    'status_code': status_code,
                    'status_text': data.get('check_status_text')
                }
            else:
                return {
                    'success': False,
                    'error': f"Ошибка API: {data.get('status_code')}"
                }
        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Status check error: {e}")
            return {
                'success': False,
                'error': f"Ошибка подключения: {str(e)}"
            }