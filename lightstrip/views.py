from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import APIException
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from binset.models import ListModel as BinSetModel
from dn.models import PickingListModel
from utils.page import MyPageNumberPagination

from .filter import BindingFilter, DeviceFilter, TaskLogFilter
from .models import BinLightBindingModel, LightStripDeviceModel, LightStripTaskLogModel
from .serializers import (
    BinLightBindingGetSerializer,
    BinLightBindingPartialUpdateSerializer,
    BinLightBindingPostSerializer,
    BinLightBindingUpdateSerializer,
    LightStripBatchTriggerSerializer,
    LightStripDeviceGetSerializer,
    LightStripDevicePartialUpdateSerializer,
    LightStripDevicePostSerializer,
    LightStripDeviceUpdateSerializer,
    LightStripTaskLogGetSerializer,
    LightStripTriggerSerializer,
    PTLDisplaySerializer,
    PTLSkuSerializer,
)
from .services import LightStripProvider


class DeviceAPIViewSet(viewsets.ModelViewSet):
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['id', 'create_time', 'update_time']
    filter_class = DeviceFilter

    def get_queryset(self):
        if self.request.user:
            return LightStripDeviceModel.objects.filter(openid=self.request.auth.openid, is_delete=False)
        return LightStripDeviceModel.objects.none()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'destroy']:
            return LightStripDeviceGetSerializer
        if self.action == 'create':
            return LightStripDevicePostSerializer
        if self.action == 'update':
            return LightStripDeviceUpdateSerializer
        if self.action == 'partial_update':
            return LightStripDevicePartialUpdateSerializer
        return self.http_method_not_allowed(request=self.request)

    def create(self, request, *args, **kwargs):
        data = self.request.data.copy()
        data['openid'] = self.request.auth.openid
        if LightStripDeviceModel.objects.filter(
            openid=self.request.auth.openid,
            device_code=data.get('device_code'),
            is_delete=False
        ).exists():
            raise APIException({"detail": "Device code already exists"})
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete = True
        instance.save(update_fields=['is_delete', 'update_time'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=200)


class BindingAPIViewSet(viewsets.ModelViewSet):
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['id', 'create_time', 'update_time']
    filter_class = BindingFilter

    def get_queryset(self):
        if self.request.user:
            return BinLightBindingModel.objects.filter(
                openid=self.request.auth.openid,
                is_delete=False
            ).select_related('device')
        return BinLightBindingModel.objects.none()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'destroy']:
            return BinLightBindingGetSerializer
        if self.action == 'create':
            return BinLightBindingPostSerializer
        if self.action == 'update':
            return BinLightBindingUpdateSerializer
        if self.action == 'partial_update':
            return BinLightBindingPartialUpdateSerializer
        return self.http_method_not_allowed(request=self.request)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['openid'] = self.request.auth.openid
        bin_name = data.get('bin_name')
        device_id = data.get('device')
        if not BinSetModel.objects.filter(openid=self.request.auth.openid, bin_name=bin_name, is_delete=False).exists():
            raise APIException({"detail": "Bin does not exist"})
        if not LightStripDeviceModel.objects.filter(openid=self.request.auth.openid, id=device_id, is_delete=False).exists():
            raise APIException({"detail": "Device does not exist"})
        if BinLightBindingModel.objects.filter(openid=self.request.auth.openid, bin_name=bin_name, is_delete=False).exists():
            raise APIException({"detail": "This bin is already bound to a light"})
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete = True
        instance.save(update_fields=['is_delete', 'update_time'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=200)


class TaskLogAPIViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['id', 'create_time', 'update_time']
    filter_class = TaskLogFilter
    serializer_class = LightStripTaskLogGetSerializer

    def get_queryset(self):
        if self.request.user:
            return LightStripTaskLogModel.objects.filter(openid=self.request.auth.openid)
        return LightStripTaskLogModel.objects.none()


class TriggerAPIViewSet(viewsets.ViewSet):
    def create(self, request, *args, **kwargs):
        serializer = LightStripTriggerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        task_log = dispatch_light_command(
            openid=request.auth.openid,
            bin_name=data['bin_name'],
            command=data.get('command', 'on'),
            task_type=data.get('task_type', 'manual'),
            source_type=data.get('source_type', 'manual'),
            source_code=data.get('source_code', ''),
            operator=data.get('operator', ''),
            extra_payload=data.get('extra_payload', {})
        )
        return Response(LightStripTaskLogGetSerializer(task_log).data, status=200)


class PickingTriggerAPIViewSet(viewsets.ViewSet):
    def create(self, request, *args, **kwargs):
        serializer = LightStripBatchTriggerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        picking_qs = PickingListModel.objects.filter(
            openid=request.auth.openid,
            dn_code=data['dn_code'],
            picking_status=0
        ).order_by('bin_name', 'id')
        if not picking_qs.exists():
            raise APIException({"detail": "No pending picking bins found for this DN"})

        task_logs = dispatch_batch_light_command(
            openid=request.auth.openid,
            bin_names=list(picking_qs.values_list('bin_name', flat=True).distinct()),
            command=data.get('command', 'on'),
            task_type='picking',
            source_type='dn',
            source_code=data['dn_code'],
            operator=data.get('operator', ''),
            extra_payload=data.get('extra_payload', {})
        )
        return Response(LightStripTaskLogGetSerializer(task_logs, many=True).data, status=200)


class PTLDisplayAPIViewSet(viewsets.ViewSet):
    def create(self, request, *args, **kwargs):
        serializer = PTLDisplaySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        task_log = dispatch_light_command(
            openid=request.auth.openid,
            bin_name=data['bin_name'],
            command='display',
            task_type='ptl_display',
            source_type='manual',
            source_code='',
            operator=data.get('operator', ''),
            extra_payload={
                **(data.get('extra_payload') or {}),
                'lcd_num_val': data['lcd_num_val']
            }
        )
        return Response(LightStripTaskLogGetSerializer(task_log).data, status=200)


class PTLSkuAPIViewSet(viewsets.ViewSet):
    def create(self, request, *args, **kwargs):
        serializer = PTLSkuSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        task_log = dispatch_light_command(
            openid=request.auth.openid,
            bin_name=data['bin_name'],
            command='set_sku',
            task_type='ptl_sku',
            source_type='manual',
            source_code='',
            operator=data.get('operator', ''),
            extra_payload={
                'sku': data['sku']
            }
        )
        return Response(LightStripTaskLogGetSerializer(task_log).data, status=200)


def dispatch_light_command(openid, bin_name, command, task_type, source_type, source_code, operator, extra_payload):
    binding = BinLightBindingModel.objects.filter(
        openid=openid,
        bin_name=bin_name,
        is_delete=False,
        is_active=True,
        device__is_delete=False,
        device__is_active=True
    ).select_related('device').first()
    if binding is None:
        raise APIException({"detail": "No active light binding found for this bin"})

    payload = {
        "task_type": task_type,
        "source_type": source_type,
        "source_code": source_code,
        "bin_name": binding.bin_name,
        "device_code": binding.device.device_code,
        "light_address": binding.light_address,
        "command": command,
        "color": binding.color,
        "extra_payload": extra_payload or {},
        "device_config": binding.device.extra_config,
        "binding_config": binding.extra_config,
    }
    provider = LightStripProvider(binding.device)
    provider_response = provider.dispatch(payload)
    task_log = LightStripTaskLogModel.objects.create(
        openid=openid,
        task_type=task_type,
        source_type=source_type,
        source_code=source_code,
        bin_name=binding.bin_name,
        device_code=binding.device.device_code,
        light_address=binding.light_address,
        command=command,
        command_status=provider_response.get('status', 'pending'),
        request_payload=payload,
        response_payload=provider_response,
        operator=operator,
        error_message='' if provider_response.get('status') != 'failed' else provider_response.get('message', '')
    )
    return task_log


def safe_dispatch_light_command(openid, bin_name, command, task_type, source_type, source_code, operator, extra_payload):
    try:
        return dispatch_light_command(
            openid=openid,
            bin_name=bin_name,
            command=command,
            task_type=task_type,
            source_type=source_type,
            source_code=source_code,
            operator=operator,
            extra_payload=extra_payload,
        )
    except Exception as exc:
        return {
            "status": "failed",
            "bin_name": bin_name,
            "message": str(exc)
        }


def dispatch_batch_light_command(openid, bin_names, command, task_type, source_type, source_code, operator, extra_payload):
    unique_bin_names = []
    seen = set()
    for bin_name in bin_names:
        if bin_name not in seen:
            seen.add(bin_name)
            unique_bin_names.append(bin_name)

    bindings = list(
        BinLightBindingModel.objects.filter(
            openid=openid,
            bin_name__in=unique_bin_names,
            is_delete=False,
            is_active=True,
            device__is_delete=False,
            device__is_active=True
        ).select_related('device')
    )
    if not bindings:
        raise APIException({"detail": "No active light bindings found for the requested bins"})

    binding_map = {binding.bin_name: binding for binding in bindings}
    missing_bins = [bin_name for bin_name in unique_bin_names if bin_name not in binding_map]
    if missing_bins:
        raise APIException({"detail": "Some bins are not bound to active lights", "bins": missing_bins})

    device_groups = {}
    for bin_name in unique_bin_names:
        binding = binding_map[bin_name]
        device_groups.setdefault(binding.device_id, {"device": binding.device, "bindings": []})
        device_groups[binding.device_id]["bindings"].append(binding)

    task_logs = []
    for group in device_groups.values():
        provider_payload = []
        for binding in group["bindings"]:
            provider_payload.append({
                "task_type": task_type,
                "source_type": source_type,
                "source_code": source_code,
                "bin_name": binding.bin_name,
                "device_code": binding.device.device_code,
                "light_address": binding.light_address,
                "command": command,
                "color": binding.color,
                "extra_payload": extra_payload or {},
                "device_config": binding.device.extra_config,
                "binding_config": binding.extra_config,
            })

        provider = LightStripProvider(group["device"])
        provider_response = provider.dispatch_batch(provider_payload)
        for binding in group["bindings"]:
            task_logs.append(
                LightStripTaskLogModel.objects.create(
                    openid=openid,
                    task_type=task_type,
                    source_type=source_type,
                    source_code=source_code,
                    bin_name=binding.bin_name,
                    device_code=binding.device.device_code,
                    light_address=binding.light_address,
                    command=command,
                    command_status=provider_response.get('status', 'pending'),
                    request_payload={
                        "task_type": task_type,
                        "source_type": source_type,
                        "source_code": source_code,
                        "bin_name": binding.bin_name,
                        "device_code": binding.device.device_code,
                        "light_address": binding.light_address,
                        "command": command,
                        "color": binding.color,
                        "extra_payload": extra_payload or {},
                        "device_config": binding.device.extra_config,
                        "binding_config": binding.extra_config,
                    },
                    response_payload=provider_response,
                    operator=operator,
                    error_message='' if provider_response.get('status') != 'failed' else provider_response.get('message', '')
                )
            )
    return task_logs
