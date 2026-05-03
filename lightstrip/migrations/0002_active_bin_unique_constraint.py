# Generated manually for the lightstrip app.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lightstrip', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='binlightbindingmodel',
            constraint=models.UniqueConstraint(
                fields=('openid', 'bin_name'),
                condition=models.Q(is_delete=False),
                name='uniq_active_lightstrip_bin'
            ),
        ),
    ]
