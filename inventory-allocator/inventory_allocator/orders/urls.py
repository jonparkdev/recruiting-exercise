from django.urls import path, include
from orders import views
from rest_framework.routers import DefaultRouter


# register viewsets
router = DefaultRouter()
router.register(r'warehouses', views.WarehouseViewSet)
router.register(r'items', views.ItemsViewSet)
router.register(r'inventory', views.InventoryViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('stock', views.get_warehouse_inventory),
    #path('order', views.make_order)
]
