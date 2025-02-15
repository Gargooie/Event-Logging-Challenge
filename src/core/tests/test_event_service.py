import pytest
from django.db import transaction
from core.models import OutboxEvent
from core.services.event_service import EventService

@pytest.mark.django_db
class TestEventService:
    def test_publish_event_creates_outbox_event(self):
        # фикстура
        event_type = "test_event"
        event_data = {"key": "value"}

        #выполнение
        event = EventService.publish_event(event_type, event_data)

        # проверка
        assert event.event_type == event_type
        assert event.event_data == event_data
        assert event.status == OutboxEvent.StatusChoices.PENDING
        assert event.attempts == 0

    def test_publish_event_rollback_on_error(self):
        # фикстура
        initial_count = OutboxEvent.objects.count()

        #выполнение
        with pytest.raises(Exception):
            with transaction.atomic():
                EventService.publish_event("test_event", {"data": "value"})
                raise Exception("Test error")

        # проверка
        assert OutboxEvent.objects.count() == initial_count 