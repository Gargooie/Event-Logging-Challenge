# Добавим админку для OutboxEvent:
from django.contrib import admin
from core.models import OutboxEvent

@admin.register(OutboxEvent)
class OutboxEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'status', 'attempts', 'created_at', 'processed_at')
    list_filter = ('status', 'event_type')
    search_fields = ('event_type', 'event_data')
    readonly_fields = ('created_at', 'updated_at', 'processed_at') 