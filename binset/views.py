from rest_framework import viewsets
from .models import ListModel
from . import serializers
from .page import MyPageNumberPagination
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from .filter import Filter
from rest_framework.exceptions import APIException
from django.db import IntegrityError, transaction
from django.db.models import Q
from binsize.models import ListModel as binsize
from scanner.models import ListModel as scanner
from binproperty.models import ListModel as binproperty
from .serializers import FileRenderSerializer
from django.http import StreamingHttpResponse
from .files import FileRenderCN, FileRenderEN
from rest_framework.settings import api_settings
from utils.md5 import Md5
from .serializers import ScannerBinsetTagGetSerializer
from lightstrip.models import BinLightBindingModel, LightStripTagModel

class ScannerBinsetTagView(viewsets.ModelViewSet):
    """
        retrieve:
            Response a data list（get）

            http://127.0.0.1:8008/binset/scannerbintag/3d89ad23d185d5f206d860745c5c4121/
    """
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = Filter
    lookup_field = 'bar_code'
    def get_project(self):
        try:
            bar_code = self.kwargs['bar_code']
            return bar_code
        except:
            return None

    def get_queryset(self):
        bar_code = self.get_project()
        if self.request.user:
            if bar_code is None:
                return ListModel.objects.filter(openid=self.request.auth.openid, is_delete=False)
            else:
                return ListModel.objects.filter(openid=self.request.auth.openid, bar_code=bar_code, is_delete=False)
        else:
            return ListModel.objects.none()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'destroy']:
            return serializers.ScannerBinsetTagGetSerializer
        else:
            return self.http_method_not_allowed(request=self.request)




