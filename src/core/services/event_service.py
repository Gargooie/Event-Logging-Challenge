# Создание сервиса для работы с событиями
from typing import Any
from django.db import transaction
from core.models import OutboxEvent

class EventService:
    @staticmethod
    @transaction.atomic
    def publish_event(event_type: str, event_data: dict[str, Any]) -> OutboxEvent:
        """
        Создает событие в outbox в рамках текущей транзакции
        """
        return OutboxEvent.objects.create(
            event_type=event_type,
            event_data=event_data
        )