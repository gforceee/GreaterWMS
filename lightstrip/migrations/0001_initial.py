# Generated manually for the lightstrip app.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LightStripDeviceModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_code', models.CharField(max_length=255, verbose_name='Device Code')),
                ('device_name', models.CharField(max_length=255, verbose_name='Device Name')),
                ('warehouse_name', models.CharField(blank=True, default='', max_length=255, verbose_name='Warehouse Name')),
                ('provider_type', models.CharField(default='tcp_socket', max_length=64, verbose_name='Provider Type')),
                ('endpoint', models.CharField(blank=True, default='', max_length=500, verbose_name='Endpoint')),
                ('auth_token', models.CharField(blank=True, default='', max_length=500, verbose_name='Auth Token')),
                ('status', models.CharField(default='offline', max_length=32, verbose_name='Status')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('extra_config', models.JSONField(default=dict, verbose_name='Extra Config')),
                ('openid', models.CharField(max_length=255, verbose_name='Openid')),
                ('is_delete', models.BooleanField(default=False, verbose_name='Delete Label')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Create Time')),
                ('update_time', models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name='Update Time')),
            ],
            options={
                'verbose_name': 'Light Strip Device',
                'verbose_name_plural': 'Light Strip Device',
                'db_table': 'lightstrip_device',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='LightStripTaskLogModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_type', models.CharField(max_length=64, verbose_name='Task Type')),
                ('source_type', models.CharField(blank=True, default='', max_length=64, verbose_name='Source Type')),
                ('source_code', models.CharField(blank=True, default='', max_length=255, verbose_name='Source Code')),
                ('bin_name', models.CharField(max_length=255, verbose_name='Bin Name')),
                ('device_code', models.CharField(max_length=255, verbose_name='Device Code')),
                ('light_address', models.CharField(max_length=255, verbose_name='Light Address')),
                ('command', models.CharField(max_length=32, verbose_name='Command')),
                ('command_status', models.CharField(default='pending', max_length=32, verbose_name='Command Status')),
                ('request_payload', models.JSONField(default=dict, verbose_name='Request Payload')),
                ('response_payload', models.JSONField(default=dict, verbose_name='Response Payload')),
                ('operator', models.CharField(blank=True, default='', max_length=255, verbose_name='Operator')),
                ('error_message', models.TextField(blank=True, default='', verbose_name='Error Message')),
                ('openid', models.CharField(max_length=255, verbose_name='Openid')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Create Time')),
                ('update_time', models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name='Update Time')),
            ],
            options={
                'verbose_name': 'Light Strip Task Log',
                'verbose_name_plural': 'Light Strip Task Log',
                'db_table': 'lightstrip_task_log',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='BinLightBindingModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bin_name', models.CharField(max_length=255, verbose_name='Bin Name')),
                ('light_address', models.CharField(max_length=255, verbose_name='Light Address')),
                ('color', models.CharField(default='green', max_length=32, verbose_name='Color')),
                ('default_command', models.CharField(default='on', max_length=32, verbose_name='Default Command')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('extra_config', models.JSONField(default=dict, verbose_name='Extra Config')),
                ('openid', models.CharField(max_length=255, verbose_name='Openid')),
                ('is_delete', models.BooleanField(default=False, verbose_name='Delete Label')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Create Time')),
                ('update_time', models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name='Update Time')),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bindings', to='lightstrip.lightstripdevicemodel', verbose_name='Device')),
            ],
            options={
                'verbose_name': 'Bin Light Binding',
                'verbose_name_plural': 'Bin Light Binding',
                'db_table': 'lightstrip_binding',
                'ordering': ['-id'],
            },
        ),
    ]
