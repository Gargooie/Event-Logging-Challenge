import pytest
from django.utils import timezone
from core.models import OutboxEvent
from core.tasks import process_outbox_events

@pytest.mark.django_db
class TestProcessOutboxEvents:
    def test_process_outbox_events_success(self, mocker):
        # фикстура
        event = OutboxEvent.objects.create(
            event_type="test_event",
            event_data={"test": "data"}
        )
        mock_client = mocker.patch('core.event_log_client.EventLogClient.init')
        mock_client.return_value.__enter__.return_value.insert = mocker.Mock()

        # выполнение
        process_outbox_events()

        # проверка
        event.refresh_from_db()
        assert event.status == OutboxEvent.StatusChoices.PROCESSED
        assert event.processed_at is not None
        assert event.attempts == 0

    def test_process_outbox_events_failure(self, mocker):
        # фикстура
        event = OutboxEvent.objects.create(
            event_type="test_event",
            event_data={"test": "data"}
        )
        mock_client = mocker.patch('core.event_log_client.EventLogClient.init')
        mock_client.return_value.__enter__.return_value.insert.side_effect = Exception("Test error")

        # выполнение и проверка
        with pytest.raises(Exception):
            process_outbox_events()

        event.refresh_from_db()
        assert event.status == OutboxEvent.StatusChoices.PENDING
        assert event.attempts == 1
        assert "Test error" in event.last_error 