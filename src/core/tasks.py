# Celery задача для обработки событий

import structlog
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from core.models import OutboxEvent
from core.event_log_client import EventLogClient, EVENT_LOG_COLUMNS

logger = structlog.get_logger(__name__)

@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3
)
def process_outbox_events() -> None:
    """
    Обрабатывает пачку pending событий и отправляет их в ClickHouse
    """
    batch_size = settings.OUTBOX_BATCH_SIZE
    max_attempts = settings.OUTBOX_MAX_ATTEMPTS

    events = OutboxEvent.objects.filter(
        status=OutboxEvent.StatusChoices.PENDING,
        attempts__lt=max_attempts
    ).order_by('created_at')[:batch_size]

    if not events:
        return

    with EventLogClient.init() as client:
        try:
            # Подготавливаем данные для пакетной вставки
            events_data = [
                {
                    'event_type': event.event_type,
                    'event_date_time': event.created_at,
                    'environment': settings.ENVIRONMENT,
                    'event_context': event.event_data,
                    'metadata_version': 1
                }
                for event in events
            ]
            
            # Отправляем пачку в ClickHouse
            client.insert(events_data)
            
            # Обновляем статус обработанных событий
            now = timezone.now()
            events.update(
                status=OutboxEvent.StatusChoices.PROCESSED,
                processed_at=now
            )
            
            logger.info(
                "processed_outbox_events",
                count=len(events),
                event_ids=[e.id for e in events]
            )
            
        except Exception as e:
            # В случае ошибки увеличиваем счетчик попыток
            events.update(
                attempts=models.F('attempts') + 1,
                last_error=str(e)
            )
            logger.error(
                "failed_to_process_outbox_events",
                error=str(e),
                event_ids=[e.id for e in events]
            )
            raise