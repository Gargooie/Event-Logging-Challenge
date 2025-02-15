from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='OutboxEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('event_type', models.CharField(max_length=255)),
                ('event_data', models.JSONField()),
                ('status', models.CharField(
                    choices=[('pending', 'Pending'), ('processed', 'Processed'), ('failed', 'Failed')],
                    default='pending',
                    max_length=20
                )),
                ('attempts', models.PositiveIntegerField(default=0)),
                ('last_error', models.TextField(blank=True, null=True)),
                ('processed_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'indexes': [models.Index(fields=['status', 'created_at'])],
            },
        ),
    ] 