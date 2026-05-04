from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import APIException
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from binset.models import ListModel as BinSetModel
from dn.models import PickingListModel
from utils.page import MyPageNumberPagination

from .filter import BindingFilter, DeviceFilter, TagFilter, TaskLogFilter
from .models import BinLightBindingModel, LightStripDeviceModel, LightStripTagModel, LightStripTaskLogModel
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
    LightStripTagGetSerializer,
    LightStripTagPartialUpdateSerializer,
    LightStripTagPostSerializer,
    LightStripTagUpdateSerializer,
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
        data = self._resolve_tag_payload(data)
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
        try:
            serializer.save()
        except IntegrityError:
            raise APIException({"detail": "This bin is already bound to a light"})
        return Response(serializer.data, status=200)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self._resolve_tag_payload(request.data.copy())
        self._validate_device_access(data)
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except IntegrityError:
            raise APIException({"detail": "This bin is already bound to a light"})
        return Response(serializer.data, status=200)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self._resolve_tag_payload(request.data.copy())
        self._validate_device_access(data)
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except IntegrityError:
            raise APIException({"detail": "This bin is already bound to a light"})
        return Response(serializer.data, status=200)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete = True
        instance.save(update_fields=['is_delete', 'update_time'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=200)

    def _validate_device_access(self, data):
        device_id = data.get('device')
        if device_id is None:
            return
        if not LightStripDeviceModel.objects.filter(
            openid=self.request.auth.openid,
            id=device_id,
            is_delete=False
        ).exists():
            raise APIException({"detail": "Device does not exist"})

    def _resolve_tag_payload(self, data):
        light_sn = data.get('light_sn')
        if not light_sn:
            return data
        tag = LightStripTagModel.objects.filter(
            openid=self.request.auth.openid,
            light_sn=light_sn,
            is_delete=False,
            is_active=True,
            device__is_delete=False,
            device__is_active=True
        ).select_related('device').first()
        if tag is None:
            raise APIException({"detail": "Light SN does not exist or is inactive"})
        device_id = data.get('device')
        if device_id and int(device_id) != tag.device_id:
            raise APIException({"detail": "Light SN does not belong to the selected device"})
        data['device'] = tag.device_id
        data['light_address'] = tag.light_address
        return data


class TagAPIViewSet(viewsets.ModelViewSet):
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['id', 'create_time', 'update_time']
    filter_class = TagFilter

    def get_queryset(self):
        if self.request.user:
            return LightStripTagModel.objects.filter(
                openid=self.request.auth.openid,
                is_delete=False
            ).select_related('device')
        return LightStripTagModel.objects.none()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'destroy']:
            return LightStripTagGetSerializer
        if self.action == 'create':
            return LightStripTagPostSerializer
        if self.action == 'update':
            return LightStripTagUpdateSerializer
        if self.action == 'partial_update':
            return LightStripTagPartialUpdateSerializer
        return self.http_method_not_allowed(request=self.request)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['openid'] = self.request.auth.openid
        self._validate_device_access(data)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except IntegrityError:
            raise APIException({"detail": "Light SN or address already exists"})
        return Response(serializer.data, status=200)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        self._validate_device_access(request.data)
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except IntegrityError:
            raise APIException({"detail": "Light SN or address already exists"})
        return Response(serializer.data, status=200)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        self._validate_device_access(request.data)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except IntegrityError:
            raise APIException({"detail": "Light SN or address already exists"})
        return Response(serializer.data, status=200)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete = True
        instance.save(update_fields=['is_delete', 'update_time'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=200)

    def _validate_device_access(self, data):
        device_id = data.get('device')
        if device_id is None:
            return
        if not LightStripDeviceModel.objects.filter(
            openid=self.request.auth.openid,
            id=device_id,
            is_delete=False
        ).exists():
            raise APIException({"detail": "Device does not exist"})


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
    request_payload = _build_request_payload(
        task_type=task_type,
        source_type=source_type,
        source_code=source_code,
        bin_name=bin_name,
        device_code='',
        light_address='',
        command=command,
        color='',
        extra_payload=extra_payload,
        device_config={},
        binding_config={},
    )
    binding = BinLightBindingModel.objects.filter(
        openid=openid,
        bin_name=bin_name,
        is_delete=False,
        is_active=True,
        device__is_delete=False,
        device__is_active=True
    ).select_related('device').first()
    if binding is None:
        _create_failed_task_log(
            openid=openid,
            task_type=task_type,
            source_type=source_type,
            source_code=source_code,
            bin_name=bin_name,
            device_code='',
            light_address='',
            command=command,
            request_payload=request_payload,
            operator=operator,
            message='No active light binding found for this bin'
        )
        raise APIException({"detail": "No active light binding found for this bin"})

    payload = _build_request_payload(
        task_type=task_type,
        source_type=source_type,
        source_code=source_code,
        bin_name=binding.bin_name,
        device_code=binding.device.device_code,
        light_address=binding.light_address,
        command=command,
        color=binding.color,
        extra_payload=extra_payload,
        device_config=binding.device.extra_config,
        binding_config=binding.extra_config,
    )
    provider = LightStripProvider(binding.device)
    try:
        provider_response = provider.dispatch(payload)
    except Exception as exc:
        provider_response = _build_failed_provider_response(payload, exc)
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
    task_logs = []
    if not bindings:
        for bin_name in unique_bin_names:
            task_logs.append(
                _create_failed_task_log(
                    openid=openid,
                    task_type=task_type,
                    source_type=source_type,
                    source_code=source_code,
                    bin_name=bin_name,
                    device_code='',
                    light_address='',
                    command=command,
                    request_payload=_build_request_payload(
                        task_type=task_type,
                        source_type=source_type,
                        source_code=source_code,
                        bin_name=bin_name,
                        device_code='',
                        light_address='',
                        command=command,
                        color='',
                        extra_payload=extra_payload,
                        device_config={},
                        binding_config={},
                    ),
                    operator=operator,
                    message='No active light binding found for this bin'
                )
            )
        return task_logs

    binding_map = {binding.bin_name: binding for binding in bindings}
    missing_bins = [bin_name for bin_name in unique_bin_names if bin_name not in binding_map]
    if missing_bins:
        for bin_name in missing_bins:
            task_logs.append(
                _create_failed_task_log(
                    openid=openid,
                    task_type=task_type,
                    source_type=source_type,
                    source_code=source_code,
                    bin_name=bin_name,
                    device_code='',
                    light_address='',
                    command=command,
                    request_payload=_build_request_payload(
                        task_type=task_type,
                        source_type=source_type,
                        source_code=source_code,
                        bin_name=bin_name,
                        device_code='',
                        light_address='',
                        command=command,
                        color='',
                        extra_payload=extra_payload,
                        device_config={},
                        binding_config={},
                    ),
                    operator=operator,
                    message='No active light binding found for this bin'
                )
            )

    device_groups = {}
    for bin_name in unique_bin_names:
        binding = binding_map[bin_name]
        device_groups.setdefault(binding.device_id, {"device": binding.device, "bindings": []})
        device_groups[binding.device_id]["bindings"].append(binding)

    for group in device_groups.values():
        provider_payload = []
        for binding in group["bindings"]:
            provider_payload.append(
                _build_request_payload(
                    task_type=task_type,
                    source_type=source_type,
                    source_code=source_code,
                    bin_name=binding.bin_name,
                    device_code=binding.device.device_code,
                    light_address=binding.light_address,
                    command=command,
                    color=binding.color,
                    extra_payload=extra_payload,
                    device_config=binding.device.extra_config,
                    binding_config=binding.extra_config,
                )
            )

        provider = LightStripProvider(group["device"])
        try:
            provider_response = provider.dispatch_batch(provider_payload)
        except Exception as exc:
            provider_response = _build_failed_provider_response(provider_payload, exc)
        for binding in group["bindings"]:
            request_payload = _build_request_payload(
                task_type=task_type,
                source_type=source_type,
                source_code=source_code,
                bin_name=binding.bin_name,
                device_code=binding.device.device_code,
                light_address=binding.light_address,
                command=command,
                color=binding.color,
                extra_payload=extra_payload,
                device_config=binding.device.extra_config,
                binding_config=binding.extra_config,
            )
            item_response = _extract_binding_response(provider_response, binding)
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
                    command_status=item_response.get('status', provider_response.get('status', 'pending')),
                    request_payload=request_payload,
                    response_payload=item_response,
                    operator=operator,
                    error_message='' if item_response.get('status') != 'failed' else item_response.get('message', provider_response.get('message', ''))
                )
            )
    return task_logs


