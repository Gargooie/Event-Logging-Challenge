# Пример использования в бизнес-логике
from django.db import transaction
from core.services.event_service import EventService
from users.models import User

class UserService:
    @staticmethod
    @transaction.atomic
    def create_user(email: str, password: str) -> User:
        # Создаем пользователя
        user = User.objects.create_user(
            email=email,
            password=password
        )
        
        # Публикуем событие в той же транзакции
        EventService.publish_event(
            event_type='user_created',
            event_data={
                'user_id': user.id,
                'email': user.email
            }
        )
        
        return user