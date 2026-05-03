from rest_framework import serializers

from utils import datasolve

from .models import BinLightBindingModel, LightStripDeviceModel, LightStripTaskLogModel


class LightStripDeviceGetSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = LightStripDeviceModel
        exclude = ['openid', 'is_delete']
        read_only_fields = ['id']


class LightStripDevicePostSerializer(serializers.ModelSerializer):
    openid = serializers.CharField(read_only=False, required=False, validators=[datasolve.openid_validate])
    device_code = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    device_name = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    warehouse_name = serializers.CharField(read_only=False, required=False, allow_blank=True, validators=[datasolve.data_validate])
    provider_type = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    endpoint = serializers.CharField(read_only=False, required=False, allow_blank=True)
    auth_token = serializers.CharField(read_only=False, required=False, allow_blank=True)
    status = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])

    class Meta:
        model = LightStripDeviceModel
        exclude = ['is_delete']
        read_only_fields = ['id', 'create_time', 'update_time']


class LightStripDeviceUpdateSerializer(serializers.ModelSerializer):
    device_code = serializers.CharField(read_only=True, required=False)
    device_name = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    warehouse_name = serializers.CharField(read_only=False, required=False, allow_blank=True, validators=[datasolve.data_validate])
    provider_type = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    status = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])

    class Meta:
        model = LightStripDeviceModel
        exclude = ['openid', 'is_delete']
        read_only_fields = ['id', 'create_time', 'update_time']


class LightStripDevicePartialUpdateSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    warehouse_name = serializers.CharField(read_only=False, required=False, allow_blank=True, validators=[datasolve.data_validate])
    provider_type = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    status = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])

    class Meta:
        model = LightStripDeviceModel
        exclude = ['openid', 'is_delete']
        read_only_fields = ['id', 'create_time', 'update_time']


class BinLightBindingGetSerializer(serializers.ModelSerializer):
    device_code = serializers.CharField(source='device.device_code', read_only=True)
    device_name = serializers.CharField(source='device.device_name', read_only=True)
    create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = BinLightBindingModel
        exclude = ['openid', 'is_delete']
        read_only_fields = ['id']


class BinLightBindingPostSerializer(serializers.ModelSerializer):
    openid = serializers.CharField(read_only=False, required=False, validators=[datasolve.openid_validate])
    bin_name = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    light_address = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    color = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    default_command = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])

    class Meta:
        model = BinLightBindingModel
        exclude = ['is_delete']
        read_only_fields = ['id', 'create_time', 'update_time']


class BinLightBindingUpdateSerializer(serializers.ModelSerializer):
    bin_name = serializers.CharField(read_only=True, required=False)
    light_address = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    color = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    default_command = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])

    class Meta:
        model = BinLightBindingModel
        exclude = ['openid', 'is_delete']
        read_only_fields = ['id', 'create_time', 'update_time']


class BinLightBindingPartialUpdateSerializer(serializers.ModelSerializer):
    light_address = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    color = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    default_command = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])

    class Meta:
        model = BinLightBindingModel
        exclude = ['openid', 'is_delete']
        read_only_fields = ['id', 'create_time', 'update_time']


class LightStripTaskLogGetSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = LightStripTaskLogModel
        exclude = ['openid']
        read_only_fields = ['id']


class LightStripTriggerSerializer(serializers.Serializer):
    bin_name = serializers.CharField(required=True, validators=[datasolve.data_validate])
    command = serializers.CharField(required=False, default='on', validators=[datasolve.data_validate])
    task_type = serializers.CharField(required=False, default='manual', validators=[datasolve.data_validate])
    source_type = serializers.CharField(required=False, default='manual', validators=[datasolve.data_validate])
    source_code = serializers.CharField(required=False, allow_blank=True, default='')
    operator = serializers.CharField(required=False, allow_blank=True, default='')
    extra_payload = serializers.JSONField(required=False)


class LightStripBatchTriggerSerializer(serializers.Serializer):
    dn_code = serializers.CharField(required=True, validators=[datasolve.data_validate])
    command = serializers.CharField(required=False, default='on', validators=[datasolve.data_validate])
    operator = serializers.CharField(required=False, allow_blank=True, default='')
    extra_payload = serializers.JSONField(required=False)


class PTLDisplaySerializer(serializers.Serializer):
    bin_name = serializers.CharField(required=True, validators=[datasolve.data_validate])
    lcd_num_val = serializers.IntegerField(required=True, min_value=0, max_value=9999)
    operator = serializers.CharField(required=False, allow_blank=True, default='')
    extra_payload = serializers.JSONField(required=False)


class PTLSkuSerializer(serializers.Serializer):
    bin_name = serializers.CharField(required=True, validators=[datasolve.data_validate])
    sku = serializers.CharField(required=True, max_length=6, validators=[datasolve.data_validate])
    operator = serializers.CharField(required=False, allow_blank=True, default='')