def _build_request_payload(task_type, source_type, source_code, bin_name, device_code, light_address, command, color, extra_payload, device_config, binding_config):
    return {
        "task_type": task_type,
        "source_type": source_type,
        "source_code": source_code,
        "bin_name": bin_name,
        "device_code": device_code,
        "light_address": light_address,
        "command": str(command or 'on').lower(),
        "color": color,
        "extra_payload": extra_payload or {},
        "device_config": device_config or {},
        "binding_config": binding_config or {},
    }


def _build_failed_provider_response(payload, exc):
    return {
        'status': 'failed',
        'message': str(exc),
        'transport': 'tcp_socket',
        'payload': payload,
        'command_results': []
    }


def _create_failed_task_log(openid, task_type, source_type, source_code, bin_name, device_code, light_address, command, request_payload, operator, message):
    return LightStripTaskLogModel.objects.create(
        openid=openid,
        task_type=task_type,
        source_type=source_type,
        source_code=source_code,
        bin_name=bin_name,
        device_code=device_code,
        light_address=light_address,
        command=str(command or 'on').lower(),
        command_status='failed',
        request_payload=request_payload,
        response_payload={
            'status': 'failed',
            'message': message
        },
        operator=operator,
        error_message=message
    )


def _extract_binding_response(provider_response, binding):
    for item in provider_response.get('command_results') or []:
        payload = item.get('payload') or {}
        if payload.get('bin_name') == binding.bin_name and payload.get('light_address') == binding.light_address:
            return {
                'status': item.get('status', provider_response.get('status', 'pending')),
                'message': provider_response.get('message', ''),
                'transport': provider_response.get('transport', ''),
                'host': provider_response.get('host', ''),
                'port': provider_response.get('port', ''),
                'command_result': item,
            }
    return provider_response
