from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, WarehouseViewSet, RegisterUserView,RecordsViewSet

router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'warehouses', WarehouseViewSet)
router.register(r'records', RecordsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('client/register/', RegisterUserView.as_view({'post': 'create'}), name='register_clients'),
]