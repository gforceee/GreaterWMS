from django.db import models


class LightStripDeviceModel(models.Model):
    device_code = models.CharField(max_length=255, verbose_name="Device Code")
    device_name = models.CharField(max_length=255, verbose_name="Device Name")
    warehouse_name = models.CharField(max_length=255, blank=True, default='', verbose_name="Warehouse Name")
    provider_type = models.CharField(max_length=64, default='tcp_socket', verbose_name="Provider Type")
    endpoint = models.CharField(max_length=500, blank=True, default='', verbose_name="Endpoint")
    auth_token = models.CharField(max_length=500, blank=True, default='', verbose_name="Auth Token")
    status = models.CharField(max_length=32, default='offline', verbose_name="Status")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    extra_config = models.JSONField(default=dict, verbose_name="Extra Config")
    openid = models.CharField(max_length=255, verbose_name="Openid")
    is_delete = models.BooleanField(default=False, verbose_name='Delete Label')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="Create Time")
    update_time = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name="Update Time")

    class Meta:
        db_table = 'lightstrip_device'
        verbose_name = 'Light Strip Device'
        verbose_name_plural = "Light Strip Device"
        ordering = ['-id']


class LightStripTagModel(models.Model):
    device = models.ForeignKey(
        LightStripDeviceModel,
        on_delete=models.CASCADE,
        related_name='tags',
        verbose_name="Device"
    )
    light_sn = models.CharField(max_length=255, verbose_name="Light SN")
    light_address = models.CharField(max_length=255, verbose_name="Light Address")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    extra_config = models.JSONField(default=dict, verbose_name="Extra Config")
    openid = models.CharField(max_length=255, verbose_name="Openid")
    is_delete = models.BooleanField(default=False, verbose_name='Delete Label')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="Create Time")
    update_time = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name="Update Time")

    class Meta:
        db_table = 'lightstrip_tag'
        verbose_name = 'Light Strip Tag'
        verbose_name_plural = "Light Strip Tag"
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['openid', 'light_sn'],
                condition=models.Q(is_delete=False),
                name='uniq_active_lightstrip_tag_sn'
            ),
            models.UniqueConstraint(
                fields=['openid', 'device', 'light_address'],
                condition=models.Q(is_delete=False),
                name='uniq_active_lightstrip_tag_address'
            )
        ]


class BinLightBindingModel(models.Model):
    bin_name = models.CharField(max_length=255, verbose_name="Bin Name")
    device = models.ForeignKey(
        LightStripDeviceModel,
        on_delete=models.CASCADE,
        related_name='bindings',
        verbose_name="Device"
    )
    light_sn = models.CharField(max_length=255, blank=True, default='', verbose_name="Light SN")
    light_address = models.CharField(max_length=255, verbose_name="Light Address")
    color = models.CharField(max_length=32, default='green', verbose_name="Color")
    default_command = models.CharField(max_length=32, default='on', verbose_name="Default Command")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    extra_config = models.JSONField(default=dict, verbose_name="Extra Config")
    openid = models.CharField(max_length=255, verbose_name="Openid")
    is_delete = models.BooleanField(default=False, verbose_name='Delete Label')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="Create Time")
    update_time = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name="Update Time")

    class Meta:
        db_table = 'lightstrip_binding'
        verbose_name = 'Bin Light Binding'
        verbose_name_plural = "Bin Light Binding"
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['openid', 'bin_name'],
                condition=models.Q(is_delete=False),
                name='uniq_active_lightstrip_bin'
            ),
            models.UniqueConstraint(
                fields=['openid', 'light_sn'],
                condition=models.Q(is_delete=False) & ~models.Q(light_sn=''),
                name='uniq_active_lightstrip_binding_sn'
            ),
            models.UniqueConstraint(
                fields=['openid', 'device', 'light_address'],
                condition=models.Q(is_delete=False),
                name='uniq_active_lightstrip_binding_address'
            )
        ]


class LightStripTaskLogModel(models.Model):
    task_type = models.CharField(max_length=64, verbose_name="Task Type")
    source_type = models.CharField(max_length=64, blank=True, default='', verbose_name="Source Type")
    source_code = models.CharField(max_length=255, blank=True, default='', verbose_name="Source Code")
    bin_name = models.CharField(max_length=255, verbose_name="Bin Name")
    device_code = models.CharField(max_length=255, verbose_name="Device Code")
    light_address = models.CharField(max_length=255, verbose_name="Light Address")
    command = models.CharField(max_length=32, verbose_name="Command")
    command_status = models.CharField(max_length=32, default='pending', verbose_name="Command Status")
    request_payload = models.JSONField(default=dict, verbose_name="Request Payload")
    response_payload = models.JSONField(default=dict, verbose_name="Response Payload")
    operator = models.CharField(max_length=255, blank=True, default='', verbose_name="Operator")
    error_message = models.TextField(blank=True, default='', verbose_name="Error Message")
    openid = models.CharField(max_length=255, verbose_name="Openid")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="Create Time")
    update_time = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name="Update Time")

    class Meta:
        db_table = 'lightstrip_task_log'
        verbose_name = 'Light Strip Task Log'
        verbose_name_plural = "Light Strip Task Log"
        ordering = ['-id']
