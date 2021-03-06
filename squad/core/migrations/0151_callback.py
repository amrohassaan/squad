# Generated by Django 2.2.17 on 2021-01-06 10:36

from django.db import migrations, models
import django.db.models.deletion
import squad.core.callback
import squad.core.utils


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0150_add_new_notification_strategy'),
    ]

    operations = [
        migrations.CreateModel(
            name='Callback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(blank=True, default=None, max_length=1024, null=True)),
                ('method', models.CharField(default='post', max_length=10, validators=[squad.core.callback.callback_methods.validator])),
                ('event', models.CharField(max_length=64, validators=[squad.core.callback.callback_events.validator])),
                ('headers', models.TextField(blank=True, default=None, null=True, validators=[squad.core.utils.yaml_validator], verbose_name='HTTP headers (JSON-formatted) to be sent in this callback')),
                ('payload', models.TextField(blank=True, default=None, null=True, validators=[squad.core.utils.yaml_validator], verbose_name='Payload (JSON-formatted) to be sent in this callback')),
                ('payload_is_json', models.BooleanField(default=True)),
                ('is_sent', models.BooleanField(default=False)),
                ('record_response', models.BooleanField(default=False, verbose_name='Should this callback response be recorded?')),
                ('response_code', models.IntegerField(blank=True, default=None, null=True)),
                ('response_content', models.CharField(blank=True, default=None, max_length=1024, null=True)),
                ('object_reference_id', models.PositiveIntegerField()),
                ('object_reference_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'unique_together': {('object_reference_type', 'object_reference_id', 'url', 'event')},
            },
        ),
    ]
