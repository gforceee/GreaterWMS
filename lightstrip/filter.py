from django_filters import FilterSet

from .models import BinLightBindingModel, LightStripDeviceModel, LightStripTagModel, LightStripTaskLogModel


class DeviceFilter(FilterSet):
    class Meta:
        model = LightStripDeviceModel
        fields = {
            "id": ['exact', 'gt', 'gte', 'lt', 'lte', 'in', 'range'],
            "device_code": ['exact', 'iexact', 'contains', 'icontains'],
            "device_name": ['exact', 'iexact', 'contains', 'icontains'],
            "warehouse_name": ['exact', 'iexact', 'contains', 'icontains'],
            "provider_type": ['exact', 'iexact'],
            "status": ['exact', 'iexact'],
            "is_active": ['exact'],
            "create_time": ['year', 'month', 'day', 'gt', 'gte', 'lt', 'lte', 'range'],
            "update_time": ['year', 'month', 'day', 'gt', 'gte', 'lt', 'lte', 'range']
        }


class BindingFilter(FilterSet):
    class Meta:
        model = BinLightBindingModel
        fields = {
            "id": ['exact', 'gt', 'gte', 'lt', 'lte', 'in', 'range'],
            "bin_name": ['exact', 'iexact', 'contains', 'icontains'],
            "light_address": ['exact', 'iexact', 'contains', 'icontains'],
            "color": ['exact', 'iexact'],
            "default_command": ['exact', 'iexact'],
            "is_active": ['exact'],
            "create_time": ['year', 'month', 'day', 'gt', 'gte', 'lt', 'lte', 'range'],
            "update_time": ['year', 'month', 'day', 'gt', 'gte', 'lt', 'lte', 'range']
        }


class TagFilter(FilterSet):
    class Meta:
        model = LightStripTagModel
        fields = {
            "id": ['exact', 'gt', 'gte', 'lt', 'lte', 'in', 'range'],
            "light_sn": ['exact', 'iexact', 'contains', 'icontains'],
            "light_address": ['exact', 'iexact', 'contains', 'icontains'],
            "is_active": ['exact'],
            "create_time": ['year', 'month', 'day', 'gt', 'gte', 'lt', 'lte', 'range'],
            "update_time": ['year', 'month', 'day', 'gt', 'gte', 'lt', 'lte', 'range']
        }


class TaskLogFilter(FilterSet):
    class Meta:
        model = LightStripTaskLogModel
        fields = {
            "id": ['exact', 'gt', 'gte', 'lt', 'lte', 'in', 'range'],
            "task_type": ['exact', 'iexact'],
            "source_type": ['exact', 'iexact'],
            "source_code": ['exact', 'iexact', 'contains', 'icontains'],
            "bin_name": ['exact', 'iexact', 'contains', 'icontains'],
            "device_code": ['exact', 'iexact', 'contains', 'icontains'],
            "command": ['exact', 'iexact'],
            "command_status": ['exact', 'iexact'],
            "operator": ['exact', 'iexact', 'contains', 'icontains'],
            "create_time": ['year', 'month', 'day', 'gt', 'gte', 'lt', 'lte', 'range'],
            "update_time": ['year', 'month', 'day', 'gt', 'gte', 'lt', 'lte', 'range']
        }
