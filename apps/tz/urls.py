from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, OrderViewSet, OrderProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-products', OrderProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('orders/<int:order_pk>/products/<int:order_product_pk>/', OrderProductViewSet.as_view({'get': 'get_order_product'})),
    path('order-products/statistics/', OrderProductViewSet.as_view({'get': 'statistics'})),
]
