from django.urls import path, re_path

from . import views


urlpatterns = [
    path(r'device/', views.DeviceAPIViewSet.as_view({"get": "list", "post": "create"}), name="lightstrip_device"),
    re_path(r'^device/(?P<pk>\d+)/$', views.DeviceAPIViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name="lightstrip_device_detail"),
    path(r'binding/', views.BindingAPIViewSet.as_view({"get": "list", "post": "create"}), name="lightstrip_binding"),
    re_path(r'^binding/(?P<pk>\d+)/$', views.BindingAPIViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name="lightstrip_binding_detail"),
    path(r'task/', views.TaskLogAPIViewSet.as_view({"get": "list"}), name="lightstrip_task"),
    re_path(r'^task/(?P<pk>\d+)/$', views.TaskLogAPIViewSet.as_view({"get": "retrieve"}), name="lightstrip_task_detail"),
    path(r'trigger/', views.TriggerAPIViewSet.as_view({"post": "create"}), name="lightstrip_trigger"),
    path(r'trigger/picking/', views.PickingTriggerAPIViewSet.as_view({"post": "create"}), name="lightstrip_trigger_picking"),
    path(r'ptl/display/', views.PTLDisplayAPIViewSet.as_view({"post": "create"}), name="lightstrip_ptl_display"),
    path(r'ptl/sku/', views.PTLSkuAPIViewSet.as_view({"post": "create"}), name="lightstrip_ptl_sku"),
]
