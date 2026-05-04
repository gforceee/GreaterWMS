from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lightstrip', '0002_active_bin_unique_constraint'),
    ]

    operations = [
        migrations.CreateModel(
            name='LightStripTagModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('light_sn', models.CharField(max_length=255, verbose_name='Light SN')),
                ('light_address', models.CharField(max_length=255, verbose_name='Light Address')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('extra_config', models.JSONField(default=dict, verbose_name='Extra Config')),
                ('openid', models.CharField(max_length=255, verbose_name='Openid')),
                ('is_delete', models.BooleanField(default=False, verbose_name='Delete Label')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Create Time')),
                ('update_time', models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name='Update Time')),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='lightstrip.lightstripdevicemodel', verbose_name='Device')),
            ],
            options={
                'verbose_name': 'Light Strip Tag',
                'verbose_name_plural': 'Light Strip Tag',
                'db_table': 'lightstrip_tag',
                'ordering': ['-id'],
            },
        ),
        migrations.AddField(
            model_name='binlightbindingmodel',
            name='light_sn',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Light SN'),
        ),
        migrations.AddConstraint(
            model_name='lightstriptagmodel',
            constraint=models.UniqueConstraint(condition=models.Q(('is_delete', False)), fields=('openid', 'light_sn'), name='uniq_active_lightstrip_tag_sn'),
        ),
        migrations.AddConstraint(
            model_name='lightstriptagmodel',
            constraint=models.UniqueConstraint(condition=models.Q(('is_delete', False)), fields=('openid', 'device', 'light_address'), name='uniq_active_lightstrip_tag_address'),
        ),
        migrations.AddConstraint(
            model_name='binlightbindingmodel',
            constraint=models.UniqueConstraint(condition=models.Q(('is_delete', False), models.Q(('light_sn', ''), _negated=True)), fields=('openid', 'light_sn'), name='uniq_active_lightstrip_binding_sn'),
        ),
        migrations.AddConstraint(
            model_name='binlightbindingmodel',
            constraint=models.UniqueConstraint(condition=models.Q(('is_delete', False)), fields=('openid', 'device', 'light_address'), name='uniq_active_lightstrip_binding_address'),
        ),
    ]