class APIViewSet(viewsets.ModelViewSet):
    """
        retrieve:
            Response a data list（get）

        list:
            Response a data list（all）

        create:
            Create a data line（post）

        delete:
            Delete a data line（delete)

        partial_update:
            Partial_update a data（patch：partial_update）

        update:
            Update a data（put：update）
    """
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = Filter

    def get_project(self):
        try:
            id = self.kwargs.get('pk')
            return id
        except:
            return None

    def get_queryset(self):
        id = self.get_project()
        if self.request.user:
            if id is None:
                return ListModel.objects.filter(openid=self.request.auth.openid, is_delete=False)
            else:
                return ListModel.objects.filter(openid=self.request.auth.openid, id=id, is_delete=False)
        else:
            return ListModel.objects.none()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'destroy']:
            return serializers.BinsetGetSerializer
        elif self.action in ['create']:
            return serializers.BinsetPostSerializer
        elif self.action in ['update']:
            return serializers.BinsetUpdateSerializer
        elif self.action in ['partial_update']:
            return serializers.BinsetPartialUpdateSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def create(self, request, *args, **kwargs):
        data = self.request.data.copy()
        data['openid'] = self.request.auth.openid
        light_sn = self._pop_light_sn(data)
        if ListModel.objects.filter(openid=data['openid'], bin_name=data['bin_name'], is_delete=False).exists():
            raise APIException({"detail": "Data exists"})
        else:
            if binsize.objects.filter(openid=data['openid'], bin_size=data['bin_size'], is_delete=False).exists():
                if binproperty.objects.filter(Q(openid=data['openid'], bin_property=data['bin_property'], is_delete=False) |
                                              Q(openid='init_data', bin_property=data['bin_property'], is_delete=False)).exists():
                    with transaction.atomic():
                        data['bar_code'] = Md5.md5(data['bin_name'])
                        serializer = self.get_serializer(data=data)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        scanner.objects.create(openid=self.request.auth.openid, mode="BINSET", code=data['bin_name'],
                                               bar_code=data['bar_code'])
                        self._bind_lightstrip_by_sn(
                            openid=self.request.auth.openid,
                            bin_name=data['bin_name'],
                            light_sn=light_sn,
                            replace_existing=False
                        )
                    headers = self.get_success_headers(serializer.data)
                    return Response(serializer.data, status=200, headers=headers)
                else:
                    raise APIException({"detail": "Bin property does not exists or it has been changed"})
            else:
                raise APIException({"detail": "Bin size does not exists or it has been changed"})

    def update(self, request, pk):
        qs = self.get_object()
        if qs.openid != self.request.auth.openid:
            raise APIException({"detail": "Cannot update data which not yours"})
        else:
            data = self.request.data.copy()
            light_sn = self._pop_light_sn(data)
            if binsize.objects.filter(openid=self.request.auth.openid, bin_size=data['bin_size'], is_delete=False).exists():
                if binproperty.objects.filter(Q(openid=self.request.auth.openid, bin_property=data['bin_property'], is_delete=False) |
                                              Q(openid='init_data', bin_property=data['bin_property'], is_delete=False)).exists():
                    with transaction.atomic():
                        serializer = self.get_serializer(qs, data=data)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        self._bind_lightstrip_by_sn(
                            openid=self.request.auth.openid,
                            bin_name=qs.bin_name,
                            light_sn=light_sn,
                            replace_existing=True
                        )
                    headers = self.get_success_headers(serializer.data)
                    return Response(serializer.data, status=200, headers=headers)
                else:
                    raise APIException({"detail": "Bin property does not exists or it has been changed"})
            else:
                raise APIException({"detail": "Bin size does not exists or it has been changed"})

    def partial_update(self, request, pk):
        qs = self.get_object()
        if qs.openid != self.request.auth.openid:
            raise APIException({"detail": "Cannot partial_update data which not yours"})
        else:
            data = self.request.data.copy()
            light_sn = self._pop_light_sn(data)
            if binsize.objects.filter(openid=self.request.auth.openid, bin_size=data['bin_size'], is_delete=False).exists():
                if binproperty.objects.filter(Q(openid=self.request.auth.openid, bin_property=data['bin_property'], is_delete=False) |
                                              Q(openid='init_data', bin_property=data['bin_property'], is_delete=False)).exists():
                    with transaction.atomic():
                        serializer = self.get_serializer(qs, data=data, partial=True)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        self._bind_lightstrip_by_sn(
                            openid=self.request.auth.openid,
                            bin_name=qs.bin_name,
                            light_sn=light_sn,
                            replace_existing=True
                        )
                    headers = self.get_success_headers(serializer.data)
                    return Response(serializer.data, status=200, headers=headers)
                else:
                    raise APIException({"detail": "Bin property does not exists or it has been changed"})
            else:
                raise APIException({"detail": "Bin size does not exists or it has been changed"})

    def destroy(self, request, pk):
        qs = self.get_object()
        if qs.openid != self.request.auth.openid:
            raise APIException({"detail": "Cannot delete data which not yours"})
        else:
            qs.is_delete = True
            qs.save()
            serializer = self.get_serializer(qs, many=False)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=200, headers=headers)

    def _pop_light_sn(self, data):
        light_sn = data.pop('light_sn', '')
        if isinstance(light_sn, list):
            light_sn = light_sn[0] if light_sn else ''
        return str(light_sn or '').strip()

    def _bind_lightstrip_by_sn(self, openid, bin_name, light_sn, replace_existing):
        if not light_sn:
            return
        tag = LightStripTagModel.objects.filter(
            openid=openid,
            light_sn=light_sn,
            is_delete=False,
            is_active=True,
            device__is_delete=False,
            device__is_active=True
        ).select_related('device').first()
        if tag is None:
            raise APIException({"detail": "Light SN does not exist or is inactive"})
        binding = BinLightBindingModel.objects.filter(
            openid=openid,
            bin_name=bin_name,
            is_delete=False
        ).first()
        try:
            if binding:
                if not replace_existing:
                    raise APIException({"detail": "This bin is already bound to a light"})
                binding.device = tag.device
                binding.light_sn = tag.light_sn
                binding.light_address = tag.light_address
                binding.is_active = True
                binding.save(update_fields=['device', 'light_sn', 'light_address', 'is_active', 'update_time'])
            else:
                BinLightBindingModel.objects.create(
                    openid=openid,
                    bin_name=bin_name,
                    device=tag.device,
                    light_sn=tag.light_sn,
                    light_address=tag.light_address,
                    color=tag.extra_config.get('color', 'green') if isinstance(tag.extra_config, dict) else 'green'
                )
        except IntegrityError:
            raise APIException({"detail": "This light SN or address is already bound to another bin"})

class FileDownloadView(viewsets.ModelViewSet):
    renderer_classes = (FileRenderCN, ) + tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = Filter

    def get_project(self):
        try:
            id = self.kwargs.get('pk')
            return id
        except:
            return None

    def get_queryset(self):
        id = self.get_project()
        if self.request.user:
            if id is None:
                return ListModel.objects.filter(openid=self.request.auth.openid, is_delete=False)
            else:
                return ListModel.objects.filter(openid=self.request.auth.openid, id=id, is_delete=False)
        else:
            return ListModel.objects.none()

    def get_serializer_class(self):
        if self.action in ['list']:
            return serializers.FileRenderSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def get_lang(self, data):
        lang = self.request.META.get('HTTP_LANGUAGE')
        if lang:
            if lang == 'zh-hans':
                return FileRenderCN().render(data)
            else:
                return FileRenderEN().render(data)
        else:
            return FileRenderEN().render(data)

    def list(self, request, *args, **kwargs):
        from datetime import datetime
        dt = datetime.now()
        data = (
            FileRenderSerializer(instance).data
            for instance in self.filter_queryset(self.get_queryset())
        )
        renderer = self.get_lang(data)
        response = StreamingHttpResponse(
            renderer,
            content_type="text/csv"
        )
        response['Content-Disposition'] = "attachment; filename='binset_{}.csv'".format(str(dt.strftime('%Y%m%d%H%M%S%f')))
        return response
