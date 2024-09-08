from rest_framework import viewsets
from .models import Order, Product, OrderProduct
from .serializers import OrderSerializer, ProductSerializer, OrderProductSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .services import rental_statistics

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        order_data = request.data

        with transaction.atomic():
            try:
                # Создание заказа и продуктов с помощью сериализатора
                serializer = self.get_serializer(data=order_data)
                serializer.is_valid(raise_exception=True)
                order = serializer.save()  # Сохранение заказа вместе с продуктами
            except Exception as e:
                transaction.set_rollback(True)
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class OrderProductViewSet(viewsets.ModelViewSet):
    queryset = OrderProduct.objects.all()
    serializer_class = OrderProductSerializer

    # Кастомный метод для получения продукта в заказе
    def get_order_product(self, request, order_pk=None, order_product_pk=None):
        try:
            # Получаем продукт по id заказа и id продукта в заказе
            order_product = OrderProduct.objects.get(order_id=order_pk, id=order_product_pk)
        except OrderProduct.DoesNotExist:
            return Response({"detail": "OrderProduct not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = OrderProductSerializer(order_product)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Получаем статистику через сервис
        statistics_data, response_status = rental_statistics(start_date, end_date)
        return Response(statistics_data, status=response_status)

    